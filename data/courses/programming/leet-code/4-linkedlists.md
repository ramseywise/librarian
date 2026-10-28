---
imported_hash: bd0440652bde0b3e
title: Definition for singly-linked list. Run to use for LL problems
summary: TBD.. - 19. remove nth node (medium) - 143.
order: 4
kind: notebook
source: learn-ai-engineering/programming/Leet-Code/4_LinkedLists.ipynb
---

## Linked Lists

        - 2.   add two numbers (medium)
        - 14.  longest common prefix (easy)
        - 21.  merge two linked list (easy)
        - 23.  merge k sorted list (hard)
        - 206. reverse linked list (easy)

        TBD..
        - 19.  remove nth node (medium)
        - 143. reorder list (medium)
        - 287. find duplicate (medium)

```python
# Definition for singly-linked list. Run to use for LL problems
class ListNode:
    def __init__(self, x):
        self.val = x
        self.next = None
```

### 2. Add two numbers

```python
def addTwoNumbers(l1, l2):
    """Add numbers from two lists."""
    num1 = int("".join(str(x) for x in l1.reverse()))
    num2 = int("".join(str(x) for x in l2.reverse()))
    tot = num1 + num2
    tot_str = list(str(tot))[::-1]
    return(list(map(int, tot_str)))

l1 = [2,4,3]
l2 = [5,6,4]

addTwoNumbers(l1, l2)
```

### 14: longest common prefix

```python
def longestCommonPrefix(strs):
    """Find the longest common prefix string amongst an array of strings."""
    if not strs: return "" # return empty str if not common prefix
    for i in range(len(strs[0])): # loop each character of first word in array
        char = strs[0][i]
        for j in range(1,len(strs)): # loop for each individul word in array
            if i == len(strs[j]) or strs[j][i] != char: # check if index of firat word matches following
                return strs[0][i]
    return strs[0]
```

```python
strs = ["flower","flow","flight"]
longestCommonPrefix(strs)
```

```python
l1.reverse()
l2.reverse()

s1 = [str(x) for x in l1]
res1 = int("".join(s1))

s2 = [str(x) for x in l2]
res2 = int("".join(s2))

ans = res1 + res2

ans1 = [int(x) for x in str(ans)]

ans1.reverse()
print(ans1)
```

## 21. Merge Two Lists

```python
class Solution:
    def mergeTwoLists(self, l1: ListNode, l2: ListNode) -> ListNode:
        """Merge the two lists in a one sorted list. The list should be made by splicing together the nodes of the first two lists.."""
        dummy = ListNode()
        tail = dummy

        while l1 and l2:
            if l1.val < l2.val:
                tail.next = l1
                l1 = l1.next
            else:
                tail.next = l2
                l2 = l2.next
            tail = tail.next

        if l1:
            tail.next = l1
        elif l2:
            tail.next = l2

        return dummy.next


list1 = [1,2,4]
list2 = [1,3,4]
```

## 23 Merge K Lists

```python
class Solution:
    def mergeKLists(self, lists: List[ListNode]) -> ListNode:
        """Merge all the linked-lists into one sorted linked-list and return it."""
        if not lists or len(lists) == 0:
            return None

        while len(lists) > 1:
            mergedLists = []
            for i in range(0, len(lists), 2):
                l1 = lists[i]
                l2 = lists[i + 1] if (i + 1) < len(lists) else None
                mergedLists.append(self.mergeList(l1, l2))
            lists = mergedLists
        return lists[0]

    def mergeList(self, l1, l2):
        dummy = ListNode()
        tail = dummy

        while l1 and l2:
            if l1.val < l2.val:
                tail.next = l1
                l1 = l1.next
            else:
                tail.next = l2
                l2 = l2.next
            tail = tail.next
        if l1:
            tail.next = l1
        if l2:
            tail.next = l2
        return dummy.next

lists = [[1,4,5],[1,3,4],[2,6]]
```

### 206. Reverse Linked List

```python
class Solution:
    def reverseList(self, head: ListNode) -> ListNode:
        prev, curr = None, head

        while curr:
            temp = curr.next
            curr.next = prev
            prev = curr
            curr = temp
        return prev
```

```python
def reverseLinkedList(head: ListNode) -> ListNode:
    """Given the head of a singly linked list, reverse the list, and return the reversed list."""
    prev, curr = None, head
    # TO(n) --> goes through one list
    # MO(1) --> only uses pointers
    while curr:
        temp = curr.next
        curr.next = prev
        prev = curr
        curr = temp
    return prev

head = [1,2,3,4,5]
reverseLinkedList(head)
```

```python
head.next
```

```python
class Solution(object):
    def reverseList(self, head):
        """
        :type head: ListNode
        :rtype: ListNode
        """
        prev, curr = None, head
        while curr:
            temp = curr.next
            curr.next = prev
            prev = curr
            curr = temp
        return prev

head = [1,2,3,4,5]
reverseList()
```

```python
        #TO(n) --> goes through one list
        # MO(1) --> only uses pointers
```
