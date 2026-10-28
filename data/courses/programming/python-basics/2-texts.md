---
imported_hash: 5a6a680762585ede
title: 2 | Working with Text Data Files
summary: 'This notebook covers specific text file topics: - Loading and writing text files - Parsing texts'
order: 2
kind: notebook
source: learn-ai-engineering/programming/Python Basics/2_Texts.ipynb
---

# 2 | Working with Text Data Files

This notebook covers specific text file topics:
- Loading and writing text files
- Parsing texts


Regular Expressions can be used in other programming languages as well to match and parse strings
   - `^`   Matches the beginning of a line
   - `$`   Matches the end of the line
   - `.`   Matches any character
   - `*`   Repeats a character zero or more times
   - `\s`    Matches whitespace
   - `\S`    Matches any non­whitespace character
   - `*?`    Repeats a character zero or more times (non­greedy) + Repeats a character one or more times
   - `+?`    Repeats a character one or more times(non­greedy) [aeiou] Matchesasinglecharacterinthelistedset [^XYZ] Matches a single character not in the listed set [a­z0­9] Thesetofcharacterscanincludearange
   - `( `   Indicates where string extraction is to start
   - `) `   Indicates where string extraction is to end


*Resources*:
- **Coursera Python for Informatics** (University of Michigan)

## Text Files and the Operating System

```python
cd /app/1-Basics/0-Functions
```

```python
ls
```

```python
# set path and open text with IO wrapper
#use open for large files rather than reading in a file with input()
path = 'Data/examples/segismundo.txt'
f = open(path)
f
```

```python
# strip lines from text
with open(path) as f:
    lines = [x.rstrip() for x in f]
lines
```

```python
# read first 10 char
f.read(10)
```

```python
f.tell()
```

```python
f2 = open(path, 'rb')  # Binary mode
f2.read(10)
```

```python
# remove encoding
data.decode('utf8')
```

```python
f.seek(3)
f.read(1)
```

```python
# open and write lines without space between lines
with open('data/tmp.txt', 'w') as handle:
    handle.writelines(x for x in open(path) if len(x) > 1)
with open('data/tmp.txt') as f:
    lines = f.readlines()
lines
```

```python
f.close()
f2.close()
```

### Text Parsing

```python
#use split to split items in a sequence
text="the clown ran after the car and the car ran into the tent and the tent fell down on the clown and the car"
words=text.split()
words
```

```python
#count word frequency with get()
counts=dict()
for word in words:
    counts[word]=counts.get(word,0)+1
counts
```

```python
# find most frequent word from text
bigcount = None
bigword = None
for word,count in counts.items():
    if bigcount is None or count > bigcount:
        bigword = word
        bigcount = count
print(bigword, bigcount)
```

```python
#split breaks a sequence into parts to create a list of strings
#items based by spaces but considers multiple spaces one split
#you can also split by defining parameter by semicolon, comma or dash etc.
s ='spam-spam-spam'
delimiter = '-'
s.split(delimiter)
```

```python
#import files from internet using requests
import requests
url = "http://www.py4inf.com/code/mbox-short.txt"
res = requests.get(url)
text = res.text
# get length of text characters
len(text)
```

```python
# have a look at the first 100 characters from text file
text[:100]
```

```python
lines=text.split('\n')
lines[:10]
```

```python
# count lines that start with From
count=0
for line in lines:
    line = line.rstrip()
    if line.startswith("From"):
        count=count+1
print("There were",count,"subject lines")
```

```python
#re.findall finds and retrieves a list
output = []
for line in lines:
    # strip text of trailing characters and lower case all words in text
    line = line.rstrip().lower()
    #remove punctuation
    line = re.sub('[!#?]', '', line)
    # return lines that begin with From
    if line.find('from'): continue
    split=line.split("@")
    # get unique domain names
    domain = split[1].split()
    output.append(domain[0])
print(set(output))
```

```python
# sort alphabetically
strings = list(set(output))
strings.sort(key=lambda x: len(set(list(x))))
strings
```
