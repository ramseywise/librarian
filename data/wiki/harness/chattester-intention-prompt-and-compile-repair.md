---
title: ChatTester Intention Prompt and Compile Repair
tags: [harness, pattern]
summary: An LLM unit-test generator that first asks for the method's intention and then repairs compile errors in a bounded loop, built on an empirical study of ChatGPT-generated Java tests.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-yuan-2023-no-more-manual-tests.md
---

# ChatTester Intention Prompt and Compile Repair

Yuan et al. (FSE, Article 76; the arXiv version is v3, 2305.04207) first study ChatGPT-generated unit tests, then propose ChatTester. The authors built it and report the results.

## Mechanism

- **Intention step:** the generator first asks the model for the focal method's intention, then generates the test.
- **Refiner:** compile the test, parse the error, add the error type, the buggy line and related class signatures, and ask for a fix. It halts once the test works, or when more than 3 rounds in a row bring no improvement. It repairs compile errors only.

## Reported numbers (self-reported)

- Study (185 Maven projects supply 1,000 Java focal methods; the model is gpt-3.5-turbo on default settings; a basic zero-shot prompt; one run): 42.1% of tests compile and 24.8% pass. Another 57.9% do not compile, and 17.3% compile but fail when executed. Of 173 failed executions, 148 (85.5%) were assertion errors, which manual inspection judged to be incorrect assertions rather than focal-method bugs.
- ChatTester (100 held-out methods, average of three runs): compilation 39.0% to 73.3%, passing 22.3% to 41.0%. The refiner alone reached 60.6% and 34.0%; the intention step alone 50.7% and 29.7%.
- Each focal method costs about 99.0 seconds. Among tests that needed refinement, those reaching iterations 5 to 7 compiled, but none of them passed.
- CodeLlama-Instruct-34B passing 3.0% to 21.0%; CodeFuse-34B 0.0% to 11.0%. On Python HumanEval (164 methods) successful execution 31.7% to 43.2%.
- The ChatGPT tests that pass achieve 82.3% statement coverage, compared with 84.2% for manual tests.

## Limits

- The study ran once because of the user-study effort; the ChatTester evaluation uses 100 methods.
- Java and Maven only, with Python checked on HumanEval; gpt-3.5-turbo only; possible training-data leakage.
- The refiner cannot tell a bad test from a bad focal method on execution failures.
- Evosuite's higher compile and pass rates result from validation after generation, and the authors caution against concluding that it is the better tool.

## See Also
- [[TestGen-LLM Filter Cascade]] — related (generate then filter tests)
- [[Verification Loops]] — related
