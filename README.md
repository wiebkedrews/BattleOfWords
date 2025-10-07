# Battle of words: Dynamics of echo chambers among political elites

This repository contains the replication files for the article *“Battle of words: Dynamics of echo chambers among political elites”* by Wiebke Drews, Joris Frese, Hilke Brockmann, Pedro Fierro, Daniel Triana, and Andreas Dafnos.

## Data Availability

Due to Twitter’s/X’s Terms of Service, raw tweet text and associated metadata cannot be shared. To ensure reproducibility, we provide:

- **Tweet IDs** underlying all analyses (can be rehydrated via the Twitter/X API)  
- **Enriched dataset** with characteristics of Members of the European Parliament (MEPs), excluding tweet text  

## Python Workflow (Preprocessing, NLP, Network Analysis)

The Python scripts implement the pipeline for **topic classification, sentiment analysis, network construction, and echo chamber measurement**. Scripts should be run chronologically:

1. `s1_tweet_cleaner.py` – Cleans and prepares raw tweets (after rehydration).  
2. `s2_topic_analysis.py` – Classifies tweets into topics using BERTopic.  
3. `s3_network_analysis.py` – Builds retweet and mention networks among political elites.  
4. `s4_ideology_detection.py` – Assigns ideological positions to MEPs.  
5. `s5_echo_chamber_score.py` – Calculates a novel Echo Chamber Score based on embedding distances between ideological groups.  
6. `s6_sentiment_analysis.py` – Detects sentiment in tweets using VADER.  

**Output:** topic distributions, network structures, ideology assignments, sentiment scores, and echo chamber scores for all tweets.  

## R Workflow (Statistical Analyses & Figures)

The **R Replication Files** folder contains code for the statistical analysis and visualization reported in the article:

- `H1H2H3H4.R` – Runs all four hypothesis tests, including:  
  - Pairwise comparisons across ideological groups  
  - Fixed-effects regressions to assess strategic elite behavior  
  - Difference-in-differences estimations to capture effects of the Russian invasion of Ukraine  
  - Generation of all figures and tables included in the article  

- `edf_clean.RData` and `old_df_clean.RData` – Clean datasets (tweet text removed) used in these analyses  
- `Echo Chambers.Rproj` – R project file for easy replication  

## How to Reproduce

1. Rehydrate tweets using provided IDs and the Twitter API.  
2. Run Python scripts sequentially (`s1` → `s6`) to generate the processed data.  
3. Open `Echo Chambers.Rproj` and run `H1H2H3H4.R` to replicate all statistical analyses, tables, and figures.  
