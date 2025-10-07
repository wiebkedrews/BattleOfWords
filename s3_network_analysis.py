# %%
import pandas as pd


DATA_PATH = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/data/'  
PERIOD_1_PATH = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/results/period_1/'
PERIOD_2_PATH = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/results/period_2/'
ALL_PERIODS_PATH = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/results/all_periods/'


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

#df_rus_ukr.to_feather(DATA_PATH + 'bigsss_tweets_ukraine_only.feather')


# %%
# Split tweets with topics according to the periods
period_1 = df_rus_ukr[(df_rus_ukr['created_at'] >= start_date_period_1) & (df_rus_ukr['created_at'] <= end_date_period_1)]
period_2 = df_rus_ukr[(df_rus_ukr['created_at'] >= start_date_period_2) & (df_rus_ukr['created_at'] <= end_date_period_2)]
all_periods = df_rus_ukr[(df_rus_ukr['created_at'] >= start_date_all_periods) & (df_rus_ukr['created_at'] <= end_date_all_periods)]


# %%
# Keep retweets ONLY and create nodes and edges 
# Period 1 
retweets_period_1 = period_1[period_1['action'] == 'retweeted']

# Period 2
retweets_period_2 = period_2[period_2['action'] == 'retweeted']

# All periods
retweets_all_periods = all_periods[all_periods['action'] == 'retweeted']


# Convert retweet IDs to str
# Period 1
retweets_period_1['action_id'] = retweets_period_1['action_id'].astype(str)

# Period 2
retweets_period_2['action_id'] = retweets_period_2['action_id'].astype(str)

# All periods
retweets_all_periods['action_id'] = retweets_all_periods['action_id'].astype(str)


# Merge the two data frames, in order to find all retweets among MPs
# Period 1
retweets_period_1_merged = pd.merge(retweets_period_1, period_1, left_on='action_id', right_on='id', 
                                    suffixes=('_retweet', '_original'))

# Period 2
retweets_period_2_merged = pd.merge(retweets_period_2, period_2, left_on='action_id', right_on='id', 
                                    suffixes=('_retweet', '_original'))

# All periods
retweets_all_periods_merged = pd.merge(retweets_all_periods, all_periods, left_on='action_id', right_on='id', 
                                        suffixes=('_retweet', '_original'))


# Create edges
# Period 1
edges_period_1 = retweets_period_1_merged[['user_id_retweet', 'user_id_original']]
edges_period_1 = edges_period_1.rename(columns={'user_id_retweet': 'source', 'user_id_original': 'target'})

# Remove edges where users retweet themselves
edges_period_1 = edges_period_1[edges_period_1['source'] != edges_period_1['target']]


# Period 2
edges_period_2 = retweets_period_2_merged[['user_id_retweet', 'user_id_original']]
edges_period_2 = edges_period_2.rename(columns={'user_id_retweet': 'source', 'user_id_original': 'target'})

# Remove edges where users retweet themselves
edges_period_2 = edges_period_2[edges_period_2['source'] != edges_period_2['target']]

# All periods
edges_all_periods = retweets_all_periods_merged[['user_id_retweet', 'user_id_original']]
edges_all_periods = edges_all_periods.rename(columns={'user_id_retweet': 'source', 'user_id_original': 'target'})

# Remove edges where users retweet themselves
edges_all_periods = edges_all_periods[edges_all_periods['source'] != edges_all_periods['target']]


# Create nodes
# Period 1
unique_nodes_period_1 = pd.unique(edges_period_1[['source', 'target']].values.ravel('K'))

nodes_period_1 = pd.DataFrame({'label': unique_nodes_period_1})
nodes_period_1.insert(0, 'id', range(1, len(nodes_period_1) + 1))  # Add 'id' column

# Period 2
unique_nodes_period_2 = pd.unique(edges_period_2[['source', 'target']].values.ravel('K'))

nodes_period_2 = pd.DataFrame({'label': unique_nodes_period_2})
nodes_period_2.insert(0, 'id', range(1, len(nodes_period_2) + 1))  # Add 'id' column

# All periods
unique_nodes_all_periods = pd.unique(edges_all_periods[['source', 'target']].values.ravel('K'))

nodes_all_periods = pd.DataFrame({'label': unique_nodes_all_periods})
nodes_all_periods.insert(0, 'id', range(1, len(nodes_all_periods) + 1))  # Add 'id' column



# %%
# Save edges and nodes 
# Period 1
edges_period_1.to_csv(PERIOD_1_PATH + 'edges.csv', index=False)
nodes_period_1.to_csv(PERIOD_1_PATH + 'nodes.csv', index=False)

# Period 2
edges_period_2.to_csv(PERIOD_2_PATH + 'edges.csv', index=False)
nodes_period_2.to_csv(PERIOD_2_PATH + 'nodes.csv', index=False)

# All periods
edges_all_periods.to_csv(ALL_PERIODS_PATH + 'edges.csv', index=False)
nodes_all_periods.to_csv(ALL_PERIODS_PATH + 'nodes.csv', index=False)



# %%