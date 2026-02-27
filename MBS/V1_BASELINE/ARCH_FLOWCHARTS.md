# MKRS BRAIN V1.0 — ARCHITECTURE & FLOWCHARTS

This document visualizes the data flow and system architecture of the MBS V1.0 RAG system.

---

## 1. The Ingestion Pipeline (PDF to Knowledge Base)
This flowchart shows how raw PDFs are processed into a searchable format.

```mermaid
graph TD
    A[Raw PDF Documents] --> B{SmartIngest V10}
    B --> B1[Global Artifact Analysis]
    B --> B2[Table Masking]
    B2 --> B3[Y-Band Segmentation]
    B3 --> B4[Per-Band Column Detection]
    B4 --> B5[Cleaned Text & Tables]
    
    B5 --> C{SmartChunker V3}
    C --> C1[Parent Chunks: 1500 chars]
    C --> C2[Child Chunks: 300-500 chars]
    
    C1 --> D[(JSON Parent Store)]
    C2 --> E[IndicBERT Embeddings]
    E --> F[(ChromaDB Vector Store)]
    
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#dfd,stroke:#333
    style F fill:#dfd,stroke:#333
```

---

## 2. The Retrieval Pipeline (Query to Answer)
This flowchart shows how the system "thinks" when a user asks a question.

```mermaid
graph TD
    User([User Query]) --> Pre[Query Normalization]
    Pre --> Embed[Embed Query via IndicBERT]
    Embed --> Search[(ChromaDB Search)]
    
    Search -->|Top 60 Chunks| RR{Cross-Encoder Re-ranker}
    RR -->|Top Candidates| PDR[PDR Expansion]
    
    PDR -->|Look up Parent ID| PS[(JSON Parent Store)]
    PS -->|1500-char Contexts| Ded[Deduplication]
    
    Ded --> Gen{Sarvam LLM Generation}
    Gen --> Trans{Translation Layer}
    Trans --> Out([Final Answer + Sources])
    
    style RR fill:#f96,stroke:#333,stroke-width:2px
    style Gen fill:#9cf,stroke:#333,stroke-width:2px
```

---

## 3. High-Level Component Relationship
How the storage systems interact.

```mermaid
graph LR
    subgraph "Vector Database"
        V[Child Chunk Vectors] --> ID[parent_id]
    end
    
    subgraph "Document Store"
        ID -.-> P[Full Parent Text]
        P --> Meta[Source, Page, Rank]
    end
    
    subgraph "Compute"
        BERT[IndicBERT-v3]
        CE[Cross-Encoder]
        LLM[Sarvam-1]
    end
```

---

## 4. Logical State Diagram (Single Extraction)
A deep look at how a single page is "decomposed."

```mermaid
stateDiagram-v2
    [*] --> Page
    Page --> Analyze_Layout
    Analyze_Layout --> Mask_Tables
    Mask_Tables --> Segment_Bands
    Segment_Bands --> Detect_Columns
    Detect_Columns --> Read_Top_to_Bottom
    Read_Top_to_Bottom --> Assemble_Text
    Assemble_Text --> [*]
```
