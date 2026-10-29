---
imported_hash: a4ec02bf024a2c7c
title: Propositional Logic
summary: proposition_P = 'He is hungry' propositon_Q = 'He will eat a sandwich'
order: 24
kind: notebook
section: Ch08   Semantic Analysis
source: learn-ai-engineering/data-science/Text Analytics with Python/Ch08 - Semantic Analysis/Ch08d - Analyzing Semantic Representations.ipynb
---

```python
import nltk
import pandas as pd
import os
```

# Propositional Logic

```python
# assign symbols and propositions
symbol_P = 'P'
symbol_Q = 'Q'

proposition_P = 'He is hungry'
propositon_Q = 'He will eat a sandwich'
```

```python
# assign various truth values to the propositions
p_statuses = [False, False, True, True]
q_statuses = [False, True, False, True]
```

```python
# assign the various expressions combining the logical operators
conjunction = '(P & Q)'
disjunction = '(P | Q)'
implication = '(P -> Q)'
equivalence = '(P <-> Q)'
expressions = [conjunction, disjunction, implication, equivalence]
expressions
```

```python
# evaluate each expression using propositional logic
results = []
for status_p, status_q in zip(p_statuses, q_statuses):
    dom = set([])
    val = nltk.Valuation([(symbol_P, status_p),
                          (symbol_Q, status_q)])
    assignments = nltk.Assignment(dom)
    model = nltk.Model(dom, val)
    row = [status_p, status_q]
    for expression in expressions:
    # evaluate each expression based on proposition truth values
        result = model.evaluate(expression, assignments)
        row.append(result)
    results.append(row)
```

```python
# build the result table
columns = [symbol_P, symbol_Q, conjunction,
           disjunction, implication, equivalence]
result_frame = pd.DataFrame(results, columns=columns)
```

```python
# display results
print('P:', proposition_P)
print('Q:', propositon_Q)
print()
print('Expression Outcomes:-')
print(result_frame)
```

# First Order Logic

```python
import nltk
import os

# for reading FOL expressions
read_expr = nltk.sem.Expression.fromstring

# initialize theorem provers (you can choose any)
os.environ['PROVER9'] = r'E:/prover9/bin'
prover = nltk.Prover9()

# I use the following one for our examples
prover = nltk.ResolutionProver()
prover
```

```python
# set the rule expression
rule = read_expr('all x. all y. (jumps_over(x, y) -> -jumps_over(y, x))')

# set the event occured
event = read_expr('jumps_over(fox, dog)')

# set the outcome we want to evaluate -- the goal
test_outcome = read_expr('jumps_over(dog, fox)')

# get the result
prover.prove(goal=test_outcome,
             assumptions=[event, rule],
             verbose=True)
```

```python
# set the rule expression
rule = read_expr('all x. (studies(x, exam) -> pass(x, exam))')

# set the events and outcomes we want to determine
event1 = read_expr('-studies(John, exam)')
test_outcome1 = read_expr('pass(John, exam)')

prover.prove(goal=test_outcome1,
             assumptions=[event1, rule],
             verbose=True)
```

```python
event2 = read_expr('studies(Pierre, exam)')
test_outcome2 = read_expr('pass(Pierre, exam)')

prover.prove(goal=test_outcome2,
             assumptions=[event2, rule],
             verbose=True)
```

```python
# define symbols (entities\functions) and their values
rules = """
    rover => r
    felix => f
    garfield => g
    alex => a
    dog => {r, a}
    cat => {g}
    fox => {f}
    runs => {a, f}
    sleeps => {r, g}
    jumps_over => {(f, g), (a, g), (f, r), (a, r)}
    """

val = nltk.Valuation.fromstring(rules)
val
```

```python
dom = {'r', 'f', 'g', 'a'}
m = nltk.Model(dom, val)
m
```

```python
m.evaluate('jumps_over(felix, rover) & dog(rover) & runs(rover)', None)
```

```python
m.evaluate('jumps_over(felix, rover) & dog(rover) & -runs(rover)', None)
```

```python
m.evaluate('jumps_over(alex, garfield) & dog(alex) & cat(garfield) & sleeps(garfield)', None)
```

```python
g = nltk.Assignment(dom, [('x', 'r'), ('y', 'f')])
g
```

```python
m.evaluate('runs(y) & jumps_over(y, x) & sleeps(x)', g)
```

```python
m.evaluate('exists y. (fox(y) & runs(y))', g)
```

```python
formula = read_expr('runs(x)')
m.satisfiers(formula, 'x', g)
```

```python
formula = read_expr('runs(x) & fox(x)')
m.satisfiers(formula, 'x', g)
```
