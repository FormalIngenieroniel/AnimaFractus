# 🧠 Multi-Agent Social Cognitive Dissonance Analysis – Distributed AI System in Cloud

This project implements a **Distributed Multi-Agent System** capable of analyzing user queries from three distinct psychological perspectives.

It integrates **Retrieval-Augmented Generation (RAG)** using ChromaDB, LangGraph for agent workflow orchestration, and Google Gemini for text generation.

The architecture is deployed across **three separate AWS EC2 instances**, simulating a scalable, microservices-oriented production environment divided into Data, Logic, and Presentation layers.

---

## 🤖 Introduction to the AI Architecture

Artificial Intelligence (AI) in this project is not just a chatbot, but a system of cooperating entities known as Intelligent Agents:

- **Agent:** An autonomous entity that perceives context, from a vector database, and generates unique insights based on a specific persona.
- **Contextual Awareness:** The agents do not hallucinate, they ground their responses in real dataset embeddings, being Tweets about Covid, Disasters, Markets, and Hideo Kojima.
- **Orchestration:** A graph-based workflow ensures that agents "think" sequentially before a final synthesizer compiles the results.

In this project, the system is modeled as a Cognitive Pipeline:

- **Perception** → Vector similarity search in ChromaDB.
- **Decision-making** → The agents Survivor, Speculator and Auteur analyze data and form a thought.
- **Synthesis** → A "Historian" agent compiles the conflicting viewpoints into a narrative conclusion.

---

## 🚀 Features

- ☁️ **Distributed Cloud Architecture:** Deployed across 3 distinct AWS EC2 instances (Data, Logic, Presentation).
- 🐳 **Dockerized Microservices:** Each layer runs in isolated containers for portability and scalability.
- 🧠 **RAG (Retrieval-Augmented Generation):** Uses SentenceTransformer to fetch relevant context before generating answers.
- 🎭 **Multi-Persona AI:** Three distinct agents with unique vocabularies and worldviews (Biosecurity, Finance, Art).
- 🔗 **LangGraph Workflow:** State-based execution graph ensuring structured flow from analysis to synthesis.
- ⚡ **FastAPI & Flask Integration:** Separates the logic API from the user-facing web interface.
- 💾 **Persistent Vector Database:** ChromaDB maintains embeddings even after container restarts.
- 🎨  **Interactive user interface:** Uses a simple and creative function to interact with the user.

---

## 💻 System Architecture & Workflow

The project is divided into three distinct layers, each running on its own server (EC2 Instance), this is a brief explanation of the main files.

1.  **Data Layer (The Memory):** Responsible for storing and retrieving semantic knowledge.

    - **start_chroma.sh:** Initializes the ChromaDB Docker container with persistent storage volumes.
    - **etl_script.py: A** It reads raw CSV datasets (Covid, Disasters, Stocks and Kojima), converts them into vector embeddings using all-MiniLM-L6-v2, and loads them into the database.

2. **Logic Layer (The Brain):** Responsible for processing, reasoning, and generating text.

    - **main.py:** The entry point for the FastAPI server. It exposes the /ask endpoint that triggers the agent workflow.
    - **agents.py:** The core intelligence.
        - Defines the StateGraph workflow.
        - Configures the 3 personas (Survivor, Speculator, Auteur).
        - Executes the logic: Query Database → Prompt Engineering → LLM Generation → Response Cleaning.
        - Define the graph of the chain of thought for the different agents in the following order: Survivor → Speculator → Auteur → Synthesizer → END

4. **Presentation Layer (The Face):** Responsible for user interaction in a interactive library.

    - **app.py:** A Flask web server that renders the HTML interface and forwards user questions to the Logic Layer via HTTP requests.
    - **deploy.sh:** Automates the build and deployment of the web container, handling port mapping (8501) and cleanup of old images.

---

## 🧩 How It Works

**User Input:** A user asks a question via the Web Interface (Presentation Layer).

**Request Forwarding:** The Flask app forwards the query to the Logic Layer API.

**Context Retrieval:** The Logic Layer embeds the query and searches the Data Layer (ChromaDB) for relevant tweets/texts.

**Agent Analysis:**
    - Survivor analyzes the data looking for threats and biological risks.
    - Speculator looks for market patterns and financial opportunities.
    - Auteur interprets the situation through a lens of artistic melancholy and connection.

**Synthesis:** The Historian agent takes these three conflicting logs and writes a summary highlighting the "social cognitive dissonance."

**Response:** The final narrative and the individual agent logs are sent back to the frontend for display in a interactive library.

---

## 📷 Screenshots 

---

## 📚 Example of the output 

```python
def greet(name):
    print(f"Hello, {name}!")

greet("GitHub User")
```

---

## 🧠 Agent Personalities

The system uses prompt engineering to enforce strict behavioral protocols:

**The Survivor (Biosecurity Officer)**
    - Focus: Viral loads, containment protocols, quarantine.
    - Style: Paranoid, military-technical, urgent.
    - Context Source: Covid-19 & Disaster datasets.

**The Speculator (Quantitative Analyst)**
    - Focus: ROI, volatility, support levels, liquidity.
    - Style: Cold, mathematical, indifferent to human tragedy.
    - Context Source: Stock Market datasets.

**The Auteur (Visionary Director)**
    - Focus: Strands, isolation, soul, connections.
    - Style: Enigmatic, short aphorisms, cinematic.
    - Context Source: Hideo Kojima / Social commentary datasets.

---

## 🔧 Tech Stack & Requirements

- **Cloud Infrastructure:** AWS EC2 (3 Instances).
- **Containerization:** Docker, Docker Compose.
- **Languages:** Python 3.9 / 3.11.
- **AI Frameworks:** LangChain, LangGraph.
- **LLM Provider:** Google Gemini (via langchain-google-genai).
- **Vector Database:** ChromaDB.
- **Embeddings:** HuggingFace all-MiniLM-L6-v2.
- **Web Frameworks:** FastAPI (Backend), Flask (Frontend).

---

## 📊 Future Improvements

- 🔄 **Real-time Ingestion:** Connect the ETL script to live Twitter/X APIs for real-time context using Lambda functions for web scrapping.
- 🧹 **Advanced Data Preprocessing:** Implement rigorous text cleaning pipelines to strip noise and irrelevant characters from tweets, ensuring higher fidelity embeddings and more accurate semantic retrieval.
- 🛠️ **Metadata-Driven Tool Use:** Integrate Named Entity Recognition (NER) during the ETL process to extract key entities. Agents can then use this metadata to trigger specific tools or enrich their context dynamically.
- 🗣️ **Non-Linear Agent Debate**: Transition from a linear LangGraph workflow to a cyclic, conversational topology. This would allow agents to debate, challenge each other's viewpoints, and refine insights through multi-turn dialogue rather than just outputting isolated thoughts.
- 🎓 **Specialized Historian Model:** Move beyond standard prompt engineering by fine-tuning a specific model on sociological datasets. This ensures the "Historian" becomes an expert in analyzing social cognitive dissonance rather than relying solely on general-purpose inference.

---

## 👨‍💻 Author

Developed by Daniel Bernal.
