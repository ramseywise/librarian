---
name: tdd
description: "Test-driven implementation loop for risky behavior changes. Use when the user asks for TDD, red-green-refactor, test-first work, regression fixes, or when changing non-trivial behavior in agents, evals, graders, retrieval, or reporting."
allowed-tools: Read Grep Glob Bash Edit Write
---

# TDD

Implement one observable behavior at a time with a red-green-refactor loop.

## When to use

Use this skill for behavior changes where a fast regression signal matters:

- Agent routing, retrieval, guardrail, grounding, or schema behavior
- Eval graders, metrics, report aggregation, or rendering
- Bug fixes with a clear expected behavior
- Public functions/classes/modules that are not trivial delegation

Do not use this for throwaway prototypes, mechanical docs edits, or purely generated artifacts.

## Principles

- Test behavior through the public interface, not private helpers.
- Prefer integration-style unit tests over implementation-mocked tests.
- Add one test, make it fail for the right reason, then write the smallest production change.
- Never refactor while the test is red.
- Keep the loop small enough that the agent can understand exactly what changed.

## Before coding

1. Read the target code and adjacent tests.
2. Identify the public interface the behavior should be visible through.
3. Name the behavior in repo vocabulary: agent, retrieval, grader, metric, report, guardrail, or schema.
4. Choose the narrowest safe command, usually:
   - `uv run pytest tests/ -q --tb=short -k "<symbol_or_behavior>"`
   - `make test` for broad shared behavior
5. State the first behavior and the command that will prove it.

If the correct test seam does not exist, say that explicitly. Add the smallest seam that tests real behavior, not a private implementation detail.

## Red-green loop

For each behavior:

1. **RED**: Add or update one test that describes the observable behavior.
2. Run the narrow test command and confirm it fails for the expected reason.
3. **GREEN**: Implement only enough code to pass that test.
4. Run the same narrow command and confirm it passes.
5. Repeat for the next behavior.

Do not batch five imagined tests before implementation. Let each test respond to what the previous loop taught you.

## Refactor

Only after all relevant tests are green:

- Remove duplication introduced during the loop.
- Simplify names and control flow.
- Keep interfaces small and stable.
- Run the same narrow tests after each refactor.
- Finish with the broader relevant suite (`make test` or a focused `uv run pytest tests/...`).

## Output

Report:

- Behaviors covered
- Test commands run and result
- Any seam that was missing or improved
- Any intentional scope left untested and why
