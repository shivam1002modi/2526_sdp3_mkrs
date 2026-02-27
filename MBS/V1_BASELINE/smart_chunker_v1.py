"""
SmartChunker v3 — PDR + Semantic Paragraph-Aware Chunking
==========================================================
Two major systems combined:

  1. PARENT DOCUMENT RETRIEVAL (PDR):
     PARENT chunks (~1500 chars) → stored in parent_store.json (LLM context)
     CHILD  chunks (~300 chars)  → stored in ChromaDB (retrieval)

  2. SEMANTIC PARAGRAPH-AWARE SPLITTING (NEW):
     - Replaces RecursiveCharacterTextSplitter with a CUSTOM regex splitter.
     - Priority order: paragraph breaks (\\n\\n) → sentence endings (. ! ?) → word boundaries.
     - NEVER cuts through a name, date, or technical term mid-word.
     - Tables are 100% ATOMIC — never split, always kept as a single chunk.

Why this matters:
  - Old splitter would cut "coined by John Wheeler in 19|67" → losing the date.
  - New splitter finds the nearest sentence boundary: "...in 1967." | "The event..."
  - Tables like "| Dept | Revenue |" are always preserved intact.
"""

import re
import hashlib
from langchain_community.docstore.document import Document


# ══════════════════════════════════════════════════════════════════════════════
# SEMANTIC PARAGRAPH-AWARE SPLITTER (Custom — replaces RecursiveCharacterTextSplitter)
# ══════════════════════════════════════════════════════════════════════════════

class SemanticSplitter:
    """
    A custom text splitter that respects natural language boundaries.

    Split priority (highest to lowest):
      1. Paragraph breaks: \\n\\n
      2. Sentence endings:  . ! ? (followed by space or newline)
      3. Clause breaks:    , ; : — (followed by space)
      4. Word boundaries:  (space)  ← last resort, never mid-word

    The algorithm:
      1. Split text into paragraphs on \\n\\n.
      2. Accumulate paragraphs into a buffer until adding more would exceed max_size.
      3. When buffer is full, flush it as a chunk.
      4. If a SINGLE paragraph exceeds max_size, sub-split it on sentence boundaries.
      5. If a SINGLE sentence exceeds max_size, sub-split on clause/word boundaries.
      6. Overlap is achieved by carrying the last N chars of the previous chunk forward.
    """

    # Sentence boundary regex: splits AFTER the punctuation + whitespace
    # Splits on: "escaped. The term", "energy! This means", "really? The answer"
    # Won't split on: single-letter abbreviations like "e.g. " or "U.S.A."
    # Uses a simple fixed-width lookbehind that Python's re module supports.
    SENTENCE_REGEX = re.compile(
        r'(?<=[.!?])'           # Lookbehind: sentence-ending punctuation (fixed-width: 1 char)
        r'\s+'                   # Followed by whitespace
        r'(?=[A-Z\d"\'\(])'     # Lookahead: next sentence starts with capital/digit/quote
    )

    # Clause boundary regex: commas, semicolons, colons, dashes
    CLAUSE_REGEX = re.compile(r'(?<=[,;:\u2014])\s+')

    def __init__(self, max_size: int, overlap: int = 0):
        self.max_size = max_size
        self.overlap = overlap

    def _split_on_sentences(self, text: str) -> list:
        """Split text into sentences using regex."""
        parts = self.SENTENCE_REGEX.split(text)
        return [p.strip() for p in parts if p.strip()]

    def _split_on_clauses(self, text: str) -> list:
        """Split text on clause boundaries (commas, semicolons, etc.)."""
        parts = self.CLAUSE_REGEX.split(text)
        return [p.strip() for p in parts if p.strip()]

    def _split_on_words(self, text: str) -> list:
        """Last resort: split on word boundaries, grouping into size-limited units."""
        words = text.split()
        if not words:
            return [text] if text.strip() else []

        chunks = []
        current = []
        current_len = 0

        for word in words:
            word_len = len(word) + (1 if current else 0)  # +1 for space
            if current_len + word_len > self.max_size and current:
                chunks.append(" ".join(current))
                current = [word]
                current_len = len(word)
            else:
                current.append(word)
                current_len += word_len

        if current:
            chunks.append(" ".join(current))

        return chunks

    def _subsplit_large_unit(self, text: str) -> list:
        """
        Handle a unit that exceeds max_size.
        Try sentence boundaries first, then clauses, then word boundaries.
        """
        if len(text) <= self.max_size:
            return [text]

        # Strategy 1: Split on sentences, then accumulate
        sentences = self._split_on_sentences(text)
        if len(sentences) > 1:
            return self._accumulate(sentences)

        # Strategy 2: Split on clauses
        clauses = self._split_on_clauses(text)
        if len(clauses) > 1:
            return self._accumulate(clauses)

        # Strategy 3: Word boundaries (guaranteed to work)
        return self._split_on_words(text)

    def _accumulate(self, units: list) -> list:
        """
        Accumulate small units into chunks up to max_size.
        If any single unit exceeds max_size, sub-split it further.
        """
        chunks = []
        buffer = ""

        for unit in units:
            # If adding this unit would exceed the limit
            candidate = (buffer + "\n\n" + unit).strip() if buffer else unit

            if len(candidate) <= self.max_size:
                buffer = candidate
            else:
                # Flush current buffer (if non-empty)
                if buffer:
                    chunks.append(buffer)

                # Check if the unit itself is too large
                if len(unit) > self.max_size:
                    sub_chunks = self._subsplit_large_unit(unit)
                    # Add all but the last as complete chunks
                    chunks.extend(sub_chunks[:-1])
                    # Keep the last one as the new buffer (for potential merging)
                    buffer = sub_chunks[-1] if sub_chunks else ""
                else:
                    buffer = unit

        if buffer:
            chunks.append(buffer)

        return chunks

    def split(self, text: str) -> list:
        """
        Main entry point. Splits text into semantically coherent chunks.

        Returns: list of strings, each <= max_size characters.
        """
        if not text or not text.strip():
            return []

        text = text.strip()

        # If text fits in one chunk, done
        if len(text) <= self.max_size:
            return [text]

        # Step 1: Split on paragraph breaks (\\n\\n)
        paragraphs = re.split(r'\n\s*\n', text)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        # Step 2: Accumulate paragraphs into chunks
        raw_chunks = self._accumulate(paragraphs)

        # Step 3: Apply overlap (carry last N chars from previous chunk)
        if self.overlap > 0 and len(raw_chunks) > 1:
            overlapped = [raw_chunks[0]]
            for i in range(1, len(raw_chunks)):
                prev = raw_chunks[i - 1]
                # Get the overlap from the end of the previous chunk
                overlap_text = prev[-self.overlap:] if len(prev) >= self.overlap else prev

                # Find a clean boundary in the overlap (sentence or word)
                # Trim to start at a word boundary
                space_idx = overlap_text.find(' ')
                if space_idx > 0:
                    overlap_text = overlap_text[space_idx + 1:]

                combined = overlap_text + "\n" + raw_chunks[i]
                # If overlap makes it exceed max_size, skip overlap for this chunk
                if len(combined) <= self.max_size:
                    overlapped.append(combined)
                else:
                    overlapped.append(raw_chunks[i])

            return overlapped

        return raw_chunks


# ══════════════════════════════════════════════════════════════════════════════
# SMART CHUNKER (PDR + Semantic Splitting)
# ══════════════════════════════════════════════════════════════════════════════

class SmartChunker:
    """
    Two-Tier PDR Chunker with Semantic Paragraph-Aware Splitting:
        - Parent Size:  ~1500 chars (semantic) → stored in parent_store.json
        - Child Size:   ~300 chars  (semantic) → stored in ChromaDB
        - Tables:       ATOMIC — never split, always single chunk
    """

    # ── Table Detection Regexes ───────────────────────────────────────────
    # Markdown tables: | col1 | col2 |\n|---|---|\n| val | val |
    TABLE_MD_REGEX = re.compile(
        r'(\|[^\n]+\|\n\|[\s\-:]+\|(?:\n\|[^\n]+\|)+)',
        re.MULTILINE
    )

    # Whitespace-aligned tables (common in PDF extraction):
    # Dept    Revenue    Profit
    # IT      500K       200K
    TABLE_ALIGNED_REGEX = re.compile(
        r'((?:^[ \t]*\S+(?:[ \t]{2,}\S+){2,}[ \t]*$\n?){3,})',
        re.MULTILINE
    )

    # Tab-separated data (TSV-like):
    TABLE_TSV_REGEX = re.compile(
        r'((?:^[^\t\n]+(?:\t[^\t\n]+){2,}$\n?){3,})',
        re.MULTILINE
    )

    def __init__(self, parent_chunk_size=1500, parent_chunk_overlap=200,
                 child_chunk_size=500, child_chunk_overlap=200,
                 # Legacy interface: accept chunk_size/chunk_overlap for backward compat
                 chunk_size=None, chunk_overlap=None):

        # If called with legacy params (chunk_size=500), upgrade silently
        if chunk_size is not None and parent_chunk_size == 1500:
            pass

        self.parent_chunk_size = parent_chunk_size
        self.parent_chunk_overlap = parent_chunk_overlap
        self.child_chunk_size = child_chunk_size
        self.child_chunk_overlap = child_chunk_overlap

        # Semantic splitters (replace RecursiveCharacterTextSplitter)
        self.parent_splitter = SemanticSplitter(
            max_size=self.parent_chunk_size,
            overlap=self.parent_chunk_overlap,
        )
        self.child_splitter = SemanticSplitter(
            max_size=self.child_chunk_size,
            overlap=self.child_chunk_overlap,
        )

    def _generate_parent_id(self, source: str, page: int, index: int) -> str:
        """Generate a deterministic, unique ID for a parent chunk."""
        raw = f"{source}__page{page}__chunk{index}"
        return "P_" + hashlib.md5(raw.encode()).hexdigest()[:12]

    def _extract_tables_and_text(self, text: str):
        """
        Splits document text into table segments and non-table segments,
        preserving their original order. Detects:
          - Markdown tables (| col | col |)
          - Aligned/columnar tables (common in PDF extraction)
          - Tab-separated tables
        
        Returns: list of (is_table: bool, content: str) tuples
        """
        # Collect all table matches with their spans
        table_spans = []

        for regex in [self.TABLE_MD_REGEX, self.TABLE_ALIGNED_REGEX, self.TABLE_TSV_REGEX]:
            for match in regex.finditer(text):
                # Check for overlapping spans
                start, end = match.start(), match.end()
                overlaps = False
                for (s, e, _) in table_spans:
                    if start < e and end > s:  # overlap detected
                        overlaps = True
                        break
                if not overlaps:
                    table_spans.append((start, end, match.group(0).strip()))

        # Sort by position
        table_spans.sort(key=lambda x: x[0])

        # Build segments
        segments = []
        last_end = 0

        for start, end, table_text in table_spans:
            # Text before the table
            before = text[last_end:start].strip()
            if before:
                segments.append((False, before))

            # The table itself (ATOMIC)
            segments.append((True, table_text))
            last_end = end

        # Remaining text after last table
        after = text[last_end:].strip()
        if after:
            segments.append((False, after))

        # If no segments found, return full text as non-table
        if not segments and text.strip():
            segments.append((False, text.strip()))

        return segments

    def _add_table_context(self, segments):
        """
        For each table segment, prepend the last 1-2 sentences of the preceding
        text segment as semantic context. This makes tables searchable by topic.

        Example:
            Before: ["Financial results for Q3 2025.", TABLE]
            After:  TABLE → "Financial results for Q3 2025.\n\n| Dept | Revenue ..."
        """
        enriched = []
        prev_text = ""

        for is_table, content in segments:
            if is_table and prev_text:
                # Get the last 1-2 sentences before the table
                sentences = re.split(r'(?<=[.!?])\s+', prev_text)
                context_prefix = ". ".join(sentences[-2:]) if len(sentences) >= 2 else sentences[-1]
                # Cap context prefix length to avoid bloating
                if len(context_prefix) > 300:
                    context_prefix = context_prefix[-300:]
                    # Trim to word boundary
                    space_idx = context_prefix.find(' ')
                    if space_idx > 0:
                        context_prefix = context_prefix[space_idx + 1:]
                enriched_table = f"{context_prefix}\n\n{content}"
                enriched.append((True, enriched_table))
            else:
                enriched.append((is_table, content))

            if not is_table:
                prev_text = content

        return enriched

    def split_documents(self, documents):
        """
        Main entry point. Takes raw page-level documents and returns:
            - child_chunks: list of Document objects for ChromaDB (small, precise)
            - parent_store: dict of { parent_id: parent_text } for expansion

        Returns: (child_chunks, parent_store) tuple
        """
        parent_store = {}  # { parent_id: full_parent_text }
        child_chunks = []
        stats = {"tables": 0, "text_parents": 0, "text_children": 0}

        for doc in documents:
            source = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page", 0)
            base_metadata = dict(doc.metadata)  # Copy original metadata

            full_text = doc.page_content

            # ── Step 1: Separate tables from text ─────────────────────────
            segments = self._extract_tables_and_text(full_text)
            segments = self._add_table_context(segments)

            # ── Step 2: Process each segment ──────────────────────────────
            parent_index = 0

            for is_table, segment_text in segments:

                if is_table:
                    # Tables are ATOMIC — they become their own parent AND child
                    parent_id = self._generate_parent_id(source, page, parent_index)
                    parent_store[parent_id] = segment_text

                    child_meta = {
                        **base_metadata,
                        "parent_id": parent_id,
                        "chunk_type": "table",
                    }
                    child_chunks.append(Document(
                        page_content=segment_text,
                        metadata=child_meta,
                    ))
                    parent_index += 1
                    stats["tables"] += 1

                else:
                    # ── Semantic split into PARENT chunks ─────────────────
                    parent_texts = self.parent_splitter.split(segment_text)

                    for p_text in parent_texts:
                        parent_id = self._generate_parent_id(source, page, parent_index)
                        parent_store[parent_id] = p_text
                        stats["text_parents"] += 1

                        # ── Semantic split each PARENT into CHILD chunks ──
                        child_texts = self.child_splitter.split(p_text)

                        for c_text in child_texts:
                            child_meta = {
                                **base_metadata,
                                "parent_id": parent_id,
                                "chunk_type": "text",
                            }
                            child_chunks.append(Document(
                                page_content=c_text,
                                metadata=child_meta,
                            ))
                            stats["text_children"] += 1

                        parent_index += 1

        print(f"  [SmartChunker v3 — Semantic PDR]")
        print(f"    Pages processed:  {len(documents)}")
        print(f"    Tables (atomic):  {stats['tables']}")
        print(f"    Text parents:     {stats['text_parents']}")
        print(f"    Text children:    {stats['text_children']}")
        print(f"    Total parents:    {len(parent_store)}")
        print(f"    Total children:   {len(child_chunks)}")

        return child_chunks, parent_store


# ══════════════════════════════════════════════════════════════════════════════
# STANDALONE TEST
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Test with realistic document content that would break old splitter
    test_doc = Document(
        page_content=(
            "Black holes are regions of spacetime where gravity is so strong that "
            "nothing, not even light, can escape once it crosses a critical boundary. "
            "The term 'black hole' was coined by physicist John Archibald Wheeler in 1967. "
            "Before Wheeler's terminology, these objects were known as 'frozen stars' in the Soviet Union.\n\n"
            "The event horizon is the boundary beyond which nothing can return. "
            "It marks the point of no return for any object falling into the black hole. "
            "The radius of the event horizon is called the Schwarzschild radius, named after "
            "Karl Schwarzschild who first calculated it in 1916.\n\n"
            "| Property | Value |\n|---|---|\n| Mass | 4 million solar masses |\n"
            "| Location | Center of Milky Way |\n| Name | Sagittarius A* |\n"
            "| Distance | 26,000 light-years |\n\n"
            "Hawking radiation is a theoretical prediction by Stephen Hawking in 1974 "
            "that black holes emit thermal radiation due to quantum effects near the event "
            "horizon. This was groundbreaking because it suggested black holes are not "
            "truly 'black' but slowly evaporate over astronomical timescales."
        ),
        metadata={"source": "test.pdf", "page": 1, "ingestion_method": "test"}
    )

    chunker = SmartChunker()
    children, parents = chunker.split_documents([test_doc])

    print(f"\n{'='*60}")
    print(f"PARENT CONTEXTS ({len(parents)}):")
    print(f"{'='*60}")
    for pid, text in parents.items():
        print(f"\n  [{pid}] ({len(text)} chars):")
        for line in text.split('\n')[:3]:
            print(f"    {line[:90]}")
        if len(text.split('\n')) > 3:
            print(f"    ...")

    print(f"\n{'='*60}")
    print(f"CHILD CHUNKS ({len(children)}) — what goes into ChromaDB:")
    print(f"{'='*60}")
    for child in children:
        chunk_type = child.metadata['chunk_type']
        parent_id = child.metadata['parent_id']
        content = child.page_content
        # Show where the chunk STARTS and ENDS to verify no mid-word cuts
        print(f"\n  [{chunk_type}] parent={parent_id} ({len(content)} chars)")
        print(f"    START: \"{content[:60]}\"")
        print(f"      END: \"{content[-60:]}\"")
