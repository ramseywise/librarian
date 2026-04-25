ROOT      := $(shell git rev-parse --show-toplevel)
AGENT     := $(ROOT)/agents/simple_router
EVAL_DIR  := $(AGENT)/eval
EVAL_APPS := $(AGENT)/eval_apps

# Optional:
#   make eval-routing CASES=my_case
#   make eval-routing CASES=case1,case2
CASES ?=

.PHONY: run test eval eval-routing eval-response eval-behavior eval-error \
        eval-subagents eval-invoice-agent eval-support-agent \
        eval-receptionist-agent eval-orchestrator-agent

run:
	uv --project $(ROOT) run adk run $(AGENT)

test:
	uv --project $(ROOT) run pytest $(ROOT)/agents/simple_router/tests/ -v

eval: eval-routing eval-response eval-behavior eval-error

eval-routing:
	uv --project $(ROOT) run adk eval $(AGENT) \
		$(EVAL_DIR)/routing_evalset.json$(if $(CASES),:$(CASES)) \
		--config_file_path $(EVAL_DIR)/routing_eval_config.json \
		--print_detailed_results

eval-response:
	uv --project $(ROOT) run adk eval $(AGENT) \
		$(EVAL_DIR)/response_evalset.json$(if $(CASES),:$(CASES)) \
		--config_file_path $(EVAL_DIR)/response_eval_config.json \
		--print_detailed_results

eval-behavior:
	uv --project $(ROOT) run adk eval $(AGENT) \
		$(EVAL_DIR)/behavior_evalset.json$(if $(CASES),:$(CASES)) \
		--config_file_path $(EVAL_DIR)/behavior_eval_config.json \
		--print_detailed_results

eval-error:
	uv --project $(ROOT) run adk eval $(AGENT) \
		$(EVAL_DIR)/error_evalset.json$(if $(CASES),:$(CASES)) \
		--config_file_path $(EVAL_DIR)/error_eval_config.json \
		--print_detailed_results

# ── Subagent evals (independent — no router involved) ─────────────────────────

eval-subagents: eval-invoice-agent eval-support-agent eval-receptionist-agent eval-orchestrator-agent

eval-invoice-agent:
	uv --project $(ROOT) run adk eval $(EVAL_APPS)/invoice_agent \
		$(EVAL_APPS)/invoice_agent/evalset.json$(if $(CASES),:$(CASES)) \
		--config_file_path $(EVAL_APPS)/invoice_agent/eval_config.json \
		--print_detailed_results

eval-support-agent:
	uv --project $(ROOT) run adk eval $(EVAL_APPS)/support_agent \
		$(EVAL_APPS)/support_agent/evalset.json$(if $(CASES),:$(CASES)) \
		--config_file_path $(EVAL_APPS)/support_agent/eval_config.json \
		--print_detailed_results

eval-receptionist-agent:
	uv --project $(ROOT) run adk eval $(EVAL_APPS)/receptionist_agent \
		$(EVAL_APPS)/receptionist_agent/evalset.json$(if $(CASES),:$(CASES)) \
		--config_file_path $(EVAL_APPS)/receptionist_agent/eval_config.json \
		--print_detailed_results

eval-orchestrator-agent:
	uv --project $(ROOT) run adk eval $(EVAL_APPS)/orchestrator_agent \
		$(EVAL_APPS)/orchestrator_agent/evalset.json$(if $(CASES),:$(CASES)) \
		--config_file_path $(EVAL_APPS)/orchestrator_agent/eval_config.json \
		--print_detailed_results
