---
imported_hash: 565ac2f96364354c
title: Knowledge Graph Fundamentals
summary: ''
order: 12
kind: reading
section: Notebooks / Knowledge graphs for rag / Notes
source: learn-ai-engineering/ai-engineering/05-graph-engineering/notebooks/knowledge-graphs-for-rag/notes/Lesson_1.md
---

# Knowledge Graph Fundamentals

- Relationships *contain* two nodes
- Example
  - (PERSON)-[KNOWS]-(PERSON)
- The nodes are "in" a relationship, which itself has properties.
- In OO-perspective or even relational model, the entity would "know" each other with direct references or foreign keys.
- **Graph types are composable!**
- ![Knowledge Graph example](../../../assets/notebooks/knowledge-graphs-for-rag/images/1_0.png)
- Formally
  - Nodes have labels which is used for grouping.
  - Nodes are data record with key/value properties.
    ![Nodes](../../../assets/notebooks/knowledge-graphs-for-rag/images/1_1.png)
  - Relationships are also data records which have a direction, a type, and properties.
    ![Relationships](../../../assets/notebooks/knowledge-graphs-for-rag/images/1_2.png)
    - Type: KNOWS, TEACHES, INTRODUCES
    - Property: Mentioned below the Type for each relationship.

## What is a Knowledge Graph?

- Knowledge Graph: A database that stores information in **nodes** and **relationships**.
- Both nodes and relationships can have **properties**.
- Nodes can be given **labels** to group them together.
- Relationships always have a **type** and a **direction**.
