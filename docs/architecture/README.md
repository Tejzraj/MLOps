# System Architecture & Technical Design

> **Project:** AI-Based Interview Preparation Assistant  
> **Course:** AI252TA – Machine Learning Operations | Semester V  
> **Status:** Phase 0 Blueprint  

---

## 1. Architectural Scope

This directory contains technical design specifications, architecture diagrams, dataflow schemas, and component interaction models for the **AI-Based Interview Preparation Assistant**.

The system is engineered as an end-to-end production MLOps pipeline designed to ingest candidate interview responses, evaluate semantic correctness and depth, classify quality into 4 standardized tiers, and deliver low-latency feedback.

---

## 2. End-to-End Architectural Blueprint

```mermaid
flowchart TD
    subgraph Data_Tier["1. Data Ingestion & Storage"]
        RawData["Raw QA Dataset (data/raw)"] --> DVC["DVC Version Control"]
        DVC --> Preproc["Preprocessing & Splitting (src/data)"]
        Preproc --> ProcessedData["Sanitized Splits (data/processed)"]
    end

    subgraph Feature_Tier["2. Feature Pipeline"]
        ProcessedData --> FeatEng["Feature Extraction (src/features)"]
        FeatEng --> Vectorizer["TF-IDF / Embedding Transformer"]
    end

    subgraph Model_Tier["3. Training & Experimentation"]
        Vectorizer --> Train["Model Training (src/models)"]
        Train --> MLflowTrack["MLflow Experiment Tracking (Params, Metrics, Artifacts)"]
        Train --> Eval["Model Evaluation (src/evaluation)"]
        Eval --> RegCriteria{"Meets Quality Threshold?"}
        RegCriteria -- "Yes" --> ModelReg["MLflow Model Registry (Phase 2)"]
        RegCriteria -- "No" --> Retune["Hyperparameter Revision"]
    end

    subgraph Serving_Tier["4. Serving & Deployment (Planned: Phase 2)"]
        ModelReg --> FastAPIService["FastAPI REST Inference Service"]
        FastAPIService --> DockerContainer["Dockerized Container Image"]
        DockerContainer --> CICD["GitHub Actions CI/CD Pipeline"]
        CICD --> CloudDeploy["Production Deployment Environment"]
    end

    subgraph Observability_Tier["5. Observability & Continuous ML (Planned: Phase 3)"]
        CloudDeploy --> Logging["Structured Application Logging"]
        CloudDeploy --> DriftCheck["Evidently Drift & Quality Analyzer"]
        DriftCheck --> Monitoring["Prometheus & Grafana Dashboard"]
        Monitoring --> Trigger{"Data/Concept Drift Detected?"}
        Trigger -- "Yes" --> RetrainPipeline["Automated Retraining Pipeline"]
        Trigger -- "No" --> SteadyState["Continuous Surveillance"]
    end

    classDef orange fill:#FF6B00,stroke:#0D1117,stroke-width:2px,color:#FFFFFF;
    classDef dark fill:#1A1A1A,stroke:#FF8C00,stroke-width:1px,color:#FFFFFF;
    classDef planned fill:#252525,stroke:#888888,stroke-width:1px,stroke-dasharray: 5 5,color:#AAAAAA;

    class RawData,ProcessedData,Vectorizer orange;
    class DVC,Preproc,FeatEng,Train,MLflowTrack,Eval dark;
    class ModelReg,FastAPIService,DockerContainer,CICD,CloudDeploy,Logging,DriftCheck,Monitoring,RetrainPipeline planned;
```

---

## 3. Component Details & Phased Roadmap

1. **Data & Storage Pipeline (Phase 1):**
   - Versioned storage with DVC.
   - Text normalization, deduplication, and stratified train/val/test splits.
2. **Feature Pipeline (Phase 1):**
   - Text vectorization (TF-IDF, n-grams, answer length ratios).
   - Serializable scikit-learn transformers.
3. **Training & Tracking (Phase 1):**
   - Baseline models: Logistic Regression, Random Forest.
   - Experiment tracking with MLflow (parameters, F1-scores, loss curves).
4. **Production Inference Service (Phase 2):**
   - High-throughput FastAPI REST API with input validation (`pydantic`).
   - Containerization via Docker multi-stage builds.
5. **Observability & Feedback Loop (Phase 3):**
   - Real-time logging of predictions.
   - Evidently test suites to detect vocabulary drift and concept shift.

---

## 4. Planned Documents in this Directory

- `data_flow.md` — Detailed sequence diagram of training and inference flows.
- `api_spec.md` — OpenAPI/Swagger schemas for the inference service.
- `deployment_topology.md` — Container orchestration and infrastructure definitions.
