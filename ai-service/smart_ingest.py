import os
import re
import logging
import pdfplumber
import numpy as np
from langchain_community.docstore.document import Document
from collections import Counter

# ══════════════════════════════════════════════════════════════════════════════
# LOGGING SETUP — persistent file + console
# ══════════════════════════════════════════════════════════════════════════════
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "smart_ingest.log")

logger = logging.getLogger("SmartIngest")
logger.setLevel(logging.DEBUG)

# File handler — full detail
if not logger.handlers:
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8", mode="a")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-5s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(fh)

    # Console handler — summary only
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("  [SmartIngest] %(message)s"))
    logger.addHandler(ch)


class SmartIngest:
    """
    Column-Aware PDF Ingestion Engine (V10)
    ========================================
    Algorithm:
        1. Global header/footer artifact detection via statistical analysis.
        2. Per-page processing:
            a. Table Masking  — Extract tables as Markdown, mask their regions.
            b. Y-Band Segmentation — Split words into horizontal bands by vertical gaps.
            c. Per-Band Column Detection — X-histogram gap analysis per band.
            d. Per-Column Reading — Read each column top-to-bottom independently.
        3. Artifact filtering & final assembly.

    Key Improvement (V10 vs V9):
        V9 sorted ALL words by (Y-band, X) which interleaves columns.
        V10 segments into Y-bands FIRST, detects columns PER BAND,
        then reads each column independently within each band.

    Why per-band matters:
        Full-width headers/titles fill the center gap in the global X-histogram,
        masking the column boundary. Per-band detection isolates the multi-column
        regions and correctly identifies their column gaps.
    """

    # ── Tunable Constants ─────────────────────────────────────────────────
    LINE_HEIGHT_PX     = 3    # Y-tolerance for grouping words into same line
    COLUMN_GAP_MIN_PX  = 15   # Minimum gap in X-histogram to declare a column split
    BAND_GAP_PX        = 12   # Minimum vertical gap (px) to split Y-bands
    HEADER_FONT_RATIO  = 1.3  # Font size ratio to consider text a section header

    def __init__(self, file_path):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)

    def load(self):
        """
        Column-Aware V10 Ingestion:
        1. Global Header/Footer Statistical Analysis.
        2. Per-Page:
            a. Table Masking (Markdown Extraction).
            b. Y-Band Segmentation (vertical gap detection).
            c. Per-Band Column Detection via X-Histogram.
            d. Per-Column Top-to-Bottom Reading.
        3. Artifact Filtering & Assembly.
        """
        logger.info("=" * 60)
        logger.info(f"INGESTING: {self.filename}")
        logger.info("=" * 60)
        documents = []

        try:
            with pdfplumber.open(self.file_path) as pdf:
                if not pdf.pages:
                    logger.warning("PDF has no pages!")
                    return []

                total_pages = len(pdf.pages)
                logger.info(f"PDF has {total_pages} pages")

                # 1. Global Artifact Analysis
                artifacts = self._analyze_artifacts(pdf)
                if artifacts:
                    logger.info(f"Artifacts to remove: {list(artifacts)}")

                for i, page in enumerate(pdf.pages):
                    page_num = i + 1
                    if not page.chars:
                        logger.debug(f"Page {page_num}: No chars, skipping")
                        continue

                    width, height = page.width, page.height
                    logger.info(f"--- Page {page_num}/{total_pages} ({width:.0f}x{height:.0f}) ---")

                    # ── Step A: Table Masking ─────────────────────────────
                    tables = page.find_tables()
                    table_bboxes = [t.bbox for t in tables]
                    logger.debug(f"Page {page_num}: Found {len(tables)} tables")

                    layout_items = []  # List of (y_position, text)

                    # Extract Tables as Markdown
                    extracted_tables = page.extract_tables()
                    for t_idx, table in enumerate(extracted_tables):
                        if not table:
                            continue
                        clean_rows = [
                            [str(cell or "").replace("\n", " ") for cell in row]
                            for row in table
                        ]
                        header = "| " + " | ".join(clean_rows[0]) + " |"
                        sep = "| " + " | ".join(["---"] * len(clean_rows[0])) + " |"
                        body = "\n".join(
                            ["| " + " | ".join(row) + " |" for row in clean_rows[1:]]
                        )
                        md_table = f"\n\n{header}\n{sep}\n{body}\n\n"
                        y_pos = table_bboxes[t_idx][1] if t_idx < len(table_bboxes) else 0
                        layout_items.append((y_pos, md_table))
                        logger.debug(f"Page {page_num}: Table at y={y_pos:.0f}")

                    # ── Step B: Extract Text NOT in tables ────────────────
                    def not_in_tables(obj):
                        cx = (obj["x0"] + obj["x1"]) / 2
                        cy = (obj["top"] + obj["bottom"]) / 2
                        for box in table_bboxes:
                            if box[0] <= cx <= box[2] and box[1] <= cy <= box[3]:
                                return False
                        return True

                    text_layer = page.filter(not_in_tables)
                    words = text_layer.extract_words(
                        extra_attrs=["size"],
                        keep_blank_chars=False,
                    )

                    if not words:
                        logger.debug(f"Page {page_num}: No text words outside tables")
                        if layout_items:
                            pass  # Still process tables
                        else:
                            continue

                    if words:
                        logger.debug(f"Page {page_num}: {len(words)} words outside tables")

                        # ── Step C: Y-Band Segmentation ──────────────────
                        bands = self._segment_y_bands(words, height)
                        logger.info(
                            f"Page {page_num}: Segmented into {len(bands)} Y-band(s)"
                        )

                        # ── Step D: Per-Band Column Detection & Reading ──
                        for band_idx, (band_start, band_end) in enumerate(bands):
                            band_words = [
                                w for w in words
                                if w['top'] >= band_start and w['bottom'] <= band_end + 5
                            ]
                            if not band_words:
                                continue

                            logger.debug(
                                f"Page {page_num}: Band {band_idx} "
                                f"(y={band_start:.0f}-{band_end:.0f}) "
                                f"has {len(band_words)} words"
                            )

                            # Detect columns within THIS band
                            columns = self._detect_columns_in_band(
                                band_words, width, band_start, band_end, page_num
                            )

                            # Read each column independently, top-to-bottom
                            # KEY: When multiple columns exist, we offset Y for
                            # later columns so they sort AFTER earlier columns.
                            # Without this, both columns share the same Y range
                            # and lines would interleave when sorted by Y.
                            is_multi_col = len(columns) > 1
                            for col_idx, col_words in enumerate(columns):
                                col_label = chr(65 + col_idx)
                                lines = self._words_to_lines(col_words)
                                logger.debug(
                                    f"  Column {col_label}: {len(lines)} lines"
                                )

                                # For multi-column: offset Y so Col B comes after Col A
                                # Use band boundary to calculate offset
                                if is_multi_col:
                                    band_height = band_end - band_start
                                    y_offset = col_idx * (band_height + 1)
                                else:
                                    y_offset = 0

                                for y, text in lines:
                                    layout_items.append((y + y_offset, text))

                    # ── Step E: Sort by Y Position & Filter ───────────────
                    layout_items.sort(key=lambda x: x[0])

                    final_lines = []
                    for y, line in layout_items:
                        line = line.strip()
                        if not line:
                            continue
                        # Remove artifacts
                        if artifacts and line in artifacts:
                            logger.debug(f"Page {page_num}: Artifact removed: '{line[:50]}'")
                            continue
                        # Remove page numbers and doc numbers
                        if re.match(r'^(Page\s+\d+|^\d+$|DOC NO:.*)', line, re.I):
                            continue
                        final_lines.append(line)

                    final_text = "\n".join(final_lines)
                    # Clean non-ASCII (keep Devanagari)
                    final_text = re.sub(r'[^\x00-\x7F\u0900-\u097F\n]+', ' ', final_text)
                    final_text = re.sub(r'[ \t]+', ' ', final_text).strip()

                    if not final_text:
                        continue

                    logger.info(
                        f"Page {page_num}: Final text = {len(final_text)} chars"
                    )
                    logger.debug(
                        f"Page {page_num}: Preview: '{final_text[:300]}...'"
                    )

                    meta = {
                        "source": self.filename,
                        "page": page_num,
                        "ingestion_method": "ColumnAware_V10",
                    }
                    documents.append(
                        Document(page_content=final_text, metadata=meta)
                    )

        except Exception as e:
            logger.error(f"FATAL: Ingestion failed on {self.filename}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []

        logger.info(f"DONE: {self.filename} -> {len(documents)} page documents")
        logger.info("=" * 60)
        return documents

    # ══════════════════════════════════════════════════════════════════════════
    # Y-BAND SEGMENTATION — Split page into horizontal bands by vertical gaps
    # ══════════════════════════════════════════════════════════════════════════
    def _segment_y_bands(self, words, page_height):
        """
        Find horizontal bands of content separated by vertical gaps.

        Algorithm:
            1. Build a Y-histogram marking occupied rows.
            2. Find continuous runs of empty rows > BAND_GAP_PX.
            3. Each run marks a band boundary.

        Returns: list of (y_start, y_end) tuples.
        """
        if not words:
            return []

        int_height = int(page_height) + 1
        y_hist = np.zeros(int_height, dtype=np.int32)
        for w in words:
            top = max(0, int(w['top']))
            bottom = min(int_height - 1, int(w['bottom']))
            y_hist[top:bottom] = 1

        # Find bands
        bands = []
        band_start = -1
        gap_size = 0

        for y in range(int_height):
            if y_hist[y] == 1:
                if band_start == -1:
                    band_start = y
                gap_size = 0
            else:
                if band_start != -1:
                    gap_size += 1
                    if gap_size > self.BAND_GAP_PX:
                        band_end = y - gap_size
                        bands.append((band_start, band_end))
                        band_start = -1
                        gap_size = 0

        # Final band
        if band_start != -1:
            bands.append((band_start, int_height))

        logger.debug(
            f"  Y-bands: {[(f'{s:.0f}-{e:.0f}') for s, e in bands]}"
        )
        return bands

    # ══════════════════════════════════════════════════════════════════════════
    # PER-BAND COLUMN DETECTION — X-Histogram Gap Analysis
    # ══════════════════════════════════════════════════════════════════════════
    def _detect_columns_in_band(self, band_words, page_width, band_y_start, band_y_end, page_num):
        """
        Detect columns within a specific Y-band using X-histogram gap analysis.

        This is the KEY fix: by analyzing columns PER BAND instead of globally,
        we avoid full-width headers masking the column gap.

        Algorithm:
            1. Build an X-histogram for ONLY this band's words.
            2. Scan for continuous gaps >= COLUMN_GAP_MIN_PX.
            3. Only consider gaps in the central 80% of the page.
            4. Split words into columns at each gap boundary.

        Returns: list of word-lists, one per detected column.
        """
        if not band_words:
            return [[]]

        # Build X-histogram for this band only
        int_width = int(page_width) + 1
        x_hist = np.zeros(int_width, dtype=np.int32)
        for w in band_words:
            x0 = max(0, int(w['x0']))
            x1 = min(int_width - 1, int(w['x1']))
            x_hist[x0:x1] += 1

        # Find all significant gaps (runs of zeros)
        gaps = []
        gap_start = None
        for x in range(int_width):
            if x_hist[x] == 0:
                if gap_start is None:
                    gap_start = x
            else:
                if gap_start is not None:
                    gap_len = x - gap_start
                    if gap_len >= self.COLUMN_GAP_MIN_PX:
                        gap_center = gap_start + gap_len // 2
                        # Only consider gaps in the central 80% of the page
                        margin = page_width * 0.1
                        if margin < gap_center < page_width - margin:
                            gaps.append((gap_start, x, gap_center))
                            logger.debug(
                                f"  Band y={band_y_start:.0f}-{band_y_end:.0f}: "
                                f"Column gap at x={gap_start}-{x} "
                                f"(width={gap_len}px)"
                            )
                    gap_start = None

        if not gaps:
            # Single column band
            logger.debug(
                f"  Band y={band_y_start:.0f}-{band_y_end:.0f}: single column"
            )
            return [band_words]

        # Sort gaps by position and create column boundaries
        gaps.sort(key=lambda g: g[0])
        boundaries = [0.0]
        for gap_start, gap_end, gap_center in gaps:
            boundaries.append(float(gap_center))
        boundaries.append(float(page_width))

        # Assign words to columns
        num_cols = len(boundaries) - 1
        columns = [[] for _ in range(num_cols)]

        for w in band_words:
            word_center_x = (w['x0'] + w['x1']) / 2.0
            assigned = False
            for col_idx in range(num_cols):
                left = boundaries[col_idx]
                right = boundaries[col_idx + 1]
                if left <= word_center_x < right:
                    columns[col_idx].append(w)
                    assigned = True
                    break
            if not assigned:
                columns[-1].append(w)

        # Remove empty columns
        columns = [col for col in columns if col]

        if len(columns) > 1:
            logger.info(
                f"  Band y={band_y_start:.0f}-{band_y_end:.0f}: "
                f"{len(columns)} COLUMNS detected! "
                f"(words: {[len(c) for c in columns]})"
            )
        return columns

    # ══════════════════════════════════════════════════════════════════════════
    # WORDS → LINES (per-column, top-to-bottom)
    # ══════════════════════════════════════════════════════════════════════════
    def _words_to_lines(self, words):
        """
        Reconstructs lines from a list of words, reading top-to-bottom.

        Groups words by Y-position (with tolerance), then sorts each group
        left-to-right to form a line.

        Returns: list of (y_position, line_text) tuples.
        """
        if not words:
            return []

        # Sort primarily by Y (top), secondarily by X (left)
        words.sort(key=lambda w: (w['top'], w['x0']))

        lines = []
        current_line_words = [words[0]]
        current_y = words[0]['top']

        for w in words[1:]:
            # Same line if Y is within tolerance
            y_delta = abs(w['top'] - current_y)
            if y_delta <= self.LINE_HEIGHT_PX * 2:
                current_line_words.append(w)
            else:
                # Flush current line
                current_line_words.sort(key=lambda ww: ww['x0'])
                line_text = " ".join([ww['text'] for ww in current_line_words])
                avg_y = sum(ww['top'] for ww in current_line_words) / len(current_line_words)
                lines.append((avg_y, line_text))

                # Start new line
                current_line_words = [w]
                current_y = w['top']

        # Flush last line
        if current_line_words:
            current_line_words.sort(key=lambda ww: ww['x0'])
            line_text = " ".join([ww['text'] for ww in current_line_words])
            avg_y = sum(ww['top'] for ww in current_line_words) / len(current_line_words)
            lines.append((avg_y, line_text))

        return lines

    # ══════════════════════════════════════════════════════════════════════════
    # ARTIFACT DETECTION (Headers/Footers that repeat across pages)
    # ══════════════════════════════════════════════════════════════════════════
    def _analyze_artifacts(self, pdf):
        """
        Detects repeating headers/footers across pages.

        For short PDFs (<=3 pages), artifact detection is disabled to avoid
        accidentally removing legitimate content.
        """
        candidates = []
        for page in pdf.pages:
            h = page.height
            header = page.crop((0, 0, page.width, h * 0.1)).extract_text()
            footer = page.crop((0, h * 0.9, page.width, h)).extract_text()
            if header:
                candidates.append(header.strip())
            if footer:
                candidates.append(footer.strip())

        counts = Counter(candidates)

        # For short PDFs (<=3 pages), artifact detection is too risky.
        if len(pdf.pages) <= 3:
            logger.debug("Short PDF (<=3 pages): skipping artifact detection")
            return set()

        threshold = len(pdf.pages) * 0.6
        artifacts = {txt for txt, count in counts.items() if count > threshold}
        if artifacts:
            logger.info(f"Detected {len(artifacts)} repeating artifacts")
        return artifacts


if __name__ == "__main__":
    # Quick test
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = os.path.join(os.path.dirname(__file__), "documents", "pdfs", "stress_test.pdf")

    ingest = SmartIngest(path)
    docs = ingest.load()
    for doc in docs:
        print(f"\n{'='*60}")
        print(f"Source: {doc.metadata['source']} | Page: {doc.metadata['page']}")
        print(f"{'='*60}")
        print(doc.page_content)
