---
imported_hash: 8382e6795049a7c4
title: zen of python
summary: 'print(''ID:'', id(new_string)) # shows the object identifier (address) print(''Type:'', type(new_string)) # shows the object type print(''Value:'', new_string) # shows the object value'
order: 4
kind: notebook
section: Ch02   Python for Natural Language Processing
source: learn-ai-engineering/data-science/Text Analytics with Python/Ch02 - Python for Natural Language Processing/Ch02b - Working with Text Data.ipynb
---

```python
# zen of python
import this
```

```
stringliteral   ::=  [stringprefix](shortstring | longstring)
stringprefix    ::=  "r" | "u" | "ur" | "R" | "U" | "UR" | "Ur" | "uR"
                     | "b" | "B" | "br" | "Br" | "bR" | "BR"
shortstring     ::=  "'" shortstringitem* "'" | '"' shortstringitem* '"'
longstring      ::=  "'''" longstringitem* "'''" | '"""' longstringitem* '"""'
shortstringitem ::=  shortstringchar | escapeseq
longstringitem  ::=  longstringchar | escapeseq
shortstringchar ::=  <any source character except "\" or newline or the quote>
longstringchar  ::=  <any source character except "\">
escapeseq       ::=  "\" <any ASCII character>
```

# String types

```python
new_string = "This is a String"  # storing a string

print('ID:', id(new_string))  # shows the object identifier (address)
print('Type:', type(new_string))  # shows the object type
print('Value:', new_string)  # shows the object value
```

```python
# simple string
simple_string = 'Hello!' + " I'm a simple string"
print(simple_string)
```

```python
# multi-line string, note the \n (newline) escape character automatically created
multi_line_string = """Hello I'm
a multi-line
string!"""

multi_line_string
```

```python
print(multi_line_string)
```

```python
# Normal string with escape sequences leading to a wrong file path!
escaped_string = "C:\the_folder\new_dir\file.txt"
print(escaped_string)  # will cause errors if we try to open a file here
```

```python
# raw string keeping the backslashes in its normal form
raw_string = r'C:\the_folder\new_dir\file.txt'
print(raw_string)
```

```python
# unicode string literals
string_with_unicode = 'H\u00e8llo!'
print(string_with_unicode)
```

```python
more_unicode = 'I love Pizza 🍕!  Shall we book a cab 🚕 to get pizza?'
print(more_unicode)
```

```python
print(string_with_unicode + '\n' + more_unicode)
```

```python
' '.join([string_with_unicode, more_unicode])
```

```python
more_unicode[::-1]  # reverses the string
```

# String operations

## Different ways of String concatenation

```python
'Hello 😊' + ' and welcome ' + 'to Python 🐍!'
```

```python
'Hello 😊' ' and welcome ' 'to Python 🐍!'
```

```python
# concatenation of variables and literals
```

```python
s1 = 'Python 💻!'
'Hello 😊 ' + s1
```

```python
'Hello 😊 ' s1
```

```python
# some more ways of concatenating strings
```

```python
s2 = '--🐍Python🐍--'
s2 * 5
```

```python
s1 + s2
```

```python
(s1 + s2)*3
```

```python
# concatenating several strings together in parentheses
```

```python
s3 = ('This '
      'is another way '
      'to concatenate '
      'several strings!')
s3
```

```python
# checking for substrings in a string
```

```python
'way' in s3
```

```python
'python' in s3
```

```python
# computing total length of the string
```

```python
len(s3)
```

# String indexing and slicing

```python
# creating a string
s = 'PYTHON'
s, type(s)
```

## String indexing

```python
# depicting string indexes
for index, character in enumerate(s):
    print('Character ->', character, 'has index->', index)
```

```python
s[0], s[1], s[2], s[3], s[4], s[5]
```

```python
s[-1], s[-2], s[-3], s[-4], s[-5], s[-6]
```

## String slicing

```python
s[:]
```

```python
s[1:4]
```

```python
s[:3], s[3:]
```

```python
s[-3:]
```

```python
s[:3] + s[3:]
```

```python
s[:3] + s[-3:]
```

## String slicing with offsets

```python
s[::1]  # no offset
```

```python
s[::2]  # print every 2nd character in string
```

# String Immutability

```python
# strings are immutable hence assignment throws error
s[0] = 'X'
```

```python
print('Original String id:', id(s))
# creates a new string
s = 'X' + s[1:]
print(s)
print('New String id:', id(s))
```

# Useful String methods

## Case conversions

```python
s = 'python is great'
```

```python
s.capitalize()
```

```python
s.upper()
```

```python
s.title()
```

## String replace

```python
s.replace('python', 'NLP')
```

## Numeric checks

```python
'12345'.isdecimal()
```

```python
'apollo11'.isdecimal()
```

## Alphabet checks

```python
'python'.isalpha()
```

```python
'number1'.isalpha()
```

## Alphanumeric checks

```python
'total'.isalnum()
```

```python
'abc123'.isalnum()
```

```python
'1+1'.isalnum()
```

## String splitting and joining

```python
s = 'I,am,a,comma,separated,string'
s.split(',')
```

```python
' '.join(s.split(','))
```

```python
# stripping whitespace characters
s = '   I am surrounded by spaces    '
s
```

```python
s.strip()
```

```python
sentences = 'Python is great. NLP is also good.'
sentences.split('.')
```

```python
print('\n'.join(sentences.split('.')))
```

```python
print('\n'.join([sentence.strip()
                     for sentence in sentences.split('.')
                         if sentence]))
```

# String formatting

## Simple string formatting expressions - old style

```python
'Hello %s' %('Python!')
```

```python
'Hello %s %s' %('World!', 'How are you?')
```

## Formatting expressions with different data types - old style

```python
'We have %d %s containing %.2f gallons of %s' %(2, 'bottles', 2.5, 'milk')
```

```python
'We have %d %s containing %.2f gallons of %s' %(5.21, 'jugs', 10.86763, 'juice')
```

## Formatting strings using the format method - new style

```python
'Hello {} {}, it is a great {} to meet you at {}'.format('Mr.', 'Jones', 'pleasure', 5)
```

```python
'Hello {} {}, it is a great {} to meet you at {} o\' clock'.format('Sir', 'Arthur', 'honor', 9)
```

## Alternative ways of using string format

```python
'I have a {food_item} and a {drink_item} with me'.format(drink_item='soda', food_item='sandwich')
```

```python
'The {animal} has the following attributes: {attributes}'.format(animal='dog', attributes=['lazy', 'loyal'])
```

# Regular Expressions

```python
s1 = 'Python is an excellent language'
s2 = 'I love the Python language. I also use Python to build applications at work!'
```

```python
import re

pattern = 'python'
# match only returns a match if regex match is found at the beginning of the string
re.match(pattern, s1)
```

```python
# pattern is in lower case hence ignore case flag helps
# in matching same pattern with different cases
re.match(pattern, s1, flags=re.IGNORECASE)
```

```python
# printing matched string and its indices in the original string
m = re.match(pattern, s1, flags=re.IGNORECASE)
print('Found match {} ranging from index {} - {} in the string "{}"'.format(m.group(0),
                                                                            m.start(),
                                                                            m.end(), s1))
```

```python
# match does not work when pattern is not there in the beginning of string s2
re.match(pattern, s2, re.IGNORECASE)
```

```python
# illustrating find and search methods using the re module
re.search(pattern, s2, re.IGNORECASE)
```

```python
re.findall(pattern, s2, re.IGNORECASE)
```

```python
match_objs = re.finditer(pattern, s2, re.IGNORECASE)
match_objs
```

```python
print("String:", s2)
for m in match_objs:
    print('Found match "{}" ranging from index {} - {}'.format(m.group(0),
                                                               m.start(), m.end()))
```

```python
# illustrating pattern substitution using sub and subn methods
re.sub(pattern, 'Java', s2, flags=re.IGNORECASE)
```

```python
re.subn(pattern, 'Java', s2, flags=re.IGNORECASE)
```

```python
# dealing with unicode matching using regexes
s = u'H\u00e8llo! this is Python 🐍'
s
```

```python
re.findall(r'\w+', s)
```

```python
re.findall(r"[A-Z]\w+", s, re.UNICODE)
```

```python
emoji_pattern = r"['\U0001F300-\U0001F5FF'|'\U0001F600-\U0001F64F'|'\U0001F680-\U0001F6FF'|'\u2600-\u26FF\u2700-\u27BF']"
re.findall(emoji_pattern, s, re.UNICODE)
```

# Putting it all together - Basic Text Processing and Analysis

```python
from nltk.corpus import gutenberg
import matplotlib.pyplot as plt

%matplotlib inline

bible = gutenberg.open('bible-kjv.txt')
bible = bible.readlines()

bible[:5]
```

```python
len(bible)
```

```python
bible = list(filter(None, [item.strip('\n') for item in bible]))
bible[:5]
```

```python
len(bible)
```

```python
line_lengths = [len(sentence) for sentence in bible]
h = plt.hist(line_lengths)
```

```python
tokens = [item.split() for item in bible]
print(tokens[:5])
```

```python
total_tokens_per_line = [len(sentence.split()) for sentence in bible]
h = plt.hist(total_tokens_per_line, color='orange')
```

```python
words = [word for sentence in tokens for word in sentence]
print(words[:20])
```

```python
words = list(filter(None, [re.sub(r'[^A-Za-z]', '', word) for word in words]))
print(words[:20])
```

```python
from collections import Counter

words = [word.lower() for word in words]
c = Counter(words)
c.most_common(10)
```

```python
import nltk

stopwords = nltk.corpus.stopwords.words('english')
words = [word.lower() for word in words if word.lower() not in stopwords]
c = Counter(words)
c.most_common(10)
```
