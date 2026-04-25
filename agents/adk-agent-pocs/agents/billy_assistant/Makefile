ROOT      := $(shell git rev-parse --show-toplevel)
AGENT     := $(ROOT)/agents/billy_assistant
EVAL_DIR  := $(AGENT)/eval

# Optional:
#   make eval-routing CASES=my_case
#   make eval-routing CASES=case1,case2
CASES ?=

.PHONY: help run web web-debug test eval eval-routing eval-response eval-behavior eval-error

help:
	@echo "Usage: make -C agents/billy_assistant <target> [CASES=case1,case2]"
	@echo ""
	@echo "Targets:"
	@echo "  run            Start the agent in interactive mode (adk run)"
	@echo "  web            Start the agent in web UI (adk web)"
	@echo "  web-debug      Start the agent in web UI with BILLY_DEBUG=1"
	@echo "  test           Run unit tests (pytest)"
	@echo "  eval           Run all eval suites"
	@echo "  eval-routing   Routing accuracy   — tool_trajectory_avg_score threshold 1.0"
	@echo "  eval-response  Response quality   — final_response_match_v2   threshold 1.0"
	@echo "  eval-behavior  Behavioral quality — rubric_based              threshold 0.8"
	@echo "  eval-error     Error handling     — rubric_based              threshold 0.8"
	@echo ""
	@echo "Examples:"
	@echo "  make -C agents/billy_assistant eval-routing"
	@echo "  make -C agents/billy_assistant eval-routing CASES=support_question_routes_to_support"

run:
	uv --project $(ROOT) run adk run $(AGENT)

web:
	uv --project $(ROOT) run adk web $(ROOT)/agents

web-debug:
	BILLY_DEBUG=1 uv --project $(ROOT) run adk web $(ROOT)/agents

test:
	uv --project $(ROOT) run pytest $(AGENT)/tests/ -v

define run-eval
	uv --project $(ROOT) run adk eval $(AGENT) \
		$(EVAL_DIR)/$(1)_evalset.json$(if $(CASES),:$(CASES)) \
		--config_file_path $(EVAL_DIR)/$(1)_eval_config.json \
		--print_detailed_results
endef

eval: eval-routing eval-response eval-behavior eval-error

eval-routing:
	$(call run-eval,routing)

eval-response:
	$(call run-eval,response)

eval-behavior:
	$(call run-eval,behavior)

eval-error:
	$(call run-eval,error)
