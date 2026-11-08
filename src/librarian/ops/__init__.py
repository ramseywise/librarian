"""Operations: encrypted off-host backups, a fenced restore and the upgrade gate.

Core package: it uses `librarian.db`, `librarian.accounts` (the mailer), `librarian.config` and
`librarian.log_config`, and none of the entry points. Everything that needs the Docker host
(stopping and starting services, waiting on /readyz, rolling back an image) lives in the
`./librarian` wrapper; the verbs here do the database and bucket part and exit non-zero on failure.
"""
