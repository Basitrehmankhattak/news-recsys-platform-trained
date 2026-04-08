#  Industry-Grade News Recommendation System

This project is a **production-style News Recommendation System** inspired by real-world systems such as Google News and Netflix.

The goal is not just to train a model, but to build a **complete end-to-end recommendation pipeline**, including backend APIs, user interaction logging, and a product-like frontend.

---

##  Overview

This system implements a **multi-stage recommendation pipeline**:

User → Retrieval → Ranking → Re-ranking → Logging → Analytics

It supports:
- Cold-start and warm-start users
- Realistic impression & click logging
- Learning-to-Rank based personalization
- Analytics dashboard (CTR, dwell time)

---

##  System Architecture

###  Candidate Retrieval
- Model: **MiniLM (Sentence Transformers)**
- Method: **FAISS vector search**
- Embedding size: 384
- Similarity: Cosine similarity (inner product on normalized vectors)

Retrieves top-K relevant articles efficiently.

---

###  Ranking (Learning-to-Rank)
- Models:
  - **LightGBM Learning-to-Rank (main model)**
  - Logistic Regression (baseline)

Training data:
- Clicked items → positive signals
- Shown but not clicked → negative signals
- Each impression is treated as a ranking group

The ranker reorders candidates based on **click likelihood**.

---

###  Re-ranking (Diversity)
- Method: **MMR (Maximal Marginal Relevance)**
- Purpose: Reduce redundancy and improve diversity in recommendations

---

###  Cold → Warm Personalization
- Cold users → fallback recommendations
- Warm users → personalized using click history
- User embedding built from recent interactions

---

##  Backend & Data Engineering

### Tech Stack
- **FastAPI** (API layer)
- **PostgreSQL (Dockerized)** (event logging)
- **FAISS** (vector search)
- **LightGBM** (ranking)
- Python

### Logging System
- Impressions are logged before clicks
- Clicks cannot exist without impressions
- Each item stores:
  - retrieval_score
  - rank_score
  - final_score

This ensures **correct supervision for training**.

---

##  API Endpoints

### `POST /recommendations`
Returns ranked recommendations.

### `POST /click`
Logs user clicks with:
- impression_id
- item_id
- position
- dwell time

### `GET /users/{anonymous_id}/recent_clicks`
Used to detect warm vs cold users.

---

##  Dataset

- **Microsoft MIND News Dataset**
- Contains:
  - thousands of news articles
  - millions of impressions
  - historical click data

---

## Frontend (Streamlit)

A product-style interface that allows:

- Anonymous account creation (cold user)
- Login with existing user (warm user)
- Browse personalized recommendations
- View reasoning ("because you clicked X")
- Track dwell time
- Analytics dashboard:
  - CTR
  - total clicks
  - impressions
  - top items

---

##  How It Works (Simple Flow)

1. User logs in (anonymous_id)
2. System retrieves candidates using FAISS
3. Ranker orders items using LightGBM
4. Re-ranking improves diversity
5. Results are served via API
6. Impressions and clicks are logged
7. Metrics are computed for analysis

---

## Key Features

- End-to-end recommendation pipeline
- Learning-to-Rank with real interaction data
- Cold-start handling
- Diversity-aware recommendations
- Production-style logging system
- Analytics dashboard
- Separation of concerns (retrieval, ranking, logging)

---

## Limitations

- Ranking model is pretrained (not fully retrained on current logs)
- No A/B testing yet
- No deployment (local system)
- No authentication system (anonymous users only)

---

##  Key Learnings

- Retrieval quality is critical for recommendation systems
- Logging correctness is as important as modeling
- Real systems require multiple stages, not a single model
- Data alignment strongly impacts ranking performance
- Diversity improves user experience

---

##  Authors

- Basit Rehman Khattak  


---

##  Future Improvements

- Model retraining pipeline
- A/B testing framework
- Deployment (cloud)
- Online learning
- Better UI/UX

---

##  Final Note

This project focuses on **system design and realism**, not just model accuracy.

It demonstrates how real-world recommendation systems are built, combining:
- Machine Learning
- Backend Engineering
- Data Engineering
- Product Thinking
