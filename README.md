# ⚽ Football Intelligence AI

> An end-to-end football analytics, scouting, machine learning, RAG, and agentic AI platform built using StatsBomb Open Data.

## Overview

Football Intelligence AI transforms event-level football data into structured analytics, statistical scouting insights, machine-learning predictions, semantic knowledge retrieval, and an AI-powered football assistant.

The system is built around a simple principle:

- **Structured questions → SQL / analytics → exact results**
- **Prediction questions → machine learning → model predictions**
- **Methodology questions → RAG → grounded explanations**
- **Multi-step questions → AI agent → tool selection + synthesis**

The LLM is used as an orchestration and explanation layer rather than as the source of truth for football statistics.

---

## Features

### Player Analytics
- Player statistics
- Goals and assists
- Playing time
- Role-based analysis

### Statistical Player Similarity
- Role-aware player similarity
- Same-role candidate filtering
- Top-N statistically similar players

### Player Archetypes
- Unsupervised player clustering
- K-Means based archetypes
- Statistical player profiles

### Performance Prediction
- Player future xG prediction
- Random Forest regression
- Previous-appearance feature window

### Match Intelligence
- Match outcome prediction
- Home win / draw / away win analysis

### Knowledge Base / RAG
- Football methodology documentation
- Semantic retrieval
- Sentence Transformer embeddings
- FAISS vector search
- Grounded answers from project documentation

### Agentic AI
The AI football assistant can select between:

- SQL
- Player similarity
- Player clustering
- Player performance prediction
- Match outcome prediction
- RAG

The agent then synthesizes the tool results into a natural-language answer.

---

## Dataset

The project uses **StatsBomb Open Data**.

The selected dataset is:

**Premier League 2015/16**

- Competition ID: `2`
- Season ID: `27`
- Matches: `380`
- Teams: `20`

StatsBomb event data is transformed from semi-structured JSON into relational football datasets and stored in SQLite.

---

## Architecture

```text
StatsBomb Open Data
        │
        ▼
      ETL
        │
        ▼
   SQLite Database
        │
        ├───────────────┐
        │               │
        ▼               ▼
    Analytics          ML
        │               │
        │       ┌───────┴────────┐
        │       │                │
        │       ▼                ▼
        │   Clustering      Prediction
        │   Similarity
        │
        └───────────────┐
                        │
                        ▼
                  AI Agent Layer
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
         SQL            ML            RAG
          │             │             │
          ▼             ▼             ▼
       Exact data    Predictions   Grounded
                                  explanations
                        │
                        ▼
                  Streamlit App
```

---

## RAG Architecture

```text
Project Documentation
        │
        ▼
      Chunking
        │
        ▼
Sentence Transformers
        │
        ▼
  384-dimensional
     embeddings
        │
        ▼
   FAISS Index
        │
        ▼
 Semantic Retrieval
        │
        ▼
 Retrieved Context
        │
        ▼
      LLM
        │
        ▼
 Grounded Answer
```

---

## Agent Architecture

The AI assistant uses tool calling to decide which capability is required for a question.

```text
User Question
      │
      ▼
   Qwen3 8B
      │
      ▼
 Tool Selection
      │
 ┌────┼────┬────┬────┬────┐
 ▼    ▼    ▼    ▼    ▼    ▼
SQL  Sim  Cluster  ML  Match RAG
 │    │      │     │    │    │
 └────┴──────┴─────┴────┴────┘
                  │
                  ▼
             Tool Results
                  │
                  ▼
              LLM Synthesis
                  │
                  ▼
                Answer
```

---

## Technology Stack

### Data Engineering
- Python
- Pandas
- NumPy
- SQLite
- SQL

### Analytics
- Pandas
- SQL
- Matplotlib

### Machine Learning
- Scikit-learn
- K-Means clustering
- Random Forest regression
- Feature preprocessing

### NLP / RAG
- Sentence Transformers
- FAISS
- Semantic retrieval
- Embeddings

### Agentic AI
- OpenAI-compatible Python client
- Ollama
- Qwen3 8B
- Function/tool calling

### Application
- Streamlit

---

## Local Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd "Football Intelligence AI"
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate it

Windows:

```powershell
.\venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Install Ollama

Install Ollama separately.

Then download the required model:

```bash
ollama pull qwen3:8b
```

Start Ollama if necessary:

```bash
ollama serve
```

### 6. Launch the application

From the project root:

```bash
streamlit run app/app.py
```

---

## AI Model Configuration

The agent currently uses:

```text
Model: Qwen3 8B
Runtime: Ollama
Endpoint: http://localhost:11434/v1
```

The Python application communicates with Ollama through its OpenAI-compatible API.

Ollama is therefore a **runtime dependency**, not a Python package dependency.

---

## Project Structure

```text
Football Intelligence AI/
│
├── agent/
│   ├── agent.py
│   └── tools/
│       ├── rag_tool.py
│       ├── tool_registry.py
│       ├── sql_tool.py
│       ├── player_similarity_tool.py
│       ├── player_clustering_tool.py
│       ├── player_performance_tool.py
│       └── match_outcome_tool.py
│
├── analytics/
│   ├── eda_team_performance.py
│   ├── queries.sql
│   └── run_query.py
│
├── app/
│   └── app.py
│
├── database/
│   ├── create_database.py
│   ├── create_schema.py
│   ├── load_database.py
│   └── validate_database.py
│
├── etl/
│   ├── build_event_dataset.py
│   ├── build_final_datasets.py
│   ├── build_player_dataset.py
│   ├── inspect_data.py
│   └── inspect_events.py
│
├── ml/
│   ├── player_clustering.py
│   ├── player_performance_prediction.py
│   ├── match_outcome_model_training.py
│   ├── match_outcome_prediction.py
│   └── validate_player_similarity.py
│
├── rag/
│   ├── build_chunks.py
│   ├── build_embeddings.py
│   ├── build_faiss_index.py
│   ├── faiss_search.py
│   └── semantic_search.py
│
├── football.db
├── requirements.txt
└── README.md
```

---

## Example AI Questions

### SQL / Analytics

> Who scored the most goals?

> Who had the most assists?

> Who are the top 5 goal scorers?

> Which team scored the most goals?

### Player Analysis

> How many goals did Harry Kane score?

> What is Kevin De Bruyne's statistical playstyle?

> Who are Kevin De Bruyne's 5 most statistically similar players?

### Prediction

> What is Kevin De Bruyne's predicted xG across his next five appearances?

### Methodology / RAG

> How does the role-aware scouting score work?

> How were player archetypes created?

> What is the 900-minute scouting threshold?

> What are the limitations of the scouting framework?

### Multi-step Agent Queries

> Give me a complete profile of Kevin De Bruyne.

> Compare Kevin De Bruyne's statistical profile with his most similar players.

---

## Important Scope

The current analytical dataset focuses on the **2015/16 Premier League season**.

The scouting framework is a project-defined analytical framework and should not be interpreted as an official club scouting rating or universal measure of player quality.

Machine-learning predictions are model outputs and should be interpreted as probabilistic estimates rather than guarantees.

---

## Data Source

StatsBomb Open Data.

StatsBomb data is used for educational and analytical purposes in accordance with its data-use terms.

---

## Project Status

### Completed

- Data ingestion
- ETL pipeline
- SQLite database
- Database validation
- Player feature engineering
- Player similarity
- Player clustering
- Player performance prediction
- Match outcome prediction
- RAG pipeline
- FAISS retrieval
- Agent tool calling
- Streamlit application
- End-to-end agent testing

### Future Improvements

- Cloud-compatible LLM deployment
- Larger multi-season dataset
- Additional competitions
- More advanced scouting models
- Improved agent error handling
- Automated evaluation
- Model monitoring
- Production deployment

---

## Disclaimer

Football Intelligence AI is an educational and analytical project.

Its scouting scores, player archetypes, similarity results and machine-learning predictions are analytical outputs generated from the project's data and methodology. They should not be interpreted as official professional scouting ratings.
