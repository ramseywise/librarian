---
imported_hash: 289fbff42116773a
title: LeetCode Problems
summary: '7 data structures: 1. arrays: - Longest consecutive subsequence (medium) - topKFreuquent (medium)'
order: 13
kind: notebook
section: Leetcode
source: sisyphus/drills/python/leetcode/Probability-Problems.ipynb
---

# LeetCode Problems

to be completed...

7 data structures:
1. arrays:
    - Longest consecutive subsequence (medium)
    - topKFreuquent (medium)

2. queues:
    - last stone weight (easy)
    - k closest points to origin (medium)
    - k largest element (medium)
    - task scheduler (medium)
    - simplified twitter (medium)

3. stacks:
    - Car Fleet (medium)
    - daily temperatures (medium)
    - Largest Rectangle in Histogram (hard)

4. linked lists:
    - reverse linked list (easy)
    - remove nth node (medium)
    - reorder list (medium)
    - find duplicate (medium)

5. trees:
    - invert binary tree (easy)
    - maximum depth of binary tree (easy)
    - subtree of another tree (easy)
    - count good nodes (medium)
    - serialize/deserialize binary tree (hard)
    - Implement trie (medium)
    - word search i & ii (hard)

6. graphs
    - reconstruct itinerary (hard)
    - network delay time (medium)
    - swim in rising water (meidum)
    - cheapest flights (medium)

7. intervals:
    - insert interval (medium)
    - merge interval (medium)
    - non-overlapping intervals (medium)
    - meeting rooms i & ii (medium)


Techniques:
1. two-pointers:
    - container holds max water (medium)
    - trapping rain water (hard)

2. sliding windows:
    - longest repeating character replacement (medium)
    - permutation in string (medium)
    - minimum window substring (hard)
    - maximum window substring (hard)

3. binary search:
    - binary search (easy)
    - koko eats bananas (medium)
    - search rotated array (medium)
    - find minimum in rotated array (medium)
    - time-based key-value pair (medium)
    - median of two sorted arrays (hard)

4. greedy:
    - jump game 1 & 2 (medium)
    - gas station (medium)
    - hand of straights (medium)
    - partition labels (medium)

5. Recursive:
    - add two numbers
    - merge 2 sorted lists
    - swap nodes in pairs
    - reverse nodes in k-groups
    - wildcard matching

6. Backtracking
    - subsets i & ii (medium)
    - permutations (medium)
    - letter combo of phone (medium)



Dynamic Programming
- nim game
- climbing stairs (easy)
- house robbber i & ii (medium)
- Longest Palindromic Substring (medium)
- coin change i & ii (medium)
- word break (medium)
- partition equal subset sum (medium)
- unique paths (medium)
- longest common subsequence (medium)
- longest increasing path (hard)
- burst balloons (hard)

## Probability problems
### Practice Probability Examples

```python
import random
import numpy as np
```

```python
def rollDiceProb(o,r):
    """Returns probability that two dice thrown is even."""
    count = 0
    for i in range(r): # loop for number of rolls
        score = random.randint(1,o) # return random array for 100 roles in range 1-6
        if score % 2: # criteria that roll even numbers using modulo operator
            count += 1 # add to count

    return count/r

o=6 # options to roll on dice
r=100 # number of rolls

string = 'The probability of rolling an even number: '
print(string,np.round(rollDiceProb(n,r)*100,2),'%')
```

```python
def rollDiceProbSim(o,r,n):
    """Returns probability that two dice thrown is even."""
    counts = 0
    for i in range(n): # outer loop each interation
        count = 0
        for i in range(r): # inner loop for number of rolls
            score = random.randint(1,o) # return random array for 100 roles in range 1-6
            count += 1 # add to count
            if count % 2 or score > 7: # criteria that roll even numbers using modulo operator
                counts += 1 # add to count

    return counts/r

o=6 # options to roll on dice
r=100 # number of rolls
n=100000 # number of simulations (law of large numbers --> probability nears to 1)

string = 'The probability of rolling an even number: '
print(string,np.round(rollDiceProb(n,r)*100,2),'%')
```

```python
def rollDiceProb(n):
    """Returns probability that two dice thrown is even or greater than 7 using simulation approach."""
    count = 0
    for i in range(n): # loop each interation
        roll1 = random.randint(1,6) # probability of roll 1 of 6 in first round
        roll2 = random.randint(1,6) # probability of roll 1 of 6 in second round
        score = roll1 + roll2 # sum values to get score
        if score % 2 == 0 or score > 7: # criteria that roll even using modulo operator (returns remainder) or if greater than 7
            count += 1 # add to count

    return count/n

n=100000 # number of simulations (law of large numbers --> probability nears to 1)
string = 'The probability of rolling an even number or greater than 7 is: '
print(string,np.round(rollDiceProb(n)*100,2),'%')
```

```python
def rollDiceProb(n):
    """Returns probability that two dice thrown is even or greater than 7 using simulation approach."""
    count = 0
    for i in range(n): # loop each interation
        roll1 = random.randint(1,6) # probability of roll 1 of 6 in first round
        roll2 = random.randint(1,6) # probability of roll 1 of 6 in second round
        roll3 = random.randint(1,6) # probability of roll 1 of 6 in second round
        score = roll1 + roll2 + roll3 # sum values to get score
        if score % 2 == 0 or score > 7: # criteria that roll even using modulo operator (returns remainder) or if greater than 7
            count += 1 # add to count

    return count/n

n=100000 # number of simulations (law of large numbers --> probability nears to 1)
string = 'The probability of rolling an even number or greater than 7 is: '
print(string,np.round(rollDiceProb(n)*100,2),'%')
```

### Luck of the Draw

A box contains 10 white balls, 20 reds and 30 greens. Draw 5 balls with replacement… what is the probability that:

    a) 3 white or 2 red
    b) All 5 are the same color

```python
# first create for 3 color classes in a dictionary for all 60 balls
d = {}
for i in range(60): # number of balls in total
    if i < 10: # assign 10 balls to white
        d[i] = 'white'
    elif i > 9 and i < 30: # assign 20 balls to red
        d[i] = 'red'
    else: # assign remaining 30 balls to green
        d[i] = 'green'

n = 100000 # number of simulations
A = 0 # subtotal for Part A solution
B = 0 # subtotal for Part B solution

for i in range(n):
    arr = [] # create array of balls chosen for 5 draws over 100k iterations
    for i in range(5):
        arr.append(d[random.randint(0,59)]) # why can't use arr = np.vectorize(d.get)(numpy.random.randint(0,59,5))

    # sum which ball was selected for all 5 draws (works for list, not numpy array)
    white = arr.count('white')
    red = arr.count('red')
    green = arr.count('green')

    # criteria for Part A combination
    if white == 3 and red ==2:
        A += 1

    # criteria for Part B combination
    if red == 5 | white == 5 | green ==5:
        B += 1

print('The probability of drawing 3 white and 2 red balls is: ', (A/n)*100,'%')
print('The probability of drawing all same color: ', (B/n)*100,'%')
```

```python
# what if balls are removed
def ballsFromHat():
    """Returns dictionary of randomly selected balls from hat."""
    balls = {
        "red":5,
        "yellow":5,
        "green":5,
        "brown":5
    }

    #Create a new empty dictionary to keep the drawn balls
    drawn = dict.fromkeys(balls.keys(), 0)
    toDraw = 3

    for i in range(toDraw):
        rball = random.choice(list(balls))
        balls[rball] -= 1 # remove random ball from hat
        drawn[rball] += 1 # add to drawn count

    return drawn

# calculate number of matches to get probability
match = 0
for i in range(n):
    r = ballsFromHat()
    if r["brown"] >= 1 and r["green"] >= 1: # criteria if we get at least 1 brown and 1 green
        match += 1

print('Probability that we get at least one brown a one green', (match/float(n)*100),'%')
```

### Problem 808: Soup Servings

There are two types of soup: type A and type B. Initially, we have n ml of each type of soup. There are four kinds of operations:

    1) Serve 100 ml of soup A and 0 ml of soup B --> A becomes empty first
    2) Serve 75 ml of soup A and 25 ml of soup B --> A becomes empty first
    3) Serve 50 ml of soup A and 50 ml of soup B --> A & B become empty at some time
    4) Serve 25 ml of soup A and 75 ml of soup B --> B becomes empty first

When we serve some soup, we give it to someone, and we no longer have it. Each turn, we will choose from the four operations with an equal probability 0.25. If the remaining volume of soup is not enough to complete the operation, we will serve as much as possible. We stop once we no longer have some quantity of both types of soup.

*Note: that we do not have an operation where all 100 ml's of soup B are used first.

**Return the probability that soup A will be empty first, plus half the probability that A and B become empty at the same time. Answers within 10-5 of the actual answer will be accepted.

```python
class Solution(object):
    def soupHelper(self, A, B, state):
        if (A, B) in state:
            return state[A, B]

        if A <=0 or B <= 0:
            if A <= 0 and B <= 0:
                return 0.5
            if B > 0:
                return 1
            return 0
        prob = 0
        prob += self.soupHelper(A - 100, B, state)
        prob += self.soupHelper(A - 75, B - 25, state)
        prob += self.soupHelper(A - 50, B - 50, state)
        prob += self.soupHelper(A - 25, B - 75, state)
        state[A, B] = 0.25 * prob
        return state[A, B]

    def soupServings(self, N):
        """
        :type N: int
        :rtype: float
        """
        if N > 4800:
            return 1.
        state = dict()
        prob = self.soupHelper(N, N, state)
        return prob
```

```python






f(a,b) means the result probability for a ml of soup A and b ml of soup B.
f(a-4,b) means that we take the first operation: Serve 100 ml of soup A and 0 ml of soup B.
f(a-3,b-1), f(a-2,b-2), f(a-1,b-3) are other 3 operations.
Fibonacci sequence. It calculate every case for only once and it can be reused for every test case.
It's obvious that A is easier to be empty than B. And when N gets bigger, we have less chance to run out of B first.
So as N increases, our result increases and it gets closer to 100 percent = 1.
```

```python
Input: n = 100
Output: 0.71875
```
