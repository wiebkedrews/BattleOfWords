# Battle of words: Dynamics of echo chambers among political elites

This repository contains the replication files for the article *“Battle of words: Dynamics of echo chambers among political elites”* by Wiebke Drews, Joris Frese, Hilke Brockmann, Pedro Fierro, Daniel Triana, and Andreas Dafnos.

---

## Data Availability

Due to Twitter’s/X’s Terms of Service, raw tweet text and associated metadata cannot be shared.  
To ensure reproducibility, we provide:

- **Tweet IDs** underlying all analyses (can be rehydrated via the X API)  
- **Enriched datasets** containing additional characteristics of Members of the European Parliament (MEPs) and European Commissioners, excluding tweet text  
- Data are stored in formats suitable for GitHub (Parquet for Python, split RData files for R, each <25MB)  

---

## Workflow Overview

The analysis proceeds in two main stages:

### 1. NLP & Network Analysis (Python)

Folder: **`NLP_Network_Analysis_Python/`**  

This step processes the raw tweets (after rehydration), classifies them by topic, constructs networks and embeddings, calculates the Echo Chamber Score, and estimates sentiment.  

**Input dataset**:  
- `tweet_ids_enriched.parquet`  
  - Contains Tweet IDs (rehydratable via API)  
  - Includes enriched variables on MEPs and Commissioners (e.g., party, country, demographics)  

**Scripts (to be run sequentially):**  
1. `s1_tweet_cleaner.py` – Cleans and prepares raw tweets (after rehydration)  
2. `s2_topic_analysis.py` – Classifies tweets into topics using BERTopic  
3. `s3_network_analysis.py` – Builds retweet and mention networks among political elites  
4. `s4_ideology_detection.py` – Assigns ideological positions to MEPs  
5. `s5_echo_chamber_score.py` – Calculates a novel Echo Chamber Score based on embedding distances  
6. `s6_sentiment_analysis.py` – Detects sentiment in tweets using VADER  

**Output:**  
- Topic distributions  
- Echo Chamber Scores  
- Sentiment scores

---

### 2. Statistical Analysis (R)

Folder: **`Statistical_Analysis_R/`**  

This step tests the study’s hypotheses using the outputs from the Python stage.  
The provided datasets already include the **topics, ECS scores, and sentiment results** produced in Python.  

**Datasets:**  
- Split into several `.RData` files (each <25 MB)  
- Automatically merged in the R scripts  
- Both *new* and *old* datasets are required:  
  - **New dataset**: includes ECS, VADER, and BERTopic outputs  
  - **Old dataset**: includes engagement metrics (needed for H3)  
  - Merging ensures a complete dataset for all tests  

**Scripts:**  
- `H1H2H3H4.R` – Runs all four hypothesis tests:  
  - Pairwise comparisons across ideological groups  
  - Fixed-effects regressions for strategic elite behavior  
  - Difference-in-differences estimations (e.g., Russian invasion of Ukraine)  
  - Generation of all figures and tables in the article  

**Project file:**  
- `Echo Chambers.Rproj` – R project file for convenient replication  

---

## How to Reproduce

1. **Rehydrate tweets** using provided IDs and the X API.  
2. **Run Python scripts** in `NLP_Network_Analysis_Python/` sequentially (`s1` → `s6`) to generate the processed variables.  
3. **Run R analyses**: open `Echo Chambers.Rproj` in `Statistical_Analysis_R/` and run `H1H2H3H4.R`.  
   - The script merges the split datasets  
   - Performs all hypothesis tests  
   - Produces the tables and figures reported in the article  

This workflow ensures that all results can be fully replicated despite restrictions on sharing raw X/Twitter data.  
