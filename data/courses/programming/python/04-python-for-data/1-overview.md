---
imported_hash: 4d259f497ac59c77
title: 1    | Introduction to Python
summary: 'gen = squares() for x in gen: print(x, end='' '')'
order: 20
kind: notebook
section: Python for data
source: learn-ai-engineering/programming/python/04-python-for-data/1_Overview.ipynb
---

# 1    | Introduction to Python

    - Basic Operations:
        - variables, expressions
        - libraries (math, random)
        - functions, conditional statements, iteration, list comprehension
    - Data Structures:
        - Read and write text files from local env and url
        - Array (see numpy)
        - Dataframe (see pandas)
    - Data Types: lists, tuples, dictionaries, strings

*Resources*:
- **Coursera Python for Informatics** (University of Michigan)
- **Python for Data Analytics** - Mckinney (O'Reilly)

## Basic Operations
### Expressions

```python
# assigning variable
string = "Hello world!"
print(string)
```

```python
# basic expression with integers
var=2
print('type: ', type(var),'answer: ', var+2)
```

### Libraries

```python
# random library
import random
for i in range(10):
    x = random.random()
print('random: ',x)

# also with random.randint
print('randint: ',random.randint(1,10))

# or choice using strings in a list
t=['a','b','c','d']
print('choice: ',random.choice(t))
```

```python
# math library
import math
print('log',math.log10(100))
print('pi', math.pi)
print('sqrt', math.sqrt(2)/2)
print('trig', math.cos(5))
```

### Condition and Iteration

```python
# if-else conditional statement
x=5
if x%2==0:
    print("x is even")
else:
    print("x is odd")
```

```python
# iteration updates a variable so that the new value depends on the old
n=5
while n>0:
    print(n)
    n=n-1
print("Blastoff!")
```

```python
# iterate strings as part of a list
friends = ['Joseph', 'Glenn', 'Sally']
for friend in friends:
    print("Happy New Year:", friend)
```

```python
# to calculate count in sequence
count = 0
for itervar in [3, 41, 12, 9, 74, 15]:
    count = count + 1
print("Count: ", count)
```

```python
#Calculate sum with total
total=0
for itervar in [3, 41, 12, 9, 74, 15]:
    total = total + itervar
print("Total: ", total)
```

```python
#Identify the largest number in a sequence
largest = None
print("Before:", largest)
for itervar in [3, 41, 12, 9, 74, 15]:
    if largest is None or itervar > largest :
        largest = itervar
    print("Loop:", itervar, largest)
print("Largest:", largest)
```

```python
# generator expressions
def squares(n=10):
    for i in range(1, n + 1):
        yield i ** 2

gen = squares()
for x in gen:
    print(x, end=' ')
```

```python
# errors and exception handling
def attempt_float(x):
    try:
        return float(x)
    except ValueError:
        return "Error"

print(attempt_float(1))
print(attempt_float('something'))
```

## Data Types
### Strings

```python
# identify characters in a sequence
fruit = 'banana'
for char in fruit:
    print(char)
```

```python
#use len function to identify last item in sequence
length=len(fruit)
last=fruit[length-1]
print(last)
```

```python
#specify item from left or right with the first character as [0]
print(fruit[:3])
print(fruit[3:])
print(fruit[:])
```

```python
#Use a loop to count items in sequence
count = 0
for letter in fruit:
    if letter == 'a':
        count = count + 1
print(count)
```

```python
#change to uppercase
"a" in fruit
"seed" in fruit
FRUIT=fruit.upper()
print(FRUIT)
```

```python
#use find to find characters in a string
fruit.find("na")
```

```python
#strip spaces from text between quotations
line=" Here we go! "
line.strip()
```

```python
#write conditional statements about text
line = 'Please have a nice day'
print('line starts with Please: ', line.startswith('Please'))
print('line starts with p: ', line.startswith('p'))
```

```python
#use \n to return output lines
nextline = 'X\nY'
print(nextline)
```

```python
#format operator constructs strings and replaces parts stored in variables
camels=42
"%d"%camels
"I saw %d camels."%camels
'In %d years I have spotted %g %s.' % (3, 0.1, 'camels')
```

### Lists

```python
#unlike strings, lists are mutable because you can change the order
numbers=[17, "five"]
print('second element as string: ',numbers)

# reassign items to a list
numbers[1]=5
print('second element as integer: ',numbers)
```

```python
#sorting
numbers.sort()
print(numbers)
```

```python
#other functions with lists
print('max: ',max(numbers))
print('min: ',min(numbers))
print('sum: ',sum(numbers))
```

```python
#like strings, lists can also be concatenated
a=[1,2,3]
b=[4,5,6]
c=a+b
print(c)
```

```python
# concat with .extend
c.extend([7, 8])
c
```

```python
# slicing to show only specific items in the list
#second parameter is "up to but not including" (remember starts at [0])
c[1:3]
```

```python
# take only even numbers
c[::2]
```

```python
# reverse number order
c[::-1]
```

```python
# pop returns up to n ordered items in list (left-right)
stuff.pop(2)
stuff
```

```python
# delete items in a list
del c[1]
print(c)
```

```python
#to remove more than one element, you can use del with a slice index
del c[1:5]
print(c)
```

```python
#if you know the element you want to remove (but not the index), you can use remove:
c.remove(6)
print(c)
```

```python
#appending items to end of list
stuff=list() #empty list
stuff.append("book")
stuff.append("movie")
print(stuff)
```

```python
#or use conditional statements to identify if a variable in a list
"ipod" in stuff
```

```python
# add to list in specific order
stuff.insert(1, 'red')
stuff
```

```python
# sort ascending (sorted or .sort())
print('with integers: ', sorted([7, 1, 2, 6, 0, 3, 2]))
print('with strings: ', sorted('horse race'))
```

```python
# sort descending
list(reversed(range(10)))
```

```python
# sort items in list by lenth
b = ['saw', 'small', 'He', 'foxes', 'six']
b.sort(key=len)
b
```

```python
# lists concat but not with set == tuple
l2 = [4, 4, 5, 6]

set(l + l2)
```

```python
# list comprehension
x = [1, 2, 3, 4]

squared = []
for item in x:
    squared.append(item**2)
print('loop: ', squared)
print('list comprehension: ', [item**2 for item in x])
```

```python
# list comprehension to apply upper case to all strings in list
strings = ['a', 'as', 'bat', 'car', 'dove', 'python']
[x.upper() for x in strings if len(x) > 2]
```

```python
# get len for each element in list
unique_lengths = {len(x) for x in strings}
unique_lengths
```

```python
# can also use map()
set(map(len, strings))
```

```python
# create dict with enumerated elements (ordered)
loc_mapping = {val : index for index, val in enumerate(strings)}
loc_mapping
```

```python
# nested list comprehension to locate element with 2 e's
all_data = [['John', 'Emily', 'Michael', 'Mary', 'Steven'],
            ['Maria', 'Juan', 'Javier', 'Natalia', 'Pilar']]

result = [name for names in all_data for name in names
          if name.count('e') >= 2]
result
```

```python
# flatten nested list into single list
some_tuples = [(1, 2, 2, 3), (4, 5, 6), (7, 8, 9)]
flattened = [x for tup in some_tuples for x in tup]
flattened
```

### Tuples

```python
#like lists, tubles is a sequence of values that are immutable (like strings)
#but they are more efficient when creating a temporary list that won't be changed
#unpack tuples
tup = (4, 5, 6)
a, b, c = tup
print('from', tup, 'to', b)
```

```python
# assert tuples do not have order
print('assert with list:',[1, 2, 3] == [3, 2, 1],'\nassert with set:',{1, 2, 3} == {3, 2, 1},'\nassert with tupl:',(1, 2, 3) == (3, 2, 1))
```

```python
#create a tuple and print left hand side of the assignment (parentheses optional)
(x,y)=(4,12)
print(x)
```

```python
#you can't modify a tuple, but you can replace it with another by identifying order in tuple
t=("L",) + t[1:]
print(t)
```

```python
# list of tuple
seq = [(1, 2, 3), (4, 5, 6), (7, 8, 9)]
for a, b, c in seq:
    print('a={0}, b={1}, c={2}'.format(a, b, c))
```

### Dictionaries

```python
#print key-value pairs by key
for k in sorted(c):
    print(k, c[k])
```

```python
#sorting dict by key
c = {'a': 10, 'c': 22, 'b': 1, 'f': 22}
sorted(c)
```

```python
#create temporary list to sort by values instead of key and reverse sort
tmp=list()
for k,v in c.items():
    tmp.append((v,k))
tmp.sort(reverse=True)
print(tmp)
```

```python
#shorthand for list comprehension in ascending order
print(sorted([(v,k) for k,v in c.items()]))
```

```python
#Whereas list is a linear collection of ordered values, a dictionary is an assortment of unordered labeled values, similar to a database
#Becuase dictionaries are not ordered, they require labels (or key for values)
# create and fillempty dict
purse = dict()
purse['money'] = 12
purse['candy'] = 3
purse['tissues'] = 75

#check if key is in dictionary
print('print dict',purse,"\nassert money is in purse:", 'money' in purse)
```

```python
#use dictionaries to count items
counts = dict()
names = ['csev','owen','csev','zqian','cwen']
for name in names:
    if name not in counts:
        counts[name]= 1
    else:
        counts[name] = counts[name] + 1
print(counts)
```

```python
#equivalent to the GET function
for name in names:
    counts[name]=counts.get(name,0)
print(counts)
```

```python
# unpack items, keys and values as nested list
print('items:',counts.items(),'\nitems:',counts.keys(),'\nvalues:',counts.values())
list(d1.keys())
```

```python
# enumerated items in diction
for i, (a, b) in enumerate(zip(seq1, seq2)):
    print('{0}: {1}, {2}'.format(i, a, b))
```

```python
# use zip to create dict from list
seq1 = ['foo', 'bar', 'baz']
seq2 = ['one', 'two', 'three']
zipped = zip(seq1, seq2)
list(zipped)
```

```python
# add element to nested list
seq3 = [False, True]
list(zip(seq1, seq2, seq3))
```

```python
# create tuple from item in nested list
pitchers = [('Nolan', 'Ryan'), ('Roger', 'Clemens'),
            ('Schilling', 'Curt')]
first_names, last_names = zip(*pitchers)
first_names
last_names
```

```python
# create nested list in a dictionary
empty_dict = {}
d1 = {'a' : 'some value', 'b' : [1, 2, 3, 4]}

# add new item
d1['7'] = 'another value'
d1
```

```python
# replace value for dict item
d1.update({'b' : 'foo', 'c' : 12})
d1
```

```python
# use pop to return value of a key
ret = d1.pop('7')
ret
```

```python
# delete item in dict
del d1['7']
d1
```
