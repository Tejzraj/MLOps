# Dataset Approval Dossier

> **Academic Course:** AI252TA – Machine Learning Operations  
> **Academic Semester:** Semester V  
> **Project Title:** AI-Based Interview Preparation Assistant  
> **Student / Maintainer:** Tejzraj ([@Tejzraj](https://github.com/Tejzraj))  
> **Repository:** [https://github.com/Tejzraj/MLOps.git](https://github.com/Tejzraj/MLOps.git)  
> **Document Status:** PENDING FACULTY REVIEW & APPROVAL (Not Yet Approved)  
> **Submission Date:** 2026-09-27  

---

## 1. Problem Statement

Automating interview preparation requires evaluating candidate answers to structured technical questions. However, existing public datasets primarily feature question-and-answer pairs designed for chatbot question answering (SFT) or knowledge retrieval, **completely lacking graded candidate responses of varying quality (Poor, Needs Improvement, Good, Excellent)**.

To train an objective, reproducible machine learning evaluator, we must curate a dataset comprising:
$$\text{Input: (Question, Candidate Answer, Reference Answer, Expected Concepts, Domain, Difficulty)}$$
$$\text{Output: Answer Quality Class } (0, 1, 2, 3) \text{ and Dimensional Scores } (0 - 15)$$

---

## 2. Why This Dataset Is Needed

1. **Targeted Task Alignment:** No existing open-source dataset offers multi-class graded candidate responses mapped to pedagogical rubrics.
2. **Pedagogical Feedback:** Enables the ML model to output granular dimensional scores (Correctness, Completeness, Communication) alongside the primary classification.
3. **MLOps Lifecycle Defense:** Serves as the foundational versioned asset for DVC pipeline tracking, data drift monitoring (Evidently), and reproducible retraining.

---

## 3. Data Sources & Candidate Provenance

Source material will be harvested strictly from permissible sources subject to formal verification:
- **`raghu298/ml-interview-sft-dataset` (Apache-2.0 candidate):** Candidate source for machine learning and AI questions; formal verification of the subset and license pending faculty review.
- **Accredited Academic Engineering Curricula:** Standardized course syllabi for core CS domains (Operating Systems, Database Management Systems, Computer Networks, OOP, Data Structures) pending formal verification.
- **External Benchmarks Under License Review:** Any additional candidate repositories (e.g., `Max00035/ml-systems-interview-bench`, `Ankshi/hr-interview-dataset`) remain marked as `LICENSE VERIFICATION REQUIRED` and will **not** be ingested without formal clearance.

---

## 4. Candidate Response Generation & Academic Sequence

Because public repositories only provide reference/exemplar answers without graded candidate variations:
1. **Intended Academic Pipeline:**
   $$\text{Specification} \rightarrow \text{Faculty Approval} \rightarrow \text{Source Verification} \rightarrow \text{Normalization} \rightarrow \text{Categorization} \rightarrow \text{Ref. Answers} \rightarrow \text{Candidate Text} \rightarrow \text{Human Annotation} \rightarrow \text{QC} \rightarrow \text{Final Data} \rightarrow \text{DVC} \rightarrow \text{EDA} \rightarrow \text{ML}$$
2. **Question Bank Formation:** Verified questions with **expert-reviewed reference answers** (reviewed against approved curriculum material) and explicit `expected_concepts` are curated to support human evaluation.
3. **Reference Answer Role:** The reference answer provides an evaluation benchmark for annotators; it is **not** automatically ground truth for candidate quality.
4. **Candidate Response Generation:** Responses are drafted as controlled variants across four pedagogical tiers (representing Poor, Needs Improvement, Good, and Excellent responses).
5. **Strict Separation of Generation and Labeling:** The generation of response text does **not** determine its ground-truth label. All candidate texts remain unverified drafts until evaluated through the human annotation rubric.

---

## 5. Use of AI-Assisted Synthetic Responses (Faculty Review Item)

> [!CAUTION]
> **Clear Academic Disclosure on Synthetic Text:**
> - If AI tools are employed as a controlled data-generation aid to assist in drafting candidate responses across proficiency tiers, they are used **strictly under faculty supervision and approval**.
> - **Synthetic candidate answers are NOT real student responses.** They are synthetic simulations created to establish a baseline evaluation distribution.
> - **Synthetic responses are NEVER treated as ground truth.** Every synthetic draft response must be inspected, evaluated, and scored by human annotators adhering strictly to [`LABELING_GUIDELINES.md`](LABELING_GUIDELINES.md).
> - Automated LLM self-evaluation without human review is strictly prohibited.

---

## 6. Proposed Dataset Schema

The schema contains 19 strictly typed fields:
- **Identifiers:** `question_id`, `annotator_id`, `version`, `split_group`
  *(Note: `annotator_id` uses anonymous tokens like `ANN_01`, `ANN_02`; strictly zero student names, USNs, emails, or personal identifiers are stored.)*
- **Taxonomy:** `domain` (10 approved technical domains: DSA, OOP, DBMS, CN, OS, Python, C/C++, Java, ML, AI), `difficulty` (Easy/Medium/Hard), `question_type` (Conceptual, Comparative, Diagnostic, Behavioral / HR)
- **Textual Content:** `question`, `reference_answer` (expert-reviewed), `expected_concepts`, `candidate_answer`
- **Quantitative Target Scores:** `correctness_score` ($0-5$), `completeness_score` ($0-5$), `communication_score` ($0-5$), `total_score` ($0-15$)
- **Primary Target Class:** `quality_label` ($0, 1, 2, 3$)
- **Provenance & Governance:** `source`, `source_license`, `annotation_method`

---

## 7. Human Annotation & Validation Methodology

Scoring follows [`LABELING_GUIDELINES.md`](LABELING_GUIDELINES.md):
- **Correctness (0 – 5):** Evaluates factual accuracy and freedom from misconceptions.
- **Completeness (0 – 5):** Evaluates coverage of mandatory technical concepts and trade-offs.
- **Communication (0 – 5):** Evaluates structure, conciseness, and professional clarity.
- **Proposed Tier Mapping (PROPOSED — SUBJECT TO FACULTY VALIDATION AND ANNOTATION CALIBRATION):**
  - $0 - 3 \rightarrow$ `0: Poor`
  - $4 - 7 \rightarrow$ `1: Needs Improvement`
  - $8 - 11 \rightarrow$ `2: Good`
  - $12 - 15 \rightarrow$ `3: Excellent`
  *(These thresholds are proposed working hypotheses, not scientifically validated constants.)*
- **Human Review Strategy:** Annotation is executed by student project team members using anonymous identifiers (`ANN_01`). A random $15\% - 20\%$ dual-audit subset will be independently reviewed by a second team member to identify disputes and assess consistency. Discrepancies are adjudicated using rubric criteria. Consistency metrics will be calculated and reported **after** annotation is completed. Faculty members serve as reviewers and advisors, not primary annotators.

---

## 8. Quality-Control & Anti-Leakage Methodology

- **Zero Nulls:** Programmatic validation rejecting missing or incomplete entries.
- **Class Parity:** Balancing class distributions across all 4 tiers ($25\% \pm 3\%$).
- **Proposed Grouped Anti-Leakage Partitioning:** Splitting strictly by `question_id` (Train $70\%$, Validation $10\%$, Test $20\%$), guaranteeing that no question present in the training set appears in validation or testing.

---

## 9. Privacy & Ethics

- **Zero PII Policy:** No student or candidate names, institutions, USNs, contact info, or IP addresses are collected or stored.
- **Controlled Text Generation:** Eliminates privacy risks associated with non-consensual harvesting of real student exam or interview records.

---

## 10. Licensing & Provenance Compliance

- Every record contains explicit provenance metadata (`source` and `source_license`).
- Source datasets must possess permissive open-source licenses (MIT, Apache-2.0, CC-BY-4.0). Proprietary or ambiguous materials are excluded.

---

## 11. Known Dataset Limitations

1. **Synthetic-Data Bias:** If AI-assisted draft responses are used, stylistic patterns characteristic of LLMs may be present.
2. **Annotator Diversity:** Annotation performed by student team members reflects academic peer judgment rather than seasoned industry recruiters.
3. **Subjectivity in Communication Scoring:** Evaluating communication clarity retains inherent human subjectivity, bounded by explicit rubric criteria.
4. **Domain Scope:** Focuses on 10 foundational engineering subjects in Phase 1 (DSA, OOP, DBMS, CN, OS, Python, C/C++, Java, ML, AI).
5. **Synthetic vs. Real-World Mismatch:** Synthetic responses may not capture authentic human disfluencies, nervous pauses, or real-time cognitive shifts that occur during actual verbal interviews.
6. **Textual Modality Scope:** Does not capture vocal tone, pacing, hesitation, or non-verbal cues (deferred to future phases).

---

## 12. Data Versioning with DVC

- All datasets are tracked outside Git via Data Version Control (DVC).
- Git tracks only the lightweight pointer file: `data/raw/interview_data.parquet.dvc`.
- Remote cache ensures immutable, reproducible pipeline execution via `dvc repro`.
- *Notice: DVC dataset tracking will occur only after the approved dataset is assembled.*

---

## 13. Faculty Review & Approval Checklist

*The following checklist must be reviewed and signed off by the course faculty / evaluation committee prior to dataset generation and model training.*

```
========================================================================================
                      FACULTY EVALUATION COMMITTEE APPROVAL FORM
========================================================================================
Course Code : AI252TA – Machine Learning Operations
Semester    : V
Project     : AI-Based Interview Preparation Assistant
Review Date : ________________________

[ ] 1. Problem Statement & Scope Reviewed
       The supervised ML formulation (4-tier quality classification) is appropriate
       and tractable for an academic MLOps project.

[ ] 2. Data Sources & Provenance Approved
       Question-bank sources and licensing (Apache-2.0 / Academic curricula) are verified
       and legally permissible.

[ ] 3. Response-Generation Methodology Approved
       The protocol for collecting or creating candidate response text across 4 proficiency
       tiers is academically sound and well-defined.

[ ] 4. Use of AI-Assisted Synthetic Responses Approved (If Applicable)
       The use of LLM prompting as a controlled data-generation aid—strictly decoupled
       from ground-truth labeling and subject to human annotation—is accepted.

[ ] 5. Dataset Schema & Metadata Approved
       The 19-field schema (including anonymous annotator_id) provides adequate context
       for training, evaluation, and MLOps governance.

[ ] 6. Annotation Rubric & Proposed Thresholds Approved
       The 15-point scoring methodology (Correctness, Completeness, Communication)
       and proposed class boundaries (0-3, 4-7, 8-11, 12-15) are approved for labeling calibration.

[ ] 7. Human Validation & Quality-Control Protocol Approved
       Student team annotation, dual-audit subset review, dispute resolution, and
       group-based zero-leakage splitting are approved.

[ ] 8. Privacy, Bias, & Limitations Disclosures Approved
       The Zero-PII policy, anonymous annotator identifiers, synthetic-data bias disclosure,
       and documented limitations are academically defensible.

[ ] 9. Train / Validation / Test Methodology Approved
       Grouped question-level partitioning (70% train / 10% val / 20% test) to prevent
       data leakage across partitions is approved.

[ ] 10. DVC Versioning Strategy Approved
       Data storage decoupling and DVC tracking ensure pipeline reproducibility.

----------------------------------------------------------------------------------------
FINAL COMMITTEE ACTION:
[ ] APPROVED WITHOUT MODIFICATIONS
[ ] APPROVED SUBJECT TO REVISIONS (See Comments Below)
[ ] REJECTED / RESUBMISSION REQUIRED

Faculty Signature(s) : __________________________________________
Faculty Name(s)      : __________________________________________
Comments / Revisions : 
________________________________________________________________________________________
========================================================================================
```
