# infra: one librarian host on AWS

Terraform for a single host that runs the Compose stack from `docs/ops/deploy.md`. Written 2026-11-17.
**Nothing here has been applied or planned against AWS.** It passes `fmt -check` and `validate` under Terraform 1.10.5 (see "Not verified").

The files are plain HCL and work with both Terraform and OpenTofu (`tofu` in place of `terraform` in every command
below). Both need version 1.10 or later, the first that locks S3 state with a lock object instead of DynamoDB.

## What it creates

| Resource | Notes |
|---|---|
| `aws_instance.host` | Ubuntu 24.04 LTS (Canonical's public SSM image parameter), IMDSv2 required, `user_data.sh` |
| root volume | encrypted gp3, `volume_size_gb` GiB, deleted with the instance |
| `aws_security_group.host` + 3 rules | in: TCP 80 and 443 from anywhere; out: all. **No port 22.** |
| `aws_eip.host` | the address DNS points at |
| `aws_iam_role.host`, `aws_iam_instance_profile.host`, one policy attachment | AWS-managed `AmazonSSMManagedInstanceCore` only |
| `aws_route53_record.host` | only if both `domain` and `route53_zone_id` are set |

It uses the account's default VPC and one of its default subnets. `bootstrap/` creates the state bucket (versioned,
encrypted, public access blocked, TLS-only policy).

`user_data.sh` installs Docker Engine and Compose v2 from Docker's apt repository, installs `git` and `rsync`, and creates
`/srv/librarian`. It does not clone the repository, pull an image or start the stack, and it contains no secret. No secret
belongs in Terraform variables or state: application secrets stay in `.env` or `_FILE` secrets on the host.

## Instance size and architecture (chosen, not measured)

Defaults: `architecture = "x86_64"`, `instance_type = "t3.large"` (2 vCPU, 8 GiB), 40 GiB volume.

- **Architecture.** `.github/workflows/ci.yml` builds the image with `docker/build-push-action` and no `platforms:`
  setting, on `ubuntu-latest`, so the image on GHCR is `linux/amd64` only. An ARM host (`t4g`, `m7g`) cannot run it
  until CI builds a multi-platform image. The variable allows `arm64` for that day; the Dockerfile's torch pin
  (`docker/requirements-torch-cpu.txt`) already carries an aarch64 hash.
- **Memory is what decides.** The image carries CPU torch and sentence-transformers with the MiniLM model loaded in
  each API process, and compose starts 2 API workers by default (`LIBRARIAN_API_WORKERS`), plus Postgres 17, Caddy, a
  one-shot indexer that loads the model again, and, with the `observability` profile, Prometheus and Grafana. A torch
  process with this model plausibly takes 1 to 1.5 GiB; two of them plus the rest is a guess of 4 to 6 GiB at peak. 4 GiB
  (`t3.medium`) looked too tight with the profile on and the indexer running at the same time; 8 GiB leaves room.
- **CPU.** `t3` is burstable. Traffic is one user, and the index build (about 60 s of full CPU per the status page) is
  occasional, so credits should cover it. `t3` runs in unlimited mode by default, which can bill extra if credits run out.
- **Volume.** The image is several GiB (torch CPU, model, Node build stage is not in the final image), plus Postgres, the
  search index (about 150 MB), Prometheus (45 days of retention) and Grafana. 40 GiB is a round number, not a sum.

**None of this was measured.** Phase A step 1 of `ec2-deployment-plan.md` (run the stack locally and read
`docker stats`) has not been done. Do that, and change `instance_type` (an in-place stop and resize) if the numbers say so.
Costs were not looked up; check the AWS price list for `t3.large` in your region before applying.

## One-time bootstrap (remote state)

Needs AWS credentials on your machine with rights to create an S3 bucket. The bootstrap keeps its own state in a local
file (`infra/bootstrap/terraform.tfstate`, gitignored); keep that file, it is the only record of the bucket.

```sh
cd infra/bootstrap
terraform init
terraform apply -var="bucket_name=librarian-tfstate-<your account id>"    # prints bucket and region
```

## Plan and apply by hand

The backend block names neither bucket nor key; pass them at init. One key per environment keeps prod and staging
state apart.

```sh
cd infra
terraform init \
  -backend-config="bucket=librarian-tfstate-<your account id>" \
  -backend-config="region=eu-west-1" \
  -backend-config="key=librarian/prod.tfstate"
cp envs/prod.tfvars.example envs/prod.tfvars       # gitignored; edit domain, zone, size
terraform plan  -var-file=envs/prod.tfvars -out=prod.plan
terraform apply prod.plan
```

For staging, run `terraform init -reconfigure` with `key=librarian/staging.tfstate` and use `envs/staging.tfvars`.
Read the plan before applying: the first one should show 13 resources to add (or 12 with no DNS record) and nothing to
change. `terraform output` prints the address, the SSM command and what to do about DNS. Run these only from your own
machine: CI holds no AWS credentials and never plans or applies.

## Reach the host (SSM, no SSH key)

Needs the AWS CLI and its Session Manager plugin on your machine, and credentials allowed to call `ssm:StartSession`.

```sh
aws ssm start-session --region eu-west-1 --target <instance_id>      # also printed as `ssm_command`
```

You land as `ssm-user`. Docker needs root and `/srv/librarian` belongs to `ubuntu`, so `sudo -iu ubuntu` first, then
`sudo docker ...` or add `ubuntu` to the `docker` group yourself. The instance appears in Systems Manager a few minutes
after boot; if it does not, see `/var/log/cloud-init-output.log` (not reachable until SSM works) and the "Not verified" list.

## Hand-over to `docs/ops/deploy.md`

Terraform stops at a host with Docker and an empty `/srv/librarian`. From there follow `docs/ops/deploy.md`: clone to
`/srv/librarian`, fill `.env`, set `LIBRARIAN_IMAGE`, `./librarian start`. Point `LIBRARIAN_DOMAIN` at the Elastic IP
(Route 53 record or by hand) before the first request so Caddy can obtain its certificate. Releases, upgrades and rollback
stay with the `./librarian` wrapper.

**A gap:** deploy.md step 5, `./librarian content push`, is `rsync` over SSH, and this host has no SSH. Options, your
call: use the content-release path (`src/librarian/release/`, `content-release.yml`) instead; or run sshd with a key
authorised for `ubuntu` and tunnel it through SSM (`ProxyCommand` with `AWS-StartSSHSession`), which adds a key this
configuration deliberately does not create. Until one is chosen, the first content load has no documented route.

## Destroy

```sh
cd infra
terraform destroy -var-file=envs/prod.tfvars
```

This deletes the instance **and its volume**: the database, search index and Caddy certificates go with it. Take and
verify a backup first (`docs/ops/restore.md`). The Elastic IP is released, so the address changes on a rebuild.
The state bucket is separate and has `prevent_destroy`; remove that line and empty the bucket (it is versioned) to
delete it.

## CI

`.github/workflows/ci.yml` job `infra` runs `fmt -check -recursive` and, for `infra/` and `infra/bootstrap/`,
`init -backend=false` and `validate`. It holds no AWS credentials and never plans or applies.
`.terraform.lock.hcl` is not committed yet; run `terraform init` once and commit it to pin provider hashes.

## Not verified

Nothing in this folder was applied. On 2026-11-17 `fmt -check -recursive`, `init -backend=false` and `validate` passed
for `infra/` and `infra/bootstrap/` under Terraform 1.10.5 (the `hashicorp/terraform:1.10.5` container, no credentials).
`validate` checks syntax and the provider schema only; it reads nothing from AWS.

- That the same files validate under OpenTofu (not run).
- That `use_lockfile` on the S3 backend works: `validate` ran with `-backend=false`, so the backend block was not exercised.
- That the Canonical SSM parameter path is right and returns an AMI, and that the Ubuntu image has a working SSM agent
  and registers with Session Manager without a VPC endpoint.
- That the account has a default VPC with a default subnet in the region.
- That `user_data.sh` runs to the end on a real instance (Docker's apt repository, the `ubuntu` user, Compose v2 present).
- That the instance type fits the stack, that the image runs on it, and the volume size: all unmeasured.
- That `lifecycle.ignore_changes = [ami]` and `user_data_replace_on_change` together behave as intended.
- The architecture rule in the instance-type precondition (a regex on the type name).
- That Caddy gets a certificate through the Elastic IP, and that the Route 53 record resolves.
- That the S3 bucket, versioning, policy and `use_lockfile` locking work as a backend, including a second `init`.
- That `destroy` removes everything, and that the bootstrap's `prevent_destroy` behaves as described.
- Cost: no prices were looked up.
