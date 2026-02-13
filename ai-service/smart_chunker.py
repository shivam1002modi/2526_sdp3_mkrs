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
            
            for part in parts:
                if not part.strip(): continue
                
                # Check if this part is a table
                if "|" in part and "---" in part:
                    # Case A: It's a table -> Keep it whole if possible
                    # If table is huge, we might have to split it, but ideally we don't.
                    # We create a separate chunk just for this table to preserve its grid structure.
                    table_doc = doc.copy()
                    table_doc.page_content = part.strip()
                    table_doc.metadata["type"] = "table"
                    final_chunks.append(table_doc)
                else:
                    # Case B: Standard Text -> Use Semantic Splitter
                    # Only split if it's large
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
