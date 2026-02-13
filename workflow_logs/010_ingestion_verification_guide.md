# Ingestion Engine Upgrade: Verification Guide

## 1. Summary of Upgrades
We have transformed the ingestion engine from a "Text dumper" to a "Structure-aware Reader".

| Feature | Before (Level-0) | After (SmartLoader V3) |
| :--- | :--- | :--- |
| **Engine** | `pypdf` (Stream-based) | `pdfplumber` (Coordinate-based) |
| **Strategy** | Read left-to-right blindly | Respect physical layout (x,y coords) |
| **Tables** | Flattened into meaningless text | Converted to **Markdown Grids** |
| **Headers/Footers**| Polluted every chunk | **Statistically Filtered** (Global pass) |
| **Duplication** | Tables read twice (as text + garbage) | **Masked** (Text extractor skips tables) |
| **Scans** | Silent failure (empty docs) | **Detection** (Logs warning for empty pages) |

## 2. Extreme Edge Cases Now Handled

### Case A: The "Newspaper Column" Problem
*   **Scenario**: Text flows down Column 1, then jumps to top of Column 2.
*   **Before**: The bot would read Line 1 Col 1, then Line 1 Col 2, merging two unrelated sentences. ("The president said... apple pie recipes")
*   **Now**: `layout=True` clusters text by physical proximity, reading Column 1 fully before moving to Column 2.

### Case B: The "Data Grid" Problem
*   **Scenario**: A table with "Name" | "Price".
*   **Before**: "Name Price Apple $5 Banana $2" -> LLM gets confused about which price belongs to what.
*   **Now**:
    ```markdown
    | Name | Price |
    | --- | --- |
    | Apple | $5 |
    | Banana | $2 |
    ```
    The LLM perfectly understands the relationship.

### Case C: The "Confidential Footer" Pollution
*   **Scenario**: Every page ends with "CONFIDENTIAL - DO NOT DISTRIBUTE".
*   **Before**: Every single search result included "CONFIDENTIAL", confusing the semantic similarity search.
*   **Now**: The engine sees this text appears on >60% of pages and **deletes it** before the AI ever sees it.

## 3. How to Test (The "Killer PDF" Prompt)
Use this prompt with an LLM (like ChatGPT/Gemini) to generate a test document. Then "Print to PDF" and ingest it to see the magic.

### 🧪 Prompt for Generating Test Data
> "Create a complex technical 'Dummy Report' in Markdown/HTML format that I can print to PDF. It must specifically stress-test a PDF ingestion engine. Include the following elements:
>
> 1.  **Multi-Column Layout**: Create a section with two narrow columns of text where reading line-by-line would ruin the meaning (e.g., Column 1 is a story, Column 2 is a recipe).
> 2.  **Complex Table**: A financial table with 4 columns (Item, Q1, Q2, Q3) and 5 rows. Ensure it has headers.
> 3.  **Repetitive Artifacts**: Add a consistent 'Header: Project Alpha' and 'Footer: Page X of Y' on every simulated page.
> 4.  **Mixed Content**: A paragraph of text that refers to the table below it, to test context preservation.
> 5.  **Structure**: Clear H1/H2 headers and bullet points.
>
> The goal is to verify that my ingestion engine correctly:
> *   Reads columns vertically (not merging lines).
> *   Formats the table as a grid.
> *   Removes the repetitive header/footer."
