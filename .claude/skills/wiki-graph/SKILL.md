---
name: wiki-graph
description: "Show the shape of the wiki's link graph: hubs, bridges, cut points and consensus clusters, with each cluster named and what the numbers mean, under one page. Read-only. Use when asked what the wiki is actually about, which pages hold it together, how the clusters compare with the directories, or where a topic has split. Do NOT use for page health such as orphans and dead links (/lint), merging or retiring pages (/compact-wiki), finding what the wiki lacks (/gaps), or the weekly review (/wiki-weekly)."
allowed-tools:
  - Read
  - Bash(uv run python core/wiki_graph.py)
  - Bash(uv run python core/wiki_graph.py --json)
---

You are reading the wiki's link graph for Ramsey. The script decides every number; you name the clusters and say what the numbers mean.

## Core rule

Every number comes from the script's output, and a cluster name is written at read time and never stored.

## Workflow

`$ARGUMENTS` is ignored.

1. **Run the script.**
   ```bash
   uv run python core/wiki_graph.py
   ```
   If it fails, print the failure and stop. Write no numbers by hand.

2. **Check stability.** If it is below 0.9, say so first and report hubs and bridges only: the clusters are not settled enough to name.

3. **Name each cluster** from its top pages, its tags and its directory mix. Read a page when its title leaves the subject unclear. Cluster numbers move between runs, so never write a name or a number into a tracked file.

4. **Read the top bridge** before describing it. An overview page can score high simply by listing everything, and that is a different finding from a page that truly joins two topics.

5. **Print the report.** Fixes go to `/compact-wiki` or a normal edit, and page health goes to `/lint`. This skill changes nothing.

## Output format

```
Pages: <n>  Links: <n>  Stability: <0.000>
Cut points: <n> pages, <n> links

Clusters: <n>, plus <n> unsettled pages
1. <name you gave it>: <n> pages, mostly <directory>

Top hub: <page>, <n> links, spans <n> clusters
Top bridge: <page>, <0.000>: <what it actually does, from reading it>

Directories that split: <directory> (<n> clusters: <names>)
Clusters with no majority directory: <names | none>

Worth a look: <at most three things, each naming a page or cluster>
```

## Calibration

Reading clusters as subjects is the optimistic failure. Claude wrote most of these links, often many in one sitting from one source, so a cluster can be the trace of one ingest batch. If a cluster's top pages share a source rather than a subject, say so.

Reading a split directory as a filing mistake is the opposite failure. `data/wiki/` directories are the canonical domains, and a report never argues for moving pages by itself: it gives Ramsey something to look at.
