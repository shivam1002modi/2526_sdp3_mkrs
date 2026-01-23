import os
import pdfplumber
import numpy as np
from langchain_community.docstore.document import Document
from collections import Counter

class SmartIngest:
    def __init__(self, file_path):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)

    def load(self):
        """
        Hybrid V4 Ingestion:
        1. Global Header/Footer Statistical Analysis.
        2. Per-Page:
            a. Table Masking (Markdown Extraction).
            b. Y-Histogram (Detect Horizontal Bands).
            c. X-Histogram per Band (Detect Columns).
            d. Layout-Aware Reading (Columnar vs Linear).
        """
        print(f"  [DeepDive V4] Ingesting {self.filename} (Hybrid Mode)...")
        documents = []

        try:
            with pdfplumber.open(self.file_path) as pdf:
                if not pdf.pages: return []

                # 1. Global Artifact Analysis
                artifacts = self._analyze_artifacts(pdf)
                if artifacts: print(f"    [Clean] Removing artifacts: {list(artifacts)}")

                for i, page in enumerate(pdf.pages):
                    page_num = i + 1
                    if not page.chars: continue

                    # 2. Table Extraction & Masking
                    tables = page.find_tables()
                    table_bboxes = [t.bbox for t in tables]
                    md_tables = []
                    
                    for table in page.extract_tables():
                        if not table: continue
                        clean_rows = [[str(cell or "").replace("\n", " ") for cell in row] for row in table]
                        if not clean_rows: continue
                        header = "| " + " | ".join(clean_rows[0]) + " |"
                        sep = "| " + " | ".join(["---"] * len(clean_rows[0])) + " |"
                        body = "\n".join(["| " + " | ".join(row) + " |" for row in clean_rows[1:]])
                        md_tables.append(f"\n{header}\n{sep}\n{body}\n")

                    def not_in_tables(obj):
                        cx, cy = (obj["x0"] + obj["x1"]) / 2, (obj["top"] + obj["bottom"]) / 2
                        for box in table_bboxes:
                            if box[0] <= cx <= box[2] and box[1] <= cy <= box[3]: return False
                        return True
                    
                    filtered_page = page.filter(not_in_tables)
                    words = filtered_page.extract_words()
                    if not words: continue

                    # 3. Hybrid Layout Analysis
                    page_text = self._process_page_hybrid(words, page.width, page.height)
                    
                    # 4. Final Cleaning
                    clean_lines = []
                    for line in page_text.splitlines():
                        if line.strip() in artifacts: continue
                        clean_lines.append(line)
                    
                    final_text = "\n".join(clean_lines) + "\n\n".join(md_tables)
                    
                    if not final_text.strip(): continue

                    meta = {
                        "source": self.filename,
                        "page": page_num,
                        "ingestion_method": "DeepDive_Hybrid_V4"
                    }
                    documents.append(Document(page_content=final_text, metadata=meta))

        except Exception as e:
            print(f"  [ERROR] Hybrid V4 failed on {self.filename}: {e}")
            return []
        
        return documents

    def _process_page_hybrid(self, words, width, height):
        """
        Core V4 Logic: Split into Y-Bands, then analyze X-Histogram for Columns.
        """
        # A. Y-Axis Segementation (Find Vertical Gaps > 10px)
        # 1. Project to Y-Histogram
        y_hist = np.zeros(int(height) + 1)
        for w in words:
            top, bottom = int(w['top']), int(w['bottom'])
            y_hist[top:bottom] = 1
        
        # 2. Find Bands
        bands = []
        in_band = False
        start_y = 0
        
        # Simple finite state machine for gaps
        gap_size = 0
        band_start = 0
        
        # Find start of first content
        first_y = int(min(w['top'] for w in words))
        last_y = int(max(w['bottom'] for w in words))
        
        if first_y < 0: first_y = 0
        
        current_y = first_y
        while current_y < last_y:
            # Check for gap (sequence of 0s)
            if y_hist[current_y] == 0:
                gap_size += 1
            else:
                if gap_size > 15: # Significant vertical gap -> Split Band
                    # Previous band ended at current_y - gap_size
                    band_end = current_y - gap_size
                    if band_end > band_start:
                        bands.append((band_start, band_end))
                    band_start = current_y
                gap_size = 0
            current_y += 1
        # Add final band
        bands.append((band_start, last_y))

        # B. Process Each Band
        full_text = ""
        
        for b_start, b_end in bands:
            # Filter words in this band
            band_words = [w for w in words if b_start <= w['top'] and w['bottom'] <= b_end]
            if not band_words: continue
            
            # X-Axis Histogram (Column Detection)
            x_hist = np.zeros(int(width) + 1)
            for w in band_words:
                x0, x1 = int(w['x0']), int(w['x1'])
                x_hist[x0:x1] = 1
            
            # Check for Central Gap (Valley)
            mid = int(width / 2)
            # Scan +/- 50px from center. If mostly empty, it's 2 columns.
            center_zone = x_hist[mid-40 : mid+40]
            is_multi_col = False
            
            # Strategy: look for a continuous gap of at least 15px in the center region
            gap_run = 0
            max_center_gap = 0
            for val in center_zone:
                if val == 0: gap_run += 1
                else: gap_run = 0
                max_center_gap = max(max_center_gap, gap_run)
            
            if max_center_gap > 15:
                is_multi_col = True
            
            if is_multi_col:
                # Split into Left and Right Columns
                # Find the gap center
                split_x = mid
                
                col_a = [w for w in band_words if w['x1'] < split_x + 20]
                col_b = [w for w in band_words if w['x0'] > split_x - 20]
                
                # Sort and Read A
                col_a_text = self._read_linear(col_a)
                # Sort and Read B
                col_b_text = self._read_linear(col_b)
                
                full_text += col_a_text + "\n" + col_b_text + "\n"
            else:
                # Single Column
                full_text += self._read_linear(band_words) + "\n"
        
        return full_text

    def _read_linear(self, words):
        """Reads words top-to-bottom, left-to-right."""
        if not words: return ""
        # Sort by Top primarily, Left secondarily
        # Tolerance: Round Top to nearest 3px to handle misalignment
        words.sort(key=lambda w: (int(w['top'] / 3), w['x0']))
        
        text = ""
        last_bottom = 0
        last_x1 = 0
        
        # Simple reconstruction
        # We assume words are pre-sorted lines.
        # Check delta-y for newlines.
        
        current_line_y = int(words[0]['top'] / 3)
        line_buffer = []
        
        for w in words:
            w_y = int(w['top'] / 3)
            if w_y > current_line_y + 1: # New line
                text += " ".join([wb['text'] for wb in line_buffer]) + "\n"
                line_buffer = [w]
                current_line_y = w_y
            else:
                line_buffer.append(w)
        
        if line_buffer:
            text += " ".join([wb['text'] for wb in line_buffer]) + "\n"
            
        return text.strip()

    def _analyze_artifacts(self, pdf):
        candidates = []
        for page in pdf.pages:
            h = page.height
            header = page.crop((0,0,page.width, h*0.1)).extract_text()
            footer = page.crop((0, h*0.9, page.width, h)).extract_text()
            if header: candidates.append(header.strip())
            if footer: candidates.append(footer.strip())
        
        counts = Counter(candidates)
        threshold = len(pdf.pages) * 0.6
        return {txt for txt, count in counts.items() if count > threshold}

if __name__ == "__main__":
    pass
