# Dataset Labeling & Annotation Guidelines

> **Project:** AI-Based Interview Preparation Assistant  
> **Course:** AI252TA – Machine Learning Operations | Semester V  
> **Document Type:** Standardized Annotation Protocol & Rubric  
> **Status:** PROPOSED METHODOLOGY (Requires Faculty Validation & Calibration Before Annotation)  
> **Version:** `v0.1.2`  

---

## 1. Purpose & Guiding Principles

This document establishes the official scoring protocol used to label candidate interview responses. Annotations must be objective, reproducible, and strictly based on pedagogical assessment of technical accuracy, concept coverage, and communication clarity.

> [!IMPORTANT]
> **Core Annotation Rules:**
> 1. **Rubric-Driven Ground Truth:** Ground-truth quality labels must strictly originate from human application of this rubric, **not** from an LLM-generated judgment or automated prompt rating.
> 2. **Reference Answer Role:** The reference answer is an **expert-reviewed reference answer** (reviewed against approved source materials) providing a baseline benchmark of required depth. It is an evaluation aid, **not** automatically ground truth for candidate quality.
> 3. **Semester V Practical Strategy:** Annotations will be performed by student project team members using anonymous identifiers (`ANN_01`, `ANN_02`). A dual-annotated subset will be used to resolve discrepancies and assess consistency. Faculty members act as academic advisors and reviewers, not primary annotators.
> 4. **Proposal Disclaimer:** The scoring definitions and threshold intervals ($0-3, 4-7, 8-11, 12-15$) represent our project's **PROPOSED** methodology and are **SUBJECT TO FACULTY VALIDATION** and **SUBJECT TO ANNOTATION CALIBRATION** before production labeling.

---

## 2. Multi-Dimensional Evaluation Framework

Every candidate response is scored across three independent, orthogonal dimensions ($0 - 5$ points each):

$$\text{Composite Score} = S_{\text{correctness}} + S_{\text{completeness}} + S_{\text{communication}} \quad (0 \le \text{Total} \le 15)$$

```
                                      TOTAL SCORE (0 – 15)
                                                │
                ┌───────────────────────────────┼───────────────────────────────┐
                ▼                               ▼                               ▼
       Correctness (0 – 5)             Completeness (0 – 5)            Communication (0 – 5)
    Factual Truth & Validity        Key Concepts & Trade-offs       Clarity, Structure & Delivery
```

---

## 3. Dimensional Scoring Rubrics

### Dimension A: Correctness ($0 - 5$)

Evaluates whether the statements made in the answer are factually accurate, sound, and free of misconceptions.

| Score | Rating | Technical Definition | Example Criteria |
| :---: | :--- | :--- | :--- |
| **0** | **Completely Incorrect / Irrelevant** | The response is factually false, misleading, or completely off-topic. | Stating that UDP provides guaranteed packet delivery. |
| **1** | **Minimal Correct Information** | Contains one accurate keyword or fact, but is dominated by gross misconceptions. | Confusing processes with virtual machines while mentioning memory. |
| **2** | **Partially Correct** | States fundamental truths but contains notable factual errors or invalid assumptions. | Correctly describes hashing, but claims hash collisions cannot occur. |
| **3** | **Mostly Correct** | Core technical mechanism is correct; minor inaccuracies in secondary details. | Accurately explains ACID properties, but slightly mischaracterizes Isolation levels. |
| **4** | **Highly Correct** | Fully accurate across all primary points; negligible technical ambiguity. | Accurate explanation of process memory layout with minor syntax omission. |
| **5** | **Fully Correct** | Fully accurate with no identified substantive factual errors, rigorous, and uses domain terminology accurately. | Accurate explanation of memory isolation, MMU, page tables, and context switching with no identified substantive errors. |

---

### Dimension B: Completeness ($0 - 5$)

Evaluates how thoroughly the candidate addressed the prompt, whether expected concepts were covered, and if relevant trade-offs were discussed.

| Score | Rating | Technical Definition | Example Criteria |
| :---: | :--- | :--- | :--- |
| **0** | **No Meaningful Answer** | The response is blank, a refusal to answer, or completely misses the question. | *"I don't know"*, *"Pass"*, or under 5 irrelevant words. |
| **1** | **Very Incomplete** | Mentions only a single superficial point; ignores all primary requirements. | Mentions that threads are faster, but fails to explain why or how. |
| **2** | **Covers Limited Concepts** | Touches on roughly $30 - 50\%$ of `expected_concepts`; omits major structural elements. | Explains TCP reliability (ACKs) but omits flow control, congestion, or handshakes. |
| **3** | **Covers Major Concepts** | Addresses primary mechanisms ($> 70\%$ of expected concepts), but omits edge cases or trade-offs. | Explains TCP handshake and reliability, but omits congestion control mechanisms. |
| **4** | **Nearly Complete** | Covers almost all primary and secondary concepts; leaves out only minor edge cases. | Thorough comparison of TCP vs UDP including handshakes, headers, and use cases. |
| **5** | **Comprehensive** | Exhaustive coverage; covers primary concepts, underlying mechanisms, edge cases, and architectural trade-offs. | Complete comparison including headers, windowing, congestion algorithms, and QUIC/HTTP3 evolutions. |

---

### Dimension C: Communication Clarity & Structure ($0 - 5$)

Evaluates how well the response is organized, whether thoughts flow logically, and whether the answer is professionally delivered.

| Score | Rating | Technical Definition | Example Criteria |
| :---: | :--- | :--- | :--- |
| **0** | **Unintelligible** | Word salad, broken fragments, or completely indecipherable text. | Random sequences of technical buzzwords without syntactic structure. |
| **1** | **Very Unclear** | Disorganized, rambling, extreme misapplication of terminology; very difficult to follow. | Highly disjointed sentences that obscure the candidate's actual thought process. |
| **2** | **Understandable but Poorly Structured** | The point can be deciphered, but requires effort due to run-on thoughts or poor flow. | A single unbroken paragraph mixing definitions, pros, cons, and unrelated notes. |
| **3** | **Reasonably Clear** | Comprehensible, standard structure (e.g., introduction then explanation); acceptable phrasing. | Clear sentences, readable pacing, standard technical terms used properly. |
| **4** | **Clear & Well-Structured** | Logical flow, good use of bulleted or sequential reasoning, clear transitions. | Uses structured formatting (e.g., *"First... Second... In contrast..."*). |
| **5** | **Concise, Precise, Professional** | Exemplary interview delivery: articulate, highly concise, zero fluff, logical precision. | Professional, structured breakdown directly answering the prompt with maximum signal-to-noise ratio. |

---

## 4. Overall Quality Classification Mapping

> [!WARNING]
> **Status of Score Thresholds:** The quality tier mapping below is **PROPOSED**, **SUBJECT TO FACULTY VALIDATION**, and **SUBJECT TO ANNOTATION CALIBRATION**.
>
> These intervals are not scientifically validated constants or established ground truth; final score boundaries will be calibrated based on empirical pilot annotation distributions and formal course faculty review.

| Total Score (PROPOSED — SUBJECT TO VALIDATION & CALIBRATION) | Class ID | Quality Tier | Practical Interpretation |
| :---: | :---: | :--- | :--- |
| **0 – 3** | **0** | **Poor** | Severe lack of knowledge; unacceptable for an interview candidate. |
| **4 – 7** | **1** | **Needs Improvement** | Partial awareness, but lacks depth; requires substantial preparation. |
| **8 – 11** | **2** | **Good** | Competent candidate; meets standard industry expectations for the role. |
| **12 – 15** | **3** | **Excellent** | Standout performance; demonstrates mastery, trade-offs, and communication polish. |

---

## 5. Edge-Case Handling Protocols

Annotators must adhere to the following rules when encountering challenging response types:

### A. Irrelevant or Off-Topic Answers
- If a candidate answers a completely different question or responds with pleasantries:
  - Correctness = `0`, Completeness = `0`, Communication = $\le 2$.
  - Quality Class = `0 (Poor)`.

### B. Extremely Short Answers ($\le 5$ words)
- Unless the question is a direct binary question (e.g., *"Is Python statically typed?"*), one-line answers cannot demonstrate depth:
  - Max Completeness = `1`.
  - Quality Class = `0` or `1`.

### C. Technically Correct but Poorly Communicated Answers
- If an answer is factually correct (Correctness $= 5$, Completeness $= 4$), but poorly structured, rambling, or awkward (Communication $= 2$):
  - Total Score = $5 + 4 + 2 = 11 \rightarrow$ Class `2 (Good)`.
  - **Rule:** Do NOT artificially depress Correctness due to weak formatting. Maintain separation across dimensions.

### D. Multiple Valid Architectural Approaches
- Engineering problems often have multiple valid solutions (e.g., SQL vs. NoSQL, microservices vs. monolith):
  - If the candidate chooses an unorthodox but defensible approach and articulates sound trade-offs, award full Correctness points.
  - Do not penalize candidates simply because their response differs from the reference answer's preferred implementation.

### E. Domain-Specific Terminology & Acronyms
- Standard industry acronyms (e.g., `OOM`, `Deadlock`, `ACID`, `CAP theorem`, `LRU`) do not require re-definition unless specifically requested by the prompt.

### F. Spelling & Minor Grammatical Errors
- **Principle:** We are evaluating computer science knowledge, not literary perfection.
- Minor typos (e.g., *"polymorphysm"*, *"concurrancy"*) or non-native phrasing that does **not** alter the technical meaning must **not** penalize Correctness or Completeness, and should carry at most a 1-point reduction on Communication if extreme.

---

## 6. Practical Human Validation Strategy (Semester V Academic Protocol)

To ensure labeling consistency and academic rigor within a college project setting:
1. **Student Team Annotators:** Scoring is conducted by student project members using the explicit rubrics above.
2. **Anonymous Annotator Tokens:** Annotators are identified strictly by anonymous keys (`annotator_id` = `ANN_01`, `ANN_02`). Zero student names, USNs, emails, or personal identifiers are stored.
3. **Dual-Audit Review:** A random $15\% - 20\%$ subset of responses will be independently evaluated by two different team members without viewing each other's scores.
4. **Dispute Resolution Protocol:**
   - Any score variance $\ge 2$ points on any dimension, or any variance that shifts the final quality class, is marked as a dispute.
   - Disputed items are re-examined by both annotators alongside the reference answer and resolved via rubric consensus.
5. **Consistency Measurement:** Inter-annotator agreement metrics (such as Cohen's Kappa or percent agreement) will be computed and logged in the project report **only after the annotation process is executed**. No fabricated consistency numbers are claimed in advance.
6. **No False Role Claims:** Faculty members are recognized as project guides and evaluators; they will not be claimed as annotators unless they actively participate in labeling.

---

## 7. Use of AI-Assisted Synthetic Responses

> [!CAUTION]
> **Handling AI-Assisted Synthetic Text:**
> - If AI tools are used to assist in generating candidate responses across quality tiers, they serve **strictly as a controlled data-generation aid**, subject to faculty review.
> - **Synthetic candidate answers are NOT real student responses.** They must never be represented as empirical human interview behavior.
> - **Synthetic answers must NOT be treated as ground truth.** The prompt used to generate a response does not dictate its label. Every synthetic response must be independently inspected, scored, and validated by human annotators using this rubric.
> - LLM self-grading without human annotation is strictly forbidden.

---

## 8. Dataset Limitations

1. **Synthetic-Data Bias:** If synthetic responses are utilized, they may carry subtle stylistic markers or predictable vocabulary patterns characteristic of LLMs.
2. **Annotator Diversity:** Annotation is performed by student team members and reflects academic peer judgment rather than seasoned industry recruiters.
3. **Communication Scoring Subjectivity:** Evaluating communication clarity retains some inherent human subjectivity, mitigated by explicit rubric boundaries.
4. **Domain Scope:** Focuses on 10 foundational engineering subjects in Phase 1 (DSA, OOP, DBMS, CN, OS, Python, C/C++, Java, ML, AI).
5. **Synthetic vs. Real-World Mismatch:** Synthetic responses may not capture authentic human disfluencies, nervous pauses, or real-time cognitive shifts that occur during actual verbal interviews.
