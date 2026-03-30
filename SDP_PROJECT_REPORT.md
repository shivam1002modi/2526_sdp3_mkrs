A Project Report On    

**(The Language Agnostic Chatbot)**

**Prepared By:**    

Pranjal Savsani(CE142, 23CEUOS141) 

Shivam Modi(CE113, 23CEUOZ113) 

B. Tech CE, Semester VI 

Subject: System Design Practice

**Guided By**

Prof. Hariom A. Pandya 

Associate Professor

 ![][image1]  

Department of Computer Engineering Faculty of Technology Dharmsinh Desai University College Road, Nadiad-387001 Gujarat, INDIA


![][image2]

Department of Computer Engineering Faculty of Technology Dharmsinh Desai University College Road, Nadiad-387001 Gujarat, INDIA


CERTIFICATE 


This is to certify that the practical/term work carried out in the subject of System Design Practice and recorded in this report is the bonafide work of 

**Pranjal Savsani**,ID: 23CEUOS141 

**Shivam Modi**, ID: 23CEUOZ113

       

of B.Tech semester VI in the branch of 

         Computer Engineering during the academic year 2025 2026

Prof. Hariom A. Pandya 					Dr. C.K. Bhensdadia                    Associate Professor                                                       Head of Department 

  Comprehensive Project Report and SRS

**The Language Agnostic Chatbot**

Academic Year : 2025–2026

Department : Computer Engineering 

Institution : Dharmsinh Desai University 

Project Team : Pranjal Savsani,Shivam Modi

Guide : Hariom A. Pandya 

Table of Contents 


| Section | Title                                                                                                                | Pg. |
| :---- | :---- | :---- |
| 1 | Introduction…………………………………………………………………………... | 3 |
| 1.1 | Document Purpose………………………………………………………………………………... | 3 |
| 1.2 | Product Scope………………………………………………………………………... | 3 |
| 1.3 | Intended Audience and Document Overview………………………………………... | 4 |
| 1.4 | Definitions, Acronyms and Abbreviations…………………………………………... | 4 |
| 1.5 | Document Conventions………………………………………………………………. | 5 |
| 1.6 | References and Acknowledgments…………………………………………………... | 5 |
| 2 | Overall Description…………………………………………………………………... | 6 |
| 2.1 | Product Overview……………………………………………………………………. | 6 |
| 2.2 | Product Functionality………………………………………………………………… | 7 |
| 2.3 | Design and Implementation Constraints……………………………………………... | 8 |
| 2.4 | Assumptions and Dependencies……………………………………………………... | 9 |
| 3 | Specific Requirements……………………………………………………………..… | 10 |
| 3.1 | External Interface Requirements……………………………………………………... | 10 |
| 3.2 | Functional Requirements…………………………………………………………….. | 12 |
| 3.3 | Use Case Model……………………………………………………………………… | 14 |
| 4 | Other Non-Functional Requirements………………………………………………… | 17 |
| 4.1 | Performance Requirements…………………………………………………………... | 17 |
| 4.2 | Safety and Security Requirements…………………………………………………… | 18 |
| 4.3 | Software Quality Attributes………………………………………………………….. | 18 |
| 5 | System Tuning and Optimization……………………………………………………. | 20 |
| 6 | Test Results and Benchmark Analysis……………………………………………….. | 22 |
| 7 | Other Requirements………………………………………………………………….. | 26 |
| A | Appendix A – Data Dictionary………………………………………………………. | 27 |
| B | Appendix B – Dependency Manifest………………………………………………… | 29 |
| D | Appendix D – Demo Screenshots……………………………………………………. | 32 |
|  |  |  |

| Version | Primary Author(s) | Description of Version | Date Completed |
| :---- | ----- | ----- | ----- |
| 0.1 | Shivam Modi | Initial draft including scope, goals, and architecture outline | 15 February 2026 |
| 0.5 | MKRS Team | Added functional requirements, use cases, and interface specifications | 01 March 2026 |
| 1.0 | MKRS Team | Finalized SRS with benchmark results, tuning data, and full dependency manifest | 13 March 2026 |

# **1\. Introduction**

### DocuBot is a professional-grade, locally-hosted Retrieval-Augmented Generation (RAG) system designed to support educational institutions and organizations that require a privacy-first and cost-effective AI assistant. The system enables users to ask questions and receive accurate answers directly from their own internal PDF documents.

Unlike cloud-based AI services, DocuBot operates entirely on local infrastructure, ensuring that sensitive documents and organizational data remain secure and private. This approach makes it especially suitable for environments where data confidentiality and compliance are critical.

This **Software Requirements Specification (SRS)** document provides a comprehensive specification of the DocuBot system. It outlines the system’s architecture, functional requirements, external interfaces, performance expectations, safety constraints, and software quality attributes. The document serves as the primary reference for all phases of the project lifecycle, including development, testing, deployment, and maintenance.

## **1.1 Document Purpose**

This **Software Requirements Specification (SRS)** formally defines the complete set of requirements for the **DocuBot** system, Version 1.0 (Project MKRS). Its purpose is threefold:

1. **Baseline for Development:**  
    It provides the development team with a clear and unambiguous set of functional and non-functional requirements to implement.

2. **Contract with the Client/Instructor:**  
    It serves as a formal agreement that defines the scope, objectives, and capabilities of the delivered product.

3. **Foundation for Testing:**  
    It provides the basis for the **MKRS Benchmark System (MBS)** test suite, which validates the system using **65 standardized questions across 15 languages**.

This document covers the entire **DocuBot system**, including its five microservices: **Frontend, Backend Proxy, Admin Server, Rasa NLU, and Rasa Action Server**, along with the custom **Retrieval-Augmented Generation (RAG) pipeline** and the **evaluation framework**.

## 

## **1.2 Product Scope**

DocuBot is a **self-contained, locally deployable AI assistant** designed to answer questions using information extracted directly from internal PDF documents.

The system is intended to replace or enhance traditional **FAQ-based knowledge systems**, particularly in environments where **data privacy and security are critical**. By operating entirely on local infrastructure, DocuBot ensures that sensitive documents remain within the organization and are not transmitted to external cloud services.

Typical deployment environments include **university examination offices, government departments, research institutions, and corporate intranets**, where staff and users require quick, accurate, and secure access to document-based information.

### **Product Name: DocuBot — The Language Agnostic Chatbot**

### **Version: 1.0**

#### **Core Capabilities**

* Ingest PDF documents of any layout (single-column, multi-column, or tabular) and build a searchable knowledge base.

* Answer user questions in natural language through a **web-based chat interface** or **voice interaction**.

* Automatically detect the user’s language and respond in that language, supporting **15+ languages**, including Hindi, Bengali, Marathi, Tamil, Telugu, Gujarati, Kannada, Malayalam, Punjabi, Urdu, Spanish, French, German, Japanese, and Chinese.

* Provide **verifiable source citations** for every answer, including the **document name and page number**.

| Benefit | Description |
| ----- | ----- |
| **100% Privacy** | All processing — embedding, inference, and generation — runs on the local machine. No data leaves the server and no external API calls are required. |
| **Zero Recurring Cost** | Uses open-source models such as **Llama 3.2** and **Multilingual-E5-Small**, eliminating subscription costs for services like OpenAI, Google, or Azure. |
| **High Accuracy** | Context-aware ingestion prevents column mixing in multi-column PDFs. **Parent Document Retrieval (PDR)** ensures the language model receives complete and relevant context. |
| **Accessibility** | Supports a full hands-free voice interaction mode with **real-time Speech-to-Text (STT), silence detection, and Text-to-Speech (TTS)**. |

### 

## **1.3 Intended Audience and Document Overview**

This document is intended for the following audiences:

| Audience | Relevant Sections |
| ----- | ----- |
| **Course Instructor / Client** | Sections 1, 2, and 4 – High-level scope, objectives, and quality requirements |
| **Development Team** | Sections 2, 3, and 5 – Architecture, functional requirements, and optimization |
| **Testers / QA Team** | Sections 3.2, 4.1, and 6 – Functional requirements, performance targets, and benchmark results |
| **Future Maintainers** | Sections 2.3, 5, Appendix A and B – Design constraints, system tuning, data dictionary, and dependency information |

It is recommended to read this document sequentially. Readers should begin with the **Overview (Section 2\)** to understand the system context, followed by **Specific Requirements (Section 3\)** for implementation details, and finally **Benchmark Analysis (Section 6\)** for performance validation and evaluation results.

## 

## 

## **1.4 Definitions, Acronyms and Abbreviations**

| Term | Definition |
| ----- | ----- |
| **Bi-Encoder** | A neural network model that independently encodes a query and a document passage into fixed-length vectors for fast cosine similarity search. |
| **ChromaDB** | An open-source vector database used to store and query document chunk embeddings. |
| **Cross-Encoder** | A more powerful (but slower) model that processes a query–passage pair together as a single input for precise relevance scoring. It is typically used for re-ranking. |
| **DIET Classifier** | Dual Intent and Entity Transformer. Rasa’s default architecture for intent classification and entity recognition. |
| **FAISS** | Facebook AI Similarity Search. A library designed for efficient similarity search and clustering of dense vectors. |
| **LLM** | Large Language Model. |
| **MBS** | MKRS Benchmark System. A custom-built automated testing framework used to measure system performance and quality. |
| **NLU** | Natural Language Understanding. |
| **Ollama** | A framework used to run and manage Large Language Models locally on consumer hardware. |
| **PDR** | Parent Document Retrieval. A strategy in which smaller child chunks are used for precise vector searches, while their larger parent contexts are sent to the LLM for answer generation. |
| **RAG** | Retrieval-Augmented Generation. An AI architecture that improves LLM responses by grounding them in retrieved factual information. |
| **RHR** | Retrieval Hit Rate. The percentage of questions for which the system retrieves context from the correct source document. |
| **SEC** | Semantic Extraction Confidence. The percentage of expected factual keywords present in the system’s generated response. |
| **SmartIngest** | A custom PDF extraction engine that performs layout-aware text extraction using Y-axis and X-axis histogram analysis. |
| **STT / TTS** | Speech-to-Text / Text-to-Speech technologies used for voice interaction. |
| **TMS** | Total MKRS Score. A weighted aggregate benchmark score ranging from 0–100. |

## **1.5 Document Conventions**

This document follows the **IEEE 830-1998 standard** for Software Requirements Specifications (SRS).

* **Font:** Body text uses the default sans-serif typeface with a standard readable size.

* **Code and Technical Terms:** Displayed in monospace backtick notation (for example, actions.py, SmartIngest).

* **Requirement Identifiers:**

  * Functional requirements use the prefix **F** (e.g., F1, F2).

  * Performance requirements use **P**.

  * Safety requirements use **S**.

  * Use cases use **U**.

* **Diagrams:** System diagrams are written using **Mermaid syntax** to ensure reproducibility.

* **Priority Levels:** Requirements are categorized as **High**, **Medium**, or **Low** priority.

## **1.6 References and Acknowledgments**

| \# | Reference |
| ----- | ----- |
| 1 | Gomaa, H. (2011). *Software Modeling and Design: UML, Use Cases, Patterns, and Software Architectures*. Cambridge University Press. |
| 2 | OMG Unified Modeling Language (UML) Specification, Version 2.5.1. |
| 3 | Rasa Open Source Documentation. [https://rasa.com/docs/rasa/](https://rasa.com/docs/rasa/) |
| 4 | LangChain Framework Documentation. [https://python.langchain.com/](https://python.langchain.com/) |
| 5 | Ollama Documentation. [https://ollama.com/](https://ollama.com/) |
| 6 | Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS. |
| 7 | Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. EMNLP. |

# **2\. Overall Description**

## **2.1 Product Overview**

DocuBot is a new, self-contained software product. It is not a follow-on to an existing commercial system. The project originated as a capstone initiative aimed at solving the challenge of **secure, offline document intelligence** for organizations that cannot send sensitive data to cloud-hosted AI APIs due to privacy regulations such as **GDPR** and **FERPA**.

The system adopts a **microservices architecture** composed of five independently deployable services that communicate through **REST APIs running on localhost**.

---

### **System Architecture Overview**

```mermaid
graph TD
    subgraph "User Layer"
        User((User / Admin))
    end

    subgraph "Presentation Tier (Port 3000)"
        Frontend["React.js Frontend<br/>Chat UI + Admin Panel + Voice"]
    end

    subgraph "API Tier (Port 5001)"
        Backend["Node.js / Express Backend<br/>Proxy, Auth, Static Files"]
    end

    subgraph "AI Tier"
        AdminServer["FastAPI Admin Server<br/>Port 8000<br/>PDF Upload & Retrain"]
        RasaNLU["Rasa NLU Server<br/>Port 5055<br/>Intent Detection (mBERT)"]
        ActionServer["Rasa Action Server<br/>Port 5055<br/>RAG Pipeline (The Brain)"]
    end

    subgraph "Data Tier"
        ChromaDB[("ChromaDB<br/>Vector Store<br/>(Child Chunks)")]
        ParentStore[("parent_store.json<br/>(Parent Contexts)")]
        PDFs[("PDF Documents<br/>/documents/pdfs/")]
        Ollama["Ollama LLM<br/>Port 11434<br/>(Llama 3.2:3b)"]
    end

    User <--> Frontend
    Frontend <-->|REST API| Backend
    Backend <-->|/api/admin| AdminServer
    Backend <-->|/api/chat| RasaNLU
    RasaNLU <-->|action_query_doc| ActionServer
    ActionServer <--> ChromaDB
    ActionServer <--> ParentStore
    ActionServer <--> Ollama
    AdminServer --> PDFs
```

The system architecture consists of four main tiers:

**1\. User Layer**

* User / Administrator interacts with the system.

**2\. Presentation Tier (Port 3000\)**

* React.js Frontend

* Chat Interface

* Admin Dashboard

* Voice Interaction Interface

**3\. API Tier (Port 5001\)**

* Node.js / Express Backend

* Handles authentication

* Provides API proxy

* Serves static files

**4\. AI Tier**

* **FastAPI Admin Server (Port 8000\)** – Handles PDF upload and retraining

* **Rasa NLU Server (Port 5005\)** – Intent detection using multilingual BERT

* **Rasa Action Server (Port 5055\)** – Executes the Retrieval-Augmented Generation (RAG) pipeline

**5\. Data Tier**

* **ChromaDB** – Vector database storing document embeddings

* **Parent Context Store (parent\_store.json)** – Stores parent document chunks

* **PDF Storage Directory (/documents/pdfs/)** – Uploaded documents

* **Ollama LLM (Port 11434\)** – Runs the Llama 3.2 language model locally

---

### **SmartIngest V10 — Document Ingestion Pipeline**

```mermaid
flowchart TD
    A["PDF File Input"] --> B["Open with pdfplumber"]
    B --> C{"Pages > 3?"}
    C -->|Yes| D["Global Artifact Analysis\n(Header/Footer detection\nacross all pages)"]
    C -->|No| E["Skip artifact detection\n(too risky for short PDFs)"]
    D --> F["Per-Page Processing Loop"]
    E --> F
    F --> G["Step A: Table Masking\nExtract tables as Markdown\nMask table regions"]
    G --> H["Step B: Extract text\noutside table bounding boxes"]
    H --> I["Step C: Y-Band Segmentation\nBuild Y-histogram\nFind vertical gaps > 12px"]
    I --> J["Step D: Per-Band\nColumn Detection\nX-histogram gap analysis\nwithin each Y-band"]
    J --> K{"Columns > 1?"}
    K -->|Yes| L["Read each column\ntop-to-bottom\nindependently"]
    K -->|No| M["Read as\nsingle column"]
    L --> N["Step E: Sort by Y-position\nFilter artifacts\nAssemble final text"]
    M --> N
    N --> O["Output: LangChain Document\nwith metadata\n(source, page, method)"]
```

The SmartIngest pipeline processes PDF files and extracts structured content through the following steps:

1. **PDF Input Processing**

   * PDF files are opened using the pdfplumber library.

2. **Artifact Detection**

   * If the document contains more than three pages, global header and footer artifacts are detected across pages.

3. **Table Extraction**

   * Tables are extracted and converted into Markdown format.

   * Table regions are masked before text extraction.

4. **Text Extraction**

   * Text outside table bounding boxes is extracted.

5. **Y-Band Segmentation**

   * A Y-axis histogram is built to detect vertical whitespace gaps greater than 12 pixels.

6. **Column Detection**

   * X-axis histogram analysis identifies multiple column boundaries within each band.

7. **Column Processing**

   * Multi-column pages are read column-by-column from top to bottom.

   * Single-column pages are processed normally.

8. **Final Assembly**

   * Text segments are sorted by vertical position.

   * Artifacts are filtered.

   * The final output is stored as a **LangChain Document object with metadata**.

---

### **RAG Query Processing Flow**

```mermaid
flowchart LR
    subgraph "INPUT"
        Q["User Query\n(any language)"]
    end

    subgraph "STEP 1: LANGUAGE"
        LD["langdetect\nIdentify language"]
        TR1["Translate to English\n(if non-English)\nvia Ollama"]
    end

    subgraph "STEP 2: RETRIEVE"
        EMB["Embed query\nmultilingual-e5-small\n384-dim vector"]
        VS["ChromaDB\nsimilarity_search\nk=75 candidates"]
    end

    subgraph "STEP 3: RE-RANK"
        T1["Tier 1: Re-rank top-10\nCross-Encoder"]
        EE{"Score > 0.95?"}
        T2["Tier 2: Re-rank\ncandidates 10-60"]
    end

    subgraph "STEP 4: EXPAND (PDR)"
        PID["Look up parent_id\nfor each child"]
        DD["Deduplicate\nby parent_id"]
        CTX["Top 8 unique\nparent contexts"]
    end

    subgraph "STEP 5: GENERATE"
        LLM["Ollama llama3.2:3b\nStructured RAG Prompt\ntemp=0.0"]
    end

    subgraph "STEP 6: TRANSLATE"
        TR2["Translate answer\nback to user language"]
        GC{"Garbled?"}
        FB["Fallback to English"]
    end

    subgraph "OUTPUT"
        ANS["JSON Response\n{text, sources}"]
    end

    Q --> LD --> TR1 --> EMB --> VS --> T1 --> EE
    EE -->|Yes: EARLY EXIT| PID
    EE -->|No| T2 --> PID
    PID --> DD --> CTX --> LLM --> TR2 --> GC
    GC -->|No| ANS
    GC -->|Yes| FB --> ANS
```

When a user asks a question, the following pipeline executes:

1. **Language Detection**

   * The system detects the language using langdetect.

2. **Query Translation**

   * Non-English queries are translated into English using the Ollama LLM.

3. **Embedding Generation**

   * The query is converted into a **384-dimensional vector** using multilingual-e5-small.

4. **Vector Search**

   * ChromaDB retrieves the **top 75 candidate document chunks**.

5. **Re-ranking**

   * Cross-Encoder model ranks the top results.

   * If a result exceeds a confidence threshold (\>0.95), the system performs an **early exit optimization**.

6. **Parent Document Retrieval (PDR)**

   * Parent contexts are retrieved using parent\_id.

   * Duplicate parents are removed.

7. **Context Expansion**

   * The system selects the **top 8 unique parent contexts**.

8. **Answer Generation**

   * The Ollama LLM (llama3.2:3b) generates a structured response.

9. **Answer Translation**

   * The response is translated back to the user's original language.

10. **Fallback Handling**

* If translation output is garbled, the system falls back to English.

11. **Final Response**

* A JSON response containing the answer text and source citations is returned.

---

### **Voice Interaction State Machine**

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Listening : User clicks microphone
    Listening --> Transcribing : Speech detected
    Transcribing --> Transcribing : Continuous speech
    Transcribing --> Submitting : Silence detected (1.5s)
    Submitting --> Thinking : Query sent to RAG pipeline
    Thinking --> Speaking : Answer received from LLM
    Speaking --> EchoGuard : TTS playback starts
    EchoGuard --> Listening : TTS playback ends, mic resumes
    Speaking --> Idle : User clicks stop
    Listening --> Idle : User clicks microphone (toggle off)

    note right of EchoGuard
        Anti-Echo Logic:
        Microphone is MUTED
        during TTS playback to
        prevent re-capture
    end note
```

DocuBot supports hands-free voice interaction with the following workflow:

1. **Idle State**

   * The system waits for the user to activate the microphone.

2. **Listening State**

   * Speech input is captured.

3. **Transcribing State**

   * Speech is continuously converted to text.

4. **Submission Trigger**

   * A 1.5-second silence automatically submits the query.

5. **Thinking State**

   * The RAG pipeline processes the query.

6. **Speaking State**

   * The generated answer is played through Text-to-Speech.

7. **Echo Guard**

   * The microphone is muted during playback to prevent feedback loops.

8. **Return to Listening**

   * Once playback ends, the microphone resumes listening.

---

# **2.2 Product Functionality**

The system consists of the following functional modules:

---

### **A. Document Ingestion Pipeline (SmartIngest V10)**

1. Detects global header and footer artifacts across pages.

2. Extracts tables and converts them into Markdown format.

3. Splits page content into **Y-axis bands** based on whitespace gaps.

4. Detects column boundaries within each band using X-axis histogram analysis.

5. Reads each column independently from top to bottom.

---

### **B. Smart Chunking Engine (SmartChunker V3 — PDR)**

1. Implements **Parent Document Retrieval (PDR)**.

2. Creates:

   * Parent chunks (\~1500 characters) for LLM context.

   * Child chunks (\~500 characters) for vector search.

3. Uses semantic splitting based on:

   * paragraph breaks

   * sentence endings

   * clause boundaries

   * word boundaries

4. Ensures tables remain **fully intact and never split across chunks**.

---

### **C. Retrieval-Augmented Generation (RAG)**

1. Query embedding using multilingual-e5-small.

2. Vector similarity search in ChromaDB with **k \= 75 candidates**.

3. Tiered Cross-Encoder re-ranking with early exit optimization.

4. Parent context expansion and deduplication.

5. Structured prompt generation for high factual accuracy using the Ollama LLM.

---

### 

### **D. Multilingual Support**

1. Automatic language detection using langdetect.

2. Translation of user queries to English.

3. Response translation back to the original language.

4. Automatic fallback to English if translation errors occur.

---

### **E. Voice Interaction**

1. Real-time Speech-to-Text using the **Web Speech API**.

2. Automatic silence detection for query submission.

3. Anti-echo logic preventing microphone feedback during playback.

4. Text-to-Speech response generation.

---

### **F. Admin Dashboard**

1. Drag-and-drop PDF upload functionality.

2. One-click retraining capability.

3. Real-time log streaming from the FastAPI Admin Server.

---

### **G. Benchmarking (MBS)**

1. 65-question standardized evaluation dataset.

2. Coverage includes:

   * 13 English topic questions

   * 7 stress tests

   * 35 multilingual questions

3. Automated scoring using five metrics:

   * Retrieval Hit Rate (RHR)

   * Semantic Extraction Confidence (SEC)

   * Negative Hallucination Rate (NEG)

   * Latency (LAT)

   * GPU Memory Usage (VRAM)

4. Generates evaluation reports including:

   * REPORT.md

   * raw\_scores.json

## **2.3 Design and Implementation Constraints**

| Constraint | Description |
| ----- | ----- |
| **C1: Local Execution Only** | All AI inference must run locally with no external API calls during the RAG pipeline. |
| **C2: Hardware Minimum** | Must run on consumer hardware with at least **16 GB RAM** and a modern multi-core CPU. |
| **C3: Python Version Lock** | Python **3.10.x** is required because Rasa 3.6.15 is incompatible with Python 3.11+. |
| **C4: Transformers Version Pin** | transformers must remain at **v4.45.0** due to TensorFlow compatibility with Rasa. |
| **C5: Design Methodology** | The **COMET methodology** must be used for system design. |
| **C6: Modeling Language** | All diagrams must follow **UML 2.5** standards. |
| **C7: Operating System** | System is optimized for **Windows 10/11** using PowerShell automation scripts. |

## **2.4 Assumptions and Dependencies**

### **Assumptions**

1. Users will access the system using a **Chromium-based browser** (Chrome or Edge).

2. Uploaded PDFs are **text-based documents**, not scanned images.

3. The host machine maintains a stable local network connection for communication with localhost services.

4. Ollama is installed and the **llama3.2:3b model** is downloaded before initial use.

| Dependency | Type | Purpose |
| ----- | ----- | ----- |
| Ollama | External Service | Runs the local LLM and manages model inference |
| Hugging Face Hub | External Download | Provides embedding and ranking models during first run |
| Web Speech API | Browser API | Enables Speech-to-Text and Text-to-Speech |
| Node.js & npm | Runtime | Runs frontend and backend services |
| Python 3.10 | Runtime | Executes AI services including Rasa NLU and Action Server |

# **3\. Specific Requirements**

## **3.1 External Interface Requirements**

### **3.1.1 User Interfaces**

The primary user interface is a **web-based single-page React application** accessible at:

http://localhost:3000

### **Chat Interface Components**

* **Message History Panel**

  * Displays a scrollable conversation between the user and DocuBot.

  * Bot responses contain **source citation badges** (document name and page number).

  * Each badge is clickable and opens the original PDF using the backend static file server.

* **Text Input Bar**

  * Persistent input field located at the bottom of the screen.

  * Includes a **Send button** for submitting questions.

* **Voice Mode Toggle**

  * Floating microphone icon used to activate hands-free voice interaction.

  * Visual states include:

    * **Idle:** Grey microphone icon

    * **Listening:** Red pulse animation

    * **Thinking:** Blue loading spinner

* **Language Indicator**

  * Displays the automatically detected language of the user's latest query

### **Admin Panel Components**

* **PDF Upload Zone**

  * Drag-and-drop interface for uploading .pdf files.

  * Displays file name and file size after selection.

* **Retrain Button**

  * Sends a request to:

POST /retrain

to the **FastAPI Admin Server (Port 8000\)**.

* **Live Log Viewer**

  * Terminal-style panel displaying retraining logs in real-time.

  * Uses **FastAPI StreamingResponse** to stream subprocess output.

---

### **User Interface Screenshots**

*(Insert screenshots in your document)*

* Chat Interface with source citations

* Voice interaction in listening mode

* Admin dashboard with upload and retraining logs

* Multilingual response example

### 

### **3.1.2 Hardware Interfaces**

| Hardware | Interface Type | Description |
| ----- | ----- | ----- |
| CPU | Compute | Main inference device. Ollama runs with OLLAMA\_NUM\_THREADS=8 and elevated priority. |
| Microphone | Audio Input | Captures voice queries using the Web Speech API. |
| Speakers | Audio Output | Plays answers through Text-to-Speech. |
| Disk | Storage | Stores vector database, parent context file, and ML models. |

### **3.1.3 Software Interfaces**

| Interface | Protocol | Description |
| ----- | ----- | ----- |
| Frontend → Backend | HTTP REST (Port 5001\) | Chat and admin API calls |
| Backend → Rasa NLU | HTTP REST (Port 5005\) | Sends messages for intent detection |
| Rasa NLU → Action Server | HTTP REST (Port 5055\) | Executes document retrieval action |
| Action Server → Ollama | HTTP REST (Port 11434\) | Sends prompts to LLM |
| Action Server → ChromaDB | Local File I/O | Vector similarity search |
| Admin Server → Retraining Script | Subprocess | Executes ingestion pipeline |

## **3.2 Functional Requirements**

| ID | Requirement | Priority | Use Case |
| ----- | ----- | ----- | ----- |
| F1 | Extract text from PDFs using SmartIngest V10. | High | U3 |
| F2 | Detect and remove repeating headers and footers. | High | U3 |
| F3 | Convert PDF tables into Markdown format and keep them atomic during chunking. | High | U3 |
| F4 | Implement Parent Document Retrieval (PDR). | High | U1, U2 |
| F5 | Perform semantic paragraph-aware chunking. | High | U3 |
| F6 | Generate query embeddings using multilingual-e5-small. | High | U1 |
| F7 | Retrieve top 75 candidate chunks from ChromaDB. | Medium | U1 |
| F8 | Re-rank candidates using Cross-Encoder model. | High | U1 |
| F9 | Expand child chunks to parent contexts and send top 8 to the LLM. | High | U1 |
| F10 | Generate answers using llama3.2:3b via Ollama. | High | U1 |
| F11 | Detect language and perform automatic translation if required. | High | U2 |
| F12 | Detect garbled translations and fallback to English. | Medium | U2 |
| F13 | Attach document source citations to every answer. | High | U1 |
| F14 | Allow admin-triggered retraining of the knowledge base. | Medium | U3 |
| F15 | Support hands-free voice interaction with silence detection. | Medium | U4 |
| F16 | Return “I don’t know” when retrieval confidence is too low. | High | U1 |

## **3.3 Use Case Model**

### **Use Case Diagram**

```mermaid
graph LR
    User((User))
    Admin((Admin))

    subgraph "DocuBot System"
        U1[U1: Ask Question via Text]
        U2[U2: Ask Question in Foreign Language]
        U3[U3: Upload and Retrain Knowledge Base]
        U4[U4: Ask Question via Voice]
        U5[U5: View Source Document]
    end

    User --> U1
    User --> U2
    User --> U4
    User --> U5
    Admin --> U3
    U4 -.->|extends| U1
    U2 -.->|extends| U1
    U1 --> U5
```

### **Parent Document Retrieval (PDR) — Chunking Strategy Diagram**

```mermaid
flowchart TD
    subgraph "Raw PDF Page"
        RAW["Full page text\n(extracted by SmartIngest)"]
    end

    subgraph "Table Detection"
        RAW --> TD{"Contains\nMarkdown table?"}
        TD -->|Yes| ATOMIC["TABLE CHUNK\n(Atomic — never split)\nBecomes its own\nParent AND Child"]
        TD -->|No| TEXT["Text Segment"]
    end

    subgraph "Semantic Splitting"
        TEXT --> PSplit["Parent Splitter\nmax_size = 1500 chars\nSplit on: paragraph > sentence > clause > word"]
        PSplit --> P1["Parent A\n~1500 chars"]
        PSplit --> P2["Parent B\n~1500 chars"]
        P1 --> CSplit1["Child Splitter\nmax_size = 500 chars"]
        P2 --> CSplit2["Child Splitter\nmax_size = 500 chars"]
        CSplit1 --> C1["Child A1\n~500c"]
        CSplit1 --> C2["Child A2\n~500c"]
        CSplit1 --> C3["Child A3\n~500c"]
        CSplit2 --> C4["Child B1\n~500c"]
        CSplit2 --> C5["Child B2\n~500c"]
    end

    subgraph "Storage"
        P1 --> PS[("parent_store.json\n(Parent Contexts)")]
        P2 --> PS
        ATOMIC --> PS
        C1 --> CDB[("ChromaDB\n(Child Chunks + Embeddings)")]
        C2 --> CDB
        C3 --> CDB
        C4 --> CDB
        C5 --> CDB
        ATOMIC --> CDB
    end
```

### **Multilingual Query Processing Flow**

```mermaid
sequenceDiagram
    participant U as User (Hindi)
    participant FE as Frontend
    participant BE as Backend :5001
    participant NLU as Rasa NLU :5005
    participant ACT as Action Server :5055
    participant OLL as Ollama :11434
    participant DB as ChromaDB

    U->>FE: "ब्लैक होल क्या है?"
    FE->>BE: POST /api/chat {text}
    BE->>NLU: POST /webhooks/rest {text}
    NLU->>NLU: Intent: document_query
    NLU->>ACT: action_query_doc
    ACT->>ACT: langdetect → lang=hi
    ACT->>OLL: Translate Hindi → English
    OLL-->>ACT: "What is a black hole?"
    ACT->>DB: similarity_search(k=75)
    DB-->>ACT: 75 child chunks
    ACT->>ACT: Cross-Encoder re-rank → top 3
    ACT->>ACT: PDR expand → parent contexts
    ACT->>OLL: Generate answer (RAG prompt)
    OLL-->>ACT: English answer
    ACT->>OLL: Translate English → Hindi
    OLL-->>ACT: Hindi answer
    ACT->>ACT: Garble check → OK
    ACT-->>NLU: {text: Hindi answer, sources}
    NLU-->>BE: Response
    BE-->>FE: JSON {text, sources[]}
    FE-->>U: Display Hindi answer + citations
```

### Primary Actors

* User

* Admin

| Use Case | Description |
| :---- | :---- |
| U1 | Ask question via text |
| U2 | Ask question in a foreign language |
| U3 | Upload and retrain knowledge base |
| U4 | Ask question using voice |
| U5 | View source document |

Relationships:

* U2 extends U1

* U4 extends U1

* U1 leads to U5

# 

# 

# 

# **4\. Other Non-Functional Requirements**

## **4.1 Performance Requirements**

| ID | Requirement | Target |
| ----- | ----- | ----- |
| P1 | Retrieval Hit Rate | ≥ 95% |
| P2 | Fact Accuracy | ≥ 75% |
| P3 | No Hallucination | 100% |
| P4 | Average Latency | ≤ 10 seconds |
| P5 | Cold Start Time | ≤ 120 seconds |
| P6 | PDF Ingestion Rate | ≥ 5 pages/sec |
| P7 | GPU Memory Usage | ≤ 4 GB |

## **4.2 Safety and Security Requirements**

| ID | Requirement |
| ----- | ----- |
| S1 | All document data must remain on the local machine. |
| S2 | Admin dashboard must require authentication. |
| S3 | Voice data must not be stored on disk. |
| S4 | Backend proxy must be the only public entry point. |
| S5 | Ollama models automatically unload after inactivity. |

## **4.3 Software Quality Attributes**

### **Reliability**

* Startup scripts terminate stale processes to prevent port conflicts.

* Ollama warmup loads LLM weights before the first query.

### **Maintainability**

Microservices architecture allows independent updates for:

* Frontend

* Backend

* Admin Server

* Rasa NLU

* Action Server

Models and components are **swappable using environment variables**.

---

### **Testability**

The project includes **MKRS Benchmark System (MBS)** which:

* Simulates the Rasa runtime

* Executes automated test suites

* Stores results for reproducibility

---

### **Adaptability**

The system automatically adapts to hardware:

* CPU thread optimization

* Automatic GPU detection

* Seamless CPU fallback

# 

# 

# **5\. System Tuning and Optimization**

Key tuned parameters include:

| Parameter | Optimal Value | Impact |
| ----- | ----- | ----- |
| Retrieval candidates (k) | 75 | Improves retrieval accuracy |
| Temperature | 0.0 | Deterministic responses |
| Max tokens | 500 | Controls response length |
| Repeat penalty | 1.05 | Reduces repetition |
| Parent chunk size | 1500 | Improves context |
| Child chunk size | 500 | Improves retrieval precision |

# **6\. Test Results and Benchmark Analysis**

## **6.1 MKRS Benchmark System**

The evaluation score is calculated as:

TMS \= (RHR × 40\) \+ (SEC × 30\) \+ (NEG × 10\) \+ (LAT × 10\) \+ (VRAM × 10\)

| Metric | Weight |
| :---- | ----- |
| Retrieval Hit Rate | 40 |
| Semantic Extraction Confidence | 30 |
| No Hallucination | 10 |
| Latency | 10 |
| VRAM | 10 |

## 

## **6.2 Test Suite Composition**

Total Questions: **65**

| Category | Count |
| :---- | ----- |
| English Knowledge Base | 23 |
| Stress Tests | 7 |
| Multilingual Questions | 30 |
| Multilingual Stress Tests | 5 |

**Languages supported include:**

Hindi, Bengali, Marathi, Tamil, Telugu, Gujarati, Kannada, Malayalam, Punjabi, Urdu, Spanish, French, German, Japanese, and Chinese.

## **6.3 Latest Benchmark Result**

**TMS Score:** **84.39 / 100**  
 **Grade:** GOOD

| Metric | Value | Points |
| ----- | ----- | ----- |
| RHR | 98.5% | 39.38 |
| SEC | 76.2% | 22.86 |
| NEG | 100% | 10 |
| LAT | 9.33 sec | 2.14 |
| VRAM | 0 MB | 10 |

**Total Score: 84.39**

# 

# **7\. Other Requirements**

## **7.1 Deployment Requirements**

The system must support **automated deployment** through simple batch scripts to ensure easy installation and execution.

* The system shall be deployable via a **single batch script (start\_system.bat)** that launches all five microservices required by the architecture.

* A separate **one-click setup script (setup\_system.bat)** shall automatically install all required **Python and Node.js dependencies**.

* The deployment scripts shall configure **CPU optimization parameters**, including setting environment variables and process priority.

* The system shall ensure that all services start in the correct order to avoid dependency failures.

### **Deployment Service Map**

```mermaid
flowchart LR
    subgraph "start_system.bat"
        OPT["1. CPU Optimization\nOLLAMA_NUM_THREADS=8\nPriority → HIGH"] --> SYNC["2. Brain Sync\nsync_brain.py"]
        SYNC --> S1["Terminal 1\nFrontend :3000\nnpm start"]
        SYNC --> S2["Terminal 2\nBackend :5001\nnode server.js"]
        SYNC --> S3["Terminal 3\nAdmin :8000\npython admin_server.py"]
        SYNC --> S4["Terminal 4\nActions :5055\nrasa run actions"]
        SYNC --> S5["Terminal 5\nRasa NLU :5005\nrasa run --enable-api"]
    end
```

### **Deployment Service Startup Flow**

The deployment script performs the following sequence:

1. **CPU Optimization**

   * Sets OLLAMA\_NUM\_THREADS=8

   * Raises the process priority to **HIGH** for improved LLM performance.

2. **Brain Synchronization**

   * Executes sync\_brain.py to verify model and vector database readiness.

3. **Service Startup**

| Terminal | Service | Port | Command |
| ----- | ----- | ----- | ----- |
| Terminal 1 | React Frontend | 3000 | npm start |
| Terminal 2 | Node.js Backend | 5001 | node server.js |
| Terminal 3 | FastAPI Admin Server | 8000 | python admin\_server.py |
| Terminal 4 | Rasa Action Server | 5055 | rasa run actions |
| Terminal 5 | Rasa NLU Server | 5005 | rasa run \--enable-api |

## **7.2 Documentation Requirements**

The system must include comprehensive documentation to ensure reproducibility and maintainability.

* A **README.md** file shall be maintained at the root of the project repository containing:

  * Setup instructions

  * Architecture overview

  * Usage guide

  * Troubleshooting steps

* A **SUBMISSION\_SETUP.md** document shall provide:

  * Exact reproduction steps for the evaluated submission

  * Required environment configuration

  * The **Git commit hash** corresponding to the final submission version.

---

# 

## **7.3 File Structure Overview**

The project follows a structured directory organization to separate **frontend, backend, AI services, and evaluation modules**.

MKRS/

├── frontend/                  \# React.js UI

│   ├── src/

│   │   ├── App.js             \# Main application component

│   │   ├── App.css            \# Styling (chat bubbles, voice UI, admin panel)

│   │   └── index.js           \# Entry point

│   └── package.json

│

├── backend/                   \# Node.js proxy server

│   ├── server.js              \# Express server and static file serving

│   ├── routes/

│   │   ├── chatRoutes.js      \# /api/chat endpoints

│   │   └── adminRoutes.js     \# /api/admin endpoints

│   └── package.json

│

├── ai-service/                \# Python AI services

│   ├── actions/

│   │   └── actions.py         \# ActionQueryDoc (RAG \+ PDR \+ Translation)

│   ├── smart\_ingest.py        \# SmartIngest V10 (Column-aware PDF engine)

│   ├── smart\_chunker.py       \# SmartChunker V3 (PDR \+ semantic splitting)

│   ├── indic\_embeddings.py    \# IndicBERT / E5 embedding wrapper

│   ├── rag\_pipeline.py        \# Ingestion pipeline orchestrator

│   ├── admin\_server.py        \# FastAPI Admin server

│   ├── eval\_v1.py             \# MBS Benchmark system

│   ├── tuner.py               \# Hyperparameter grid search

│   ├── super\_tuner.py         \# Advanced tuning framework

│   ├── config.yml             \# Rasa NLU pipeline configuration

│   ├── domain.yml             \# Rasa intents and responses

│   ├── requirements.txt       \# Python dependency list

│   └── documents/

│       ├── pdfs/              \# Uploaded PDF documents

│       ├── chroma\_db/         \# Vector database

│       └── parent\_store.json  \# Parent context store

│

├── MBS/                       \# Benchmark archives

│   ├── INDEX.md

│   ├── TEST\_01\_BASELINE/

│   └── TEST\_75\_OPTIMIZED\_BRAIN\_RUN/

│

├── start\_system.bat           \# Launch all services

├── setup\_system.bat           \# Install dependencies

├── LAUNCH\_CHAT\_MODE.bat       \# Chat mode startup

├── LAUNCH\_BENCHMARK\_MODE.bat  \# Benchmark mode startup

├── README.md                  \# Project documentation

└── SUBMISSION\_SETUP.md        \# Reproduction guide

# 

# 

# 

# **Appendix A – Data Dictionary**

| Item | Type | Description | Related Requirements |
| :---- | :---- | ----- | ----- |
| OLLAMA\_MODEL | Environment Variable | Name of the Ollama LLM model (default: llama3.2:3b). | F10 |
| OLLAMA\_URL | Environment Variable | Ollama API endpoint (http://localhost:11434). | F10 |
| CONFIDENCE\_THRESHOLD | Constant | Minimum re-ranker score required for confident answers. | F8, F16 |
| OLLAMA\_TIMEOUT | Constant | Maximum wait time for LLM response (120 seconds). | P4 |
| DB\_CHROMA\_PATH | Path | Disk location of ChromaDB vector store. | F4 |
| PARENT\_STORE\_PATH | Path | Location of parent context JSON file. | F4, F9 |
| PDFS\_PATH | Path | Storage location for uploaded PDF documents. | F1, F14 |
| parent\_id | String | Unique identifier linking child chunk to parent context. | F4, F9 |
| lang | State Variable | Detected language code of user query. | F11 |
| search\_query | Variable | English-translated query used for vector search. | F11 |
| scored\_docs | List | Ranked list of retrieved documents with scores. | F8 |
| BAND\_GAP\_PX | Constant | Minimum vertical whitespace gap (12px) for Y-band segmentation. | F1 |
| COLUMN\_GAP\_MIN\_PX | Constant | Minimum horizontal whitespace gap (15px) for column detection. | F1 |
| LINE\_HEIGHT\_PX | Constant | Y-axis tolerance (3px) for grouping words into lines. | F1 |
| HEADER\_FONT\_RATIO | Constant | Font-size ratio (1.3×) for detecting headings. | F1 |

# 

# 

# 

# 

# **Appendix B – Dependency Manifest**

## **B.1 Python Dependencies**

| Package | Version | Purpose |
| :---- | ----- | ----- |
| langchain | 0.0.354 | RAG orchestration framework |
| langchain-community | 0.0.20 | Community integrations |
| transformers | 4.45.0 | Hugging Face model loading |
| sentence-transformers | 2.3.1 | Cross-encoder model |
| torch | 2.1.2 | Neural network inference |
| rasa | 3.6.15 | Conversational AI framework |
| rasa-sdk | 3.6.2 | Custom action server SDK |
| pdfplumber | 0.11.9 | PDF extraction |
| langdetect | 1.0.9 | Language detection |
| fastapi | 0.99.1 | Admin server |
| uvicorn | 0.41.0 | FastAPI runtime |
| chromadb | 0.4.24 | Vector database |

# 

# **Appendix D – Demo Screenshots**

*(Insert screenshots in your report)*

### **Chat Interface**

* Chat conversation with citation badges

* Source document preview

### **Multilingual Queries**

* Hindi response example

* Spanish response example

* Japanese response example

### **Voice Interaction**

* Listening state

* Real-time transcription

* TTS playback

### **Admin Dashboard**

* PDF upload interface

* Retraining logs

* Successful retraining message

### **Benchmark System**

* Benchmark execution output

* Final benchmark report

### **System Startup**

* Batch script launching services

* All service terminals running

### **SmartIngest Processing**

* Column detection logs

* Before/after text extraction comparison

[image1]: <data:image/png;base64,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>

[image2]: <data:image/png;base64,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>