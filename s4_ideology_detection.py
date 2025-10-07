
# %% 
import pandas as pd
import numpy as np
import sys

sys.path.insert(1, '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine') # adjust if necessary

from sentence_transformers import SentenceTransformer
from src.tweet_preprocessing import preprocess_tweet_for_bert

from tqdm import tqdm

tqdm.pandas()

DATA_PATH = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/data/'  
PERIOD_1_PATH = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/results/period_1/'
PERIOD_2_PATH = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/results/period_2/'
ALL_PERIODS_PATH = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/results/all_periods/'

SENTENCE_MODEL = 'all-mpnet-base-v2' # The default is: 'all-MiniLM-L6-v2'

# https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 384 dimensional dense vector space
# https://huggingface.co/sentence-transformers/all-mpnet-base-v2 768 dimensional dense vector space


# %%

# Define Periods
start_date_period_1 = '2021-10-13'
end_date_period_1 = '2022-02-23'

start_date_period_2 = '2022-02-24'
end_date_period_2 = '2022-07-22'

start_date_all_periods = '2021-10-13'
end_date_all_periods = '2022-07-22'


# %%
# Load data

df = pd.read_feather(DATA_PATH + 'bigsss_tweets_w_topic.feather')

# Create russo-ukraine data frame with only tweets containing this topic
df_rus_ukr = df.loc[(df['russo_ukraine']==1)]  

#df_rus_ukr_100 = df_rus_ukr.head(100)
#print(df_rus_ukr_100)


# %%
# rename user_id to author_id for the rest of the analysis
df_rus_ukr = df_rus_ukr.rename(columns={'user_id': 'author_id'})

# NOTE: Keep original tweets ONLY (not retweets) 
df_rus_ukr = df_rus_ukr[~df_rus_ukr['action'].isin(['retweeted'])]

# Keep certain columns
df_rus_ukr = df_rus_ukr[['author_id', 'text_translated', 'created_at']]  

# Rename columns
df_rus_ukr = df_rus_ukr.rename(columns={'author_id': 'author_id', 'text_translated': 'tweets'})  

# Convert tweets to str
df_rus_ukr['tweets'] = df_rus_ukr['tweets'].astype(str)  


# %%
# Split tweets with topics according to the periods
# NOTE: Ideology detection (& embeddings computation) is done on Russo-Ukraine tweets for the respective period (before, after, all) --> TO DO: Clarify whether ideology should be computed on all tweets (not only those mentioning Russo-Ukraine) & or on all Tweets mentionings Russo-Ukraine

period_1 = df_rus_ukr[(df_rus_ukr['created_at'] >= start_date_period_1) & (df_rus_ukr['created_at'] <= end_date_period_1)]
period_2 = df_rus_ukr[(df_rus_ukr['created_at'] >= start_date_period_2) & (df_rus_ukr['created_at'] <= end_date_period_2)]
all_periods = df_rus_ukr[(df_rus_ukr['created_at'] >= start_date_all_periods) & (df_rus_ukr['created_at'] <= end_date_all_periods)]


# %%
# Group by author_id and convert to array and truncate tweets to a maximum of 200 per author_id

def process_period(df):
    df_grouped = df.groupby('author_id')['tweets'].apply(list).reset_index()
    df_grouped['tweets'] = df_grouped['tweets'].apply(lambda x: np.array(x[:200]))
    return df_grouped

period_1_grouped = process_period(period_1)
period_2_grouped = process_period(period_2)
all_periods_grouped = process_period(all_periods)


# %%
# Save tweets for ideology detection to all sub-folders
period_1_grouped.to_feather(PERIOD_1_PATH + 'tweets.feather')  
period_2_grouped.to_feather(PERIOD_2_PATH + 'tweets.feather')  
all_periods_grouped.to_feather(ALL_PERIODS_PATH + 'tweets.feather')


# %%
# Compute embeddings for each period
def compute_embeddings(df_grouped, path):
    def preprocess_tweets(tweets):
        out = []
        for tw in tweets:
            tw = preprocess_tweet_for_bert(tw)
            if len(tw) > 1:
                out.append(" ".join(tw))
        return out

    df_grouped["tweets"] = df_grouped["tweets"].progress_apply(preprocess_tweets)

    # Remove users with no tweets
    df_grouped = df_grouped[df_grouped["tweets"].apply(len) > 0]

    model = SentenceTransformer(SENTENCE_MODEL)

    def embed_user_tweets(tweets):
        emb = model.encode(tweets)
        emb = np.mean(emb, axis=0)
        return emb

    df_grouped["embeddings"] = df_grouped["tweets"].progress_apply(embed_user_tweets)

    embeddings_tmp = df_grouped[["author_id", "embeddings"]]
    embeddings_tmp.reset_index(drop=True, inplace=True)

    # Save embeddings to the specified path
    embeddings_tmp.to_feather(path + "embeddings.feather")

# Compute and save embeddings for each period
compute_embeddings(period_1_grouped, PERIOD_1_PATH)
compute_embeddings(period_2_grouped, PERIOD_2_PATH)
compute_embeddings(all_periods_grouped, ALL_PERIODS_PATH)


# %%
