# Hierarchical Chunking

Extract the content from an image page and output in Markdown syntax. Enclose the content in the `<markdown></markdown>` tag and do not use code blocks.

1. Examine the provided page carefully.
2. Identify all elements: headers, body text, tables, etc.
3. Use markdown syntax: # for main, ## for sections.
4. **Crucial:** Ensure that steps (e.g., "Trin 1", "Trin 2") remain logically connected to their respective headings so they are not separated during chunking.
5. If the element is a table: Create a clean markdown table. If a cell has multiple items, list them in separate rows within the cell to maintain readability.

# Semantic Chunking

**Focus on capturing the instructional flow. Keep troubleshooting steps, warnings, and their immediate context grouped together. Ensure that all UI elements mentioned (buttons, menus) are clearly associated with their actions.**

Extract the content from the page and output in Markdown syntax. Enclose the content in the `<markdown></markdown>` tag and do not use code blocks.

1. Examine the provided page carefully.
2. Identify all elements: headers, body text, tables, and instructional lists.
3. Use markdown syntax: # for the main article title, ## for sub-steps or sections.
4. **Special Handling for Support:** If a paragraph explains "Why" and the following list explains "How", ensure they are formatted to appear as a single logical block to assist semantic grouping.
5. **Tables:** Convert any comparison tables or pricing into clean markdown tables.
6. **Screenshots:** If a screenshot is present, describe the UI action it represents (e.g., "Screenshot showing where to find the 'Delete' button") inside `<figure></figure>` tags.
7. Exclude repetitive footer elements like "Was this article helpful?" to keep chunks clean.
