
<img width="1024" height="500" alt="flowforge_logo02" src="https://github.com/user-attachments/assets/28076f4f-60de-4873-9bb1-783cb4f8b9aa" />

# FlowForge AI

**Agentic MLflow Model Development & Governance Platform**

FlowForge AI is an open-source, containerized Machine Learning platform that automates the end-to-end ML lifecycle using AI Agents. It features a Human-in-the-Loop workflow, ensuring you stay in control while AI handles the heavy lifting of EDA, Feature Engineering, and Model Optimization.

![Architecture](https://img.shields.io/badge/Architecture-Microservices-blue)
![Python](https://img.shields.io/badge/Python-3.10-green)
![License](https://img.shields.io/badge/License-Apache%202.0-blue)

## 🏗️ Architecture

The system is composed of several Docker services orchestrated via Docker Compose:

```mermaid
graph TD
    User((User)) -->|Browser| UI[Streamlit UI : 8501]
    UI -->|HTTP| API[FastAPI Backend : 8000]
    API -->|Manage| Prefect[Prefect Orchestrator : 4200]
    API -->|Log| MLflow[MLflow Tracking : 5000]
    API -->|Prompt| Ollama[Ollama LLM GPU : 11434]
    Prefect -->|Run| Workers[ML Workers]
    Workers -->|Train| Optuna[Optuna Optimization]
    Workers -->|Track| MLflow
    API -->|RAG| Artifacts[File System /app/docs]
```

### Key Components
- **Streamlit UI**: Interactive Wizard-style interface.
- **FastAPI Backend**: Handles requests, runs Agents, and manages file I/O.
- **Prefect**: Orchestrates long-running flows (Model Training).
- **MLflow**: Tracks experiments, metrics, and models.
- **Ollama**: Local LLM inference (Llama 3 recommended) for Agents.
- **Dozzle**: Real-time log viewer.

## 🚀 Getting Started

### Prerequisites
- **Docker** and **Docker Compose** installed.
- **NVIDIA GPU** & **NVIDIA Container Toolkit** (for Ollama acceleration).
  - *Note: If you don't have a GPU, modify `docker-compose.yml` to remove the `deploy` section under `ollama`.*

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/quickSilverShanks/FlowForge-AI.git
   cd FlowForge-AI
   ```

2. **Start the Platform**
   ```bash
   docker-compose up --build -d
   ```
   *The first run will take time to build images.*

3. **Initialize Ollama Model**
   Once containers are running, download the LLM model (execute inside the ollama container or via API if implemented, typical manual step for first time):
   ```bash
   docker exec -it flowforge_ollama ollama pull llama3
   ```

### Usage Guide

Access the services at the following URLs:

| Service | URL | Description |
| --- | --- | --- |
| **App UI** | `http://localhost:8501` | Main Interface |
| **Backend API** | `http://localhost:8000/docs` | API Swagger |
| **MLflow** | `http://localhost:5000` | Experiment Tracking |
| **Prefect** | `http://localhost:4200` | Workflow Orchestration |
| **Logs** | `http://localhost:8888` | Container Logs |

### 🧪 Workflow Steps

1.  **Data Upload**: Go to the "Data Upload" page and upload your CSV/Parquet file. Define your Target column.
2.  **EDA**: Switch to "EDA". Click "Run AI Analysis". The Agent will generate a "Vibe Check" and statistical summary.
3.  **Feature Engineering**: Go to "Feature Engineering". The Agent will propose a plan (Imputation, Encoding, etc.). Review, Edit, and Apply it.
4.  **Model Training**: Go to "Model Training". The Agent proposes a search space. Click "Start Training" to trigger the Prefect Flow. Watch the progress in the Prefect Dashboard.
5.  **Validation**: Evaluate fairness and performance on OOT data.
6.  **Monitoring**: Generate a drift detection config.
7.  **Final Report**: Chat with the `RAG Agent` to ask questions about what happened during the session (e.g., "Why did we drop the Age column?").

## 🛠️ Development

- **Backend Code**: `app/api/`
- **UI Code**: `app/ui/`
- **Agents**: `app/core/agents/`
- **ML Logic**: `app/core/ml/`

To add a new dependency, update `requirements.txt` and rebuild:
```bash
docker-compose up --build -d
```
