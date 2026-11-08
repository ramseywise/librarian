# Raw source formats

Moved from CLAUDE.md. Frontmatter formats for the book and article subdirectories of `data/raw/`.

#### Book source format (`data/raw/books/<author-title.md>`)

```markdown
---
source_type: book
title: "Title of the Book"
author: "Author Name"
year: YYYY
---

## Chapter N — Chapter Title

> "Exact quote that is relevant to agent design or engineering."

**Note:** Why this quote matters for your work — connect it to a pattern, decision, or technique.

> "Another relevant quote."

**Note:** Application or implication.
```

#### Article source format (`data/raw/articles/<YYYY-MM-DD-slug.md>`)

```markdown
---
source_type: article
title: "Article Title"
author: "Author Name"
url: https://...
published: YYYY-MM-DD
---

> "Key quote from the article."

**Note:** Why this is relevant.
```
