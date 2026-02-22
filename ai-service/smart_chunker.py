from langchain.text_splitter import RecursiveCharacterTextSplitter
import re

class SmartChunker:
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Base splitter for fallback
        self.base_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def split_documents(self, documents):
        """
        Splits documents while preserving Markdown tables as atomic units.
        """
        final_chunks = []
        
        for doc in documents:
            text = doc.page_content
            
            # 1. Identify Tables (Markdown format)
            # Regex groups: (pre_text) (table) (post_text)
            # Table pattern: Pipe characters on consecutive lines
            # Matches header | row | separator | row...
            # We look for the separator line explicitly: | --- |
            table_pattern = r'(\|[^\n]+\|\n\|[\s:\-]+\|\n(?:\|[^\n]+\|\n)+)'
            parts = re.split(table_pattern, text)
            
            last_text_part = ""
            for part in parts:
                if not part.strip(): continue
                
                # Check if this part is a table
                if "|" in part and "---" in part:
                    # Case A: It's a table -> Prepend last text part as context
                    table_doc = doc.copy()
                    # Add context from the preceding text (last 200 chars)
                    context = last_text_part[-200:].strip() if last_text_part else ""
                    table_doc.page_content = f"{context}\n\n{part.strip()}" if context else part.strip()
                    table_doc.metadata["type"] = "table"
                    final_chunks.append(table_doc)
                    last_text_part = "" # Reset context after use
                else:
                    # Case B: Standard Text
                    last_text_part = part.strip()
                    text_doc = doc.copy()
                    text_doc.page_content = part.strip()
                    text_doc.metadata["type"] = "text"
                    
                    if len(part) > self.chunk_size:
                        sub_chunks = self.base_splitter.split_documents([text_doc])
                        final_chunks.extend(sub_chunks)
                    else:
                        final_chunks.append(text_doc)
                        
        print(f"  [Chunker] Split {len(documents)} pages into {len(final_chunks)} semantic chunks.")
        return final_chunks
