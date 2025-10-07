##########################################################
##### IMPORTANT NOTE: Due to a lack of data (particularly number of Tweets), we cannot calculate the ECS for Ukraine Tweets only for the first period; it works for the second period and the entire period #####
##########################################################

# %%
#import os
#os.environ["CUBLAS_WORKSPACE_CONFIG"]=":4096:8"

import json
import torch
import random
import numpy as np
from sklearn.utils import check_random_state
import pandas as pd
import sys

sys.path.insert(1, '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/') # adjust if necessary

from src.load_data import get_data
from src.EchoGAE import EchoGAE_algorithm
from src.echo_chamber_measure import EchoChamberMeasure


# %%
seed_value=42
random.seed(seed_value)
np.random.seed(seed_value)
torch.manual_seed(seed_value)
torch.cuda.manual_seed(seed_value)
torch.cuda.manual_seed_all(seed_value)
#torch.backends.cudnn.enabled=True
#torch.backends.cudnn.benchmark=False
#torch.backends.cudnn.deterministic=True
#torch.use_deterministic_algorithms(True)
check_random_state(seed_value)

# NOTE: Yu need to calculate the ECS for each period individually, i.e., add and remove # for the specific periods you are interested in

# Datasets 
# Period 1
# ds = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/results/period_1/'

# Period 2
# ds = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/results/period_2/'

# All periods
ds = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/results/all_periods/'


# Filters
RES_VALUE = 0.1  # NOTE: Resolution value for community detection, TO DO: manually adjust this until the code works (no error messages) & you have at least two communities
COMM_SIZE = 3  # NOTE: Minimum number of members in each community, TO DO: find a reference or adjust, i.e., how many members should a community have?
MIN_DEGREE = 0  # NOTE: Minimum degree each node should have in given RT networks, i.e., number of connections each user / node should have
MIN_TWEETS = 2  # NOTE: Minimum number of tweets posted in given period


# ECS metric
ecs_information = []

print(f"Dataset ({ds}): ", end="")

ds_dict = {}
ds_dict["dataset"] = ds

# Get the data
# NOTE: See https://github.com/pyg-team/pytorch_geometric/issues/92
G, users_embeddings, community_labels, author_id_to_index_map, users_information = get_data(path=f"{ds}", 
                                                                                          resolution=RES_VALUE, 
                                                                                          min_comm_size=COMM_SIZE,
                                                                                          directed_graph=True, # TO DO: decide whether directed or undirected
                                                                                          min_degree=MIN_DEGREE,
                                                                                          min_tweets=MIN_TWEETS)


# Graph information
ds_dict["number_of_nodes"] = G.number_of_nodes()
ds_dict["number_of_edges"] = G.number_of_edges()
ds_dict["number_of_communities"] = len(np.unique(community_labels))

# ECS
user_emb = EchoGAE_algorithm(G, user_embeddings=users_embeddings, show_progress=False, hidden_channels=20, 
                                out_channels=10, epochs=300)
ecm = EchoChamberMeasure(user_emb, community_labels)
eci = ecm.echo_chamber_index()
ds_dict["echo_chamber_score"] = eci

print(f"ECS = {eci:.3f} -- ", end=" ")

# For communities ECIs and Sizes
sizes = []
ECSs = []

for i in np.unique(community_labels):
    sizes.append(np.sum(community_labels == i))
    ECSs.append(ecm.community_echo_chamber_index(i))

ds_dict["community_sizes"] = sizes
ds_dict["community_ECIs"] = ECSs

print("")


# Create df for "ecs_information"
ecs_information.append(ds_dict)
ecs_information_df = pd.DataFrame(ecs_information)

# Delete from df "tweets" and "embeddings"
users_information = users_information[["author_id", "community"]]

# Save results
ecs_information_df.to_csv(f"{ds}/ecs_information_resolution_{RES_VALUE}.csv", index=False) 
users_information.to_csv(f"{ds}/users_information.csv", index=False) 


# Create mappings from community to users and user to community 
community_to_author_ids_map = {}
author_id_to_community_map = {}

# Extract all "author_ids" from the "author_id_index_map"
author_ids = author_id_to_index_map.keys()

# Iterate through pairs of "author_ids" and corresponding "community_labels"
for author_id, community_label in zip(author_ids, community_labels):
    community_to_author_ids_map.setdefault(f"Community_{community_label}", []).append(author_id)
    author_id_to_community_map[str(author_id)] = f"Community_{community_label}"

# Save "community_to_author_ids_map"
with open(f"{ds}/" + "community_to_author_ids_map.json", "w") as json_file:
    json.dump(community_to_author_ids_map, json_file)

# Save "author_id_to_community_map" 
with open(f"{ds}/" + "author_id_to_community_map.json", "w") as json_file:
    json.dump(author_id_to_community_map, json_file)  

print("\n\n")


# %%
# Merge community information with original data set
# Period 2 incl topics

# Read the CSV and Feather files
users_information_df_p2 = pd.read_csv('/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/results/period_2/users_information.csv')
tweets_df = pd.read_feather('/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/data/bigsss_tweets_w_topic.feather')

# Rename 'user_id' to 'author_id' in users_information_df_p2 for the rest of the analysis
users_information_df_p2 = users_information_df_p2.rename(columns={'author_id': 'user_id'})

# Convert 'user_id' in both DataFrames to the same data type
# Choose str or int based on your data context
tweets_df['user_id'] = tweets_df['user_id'].astype(str)
users_information_df_p2['user_id'] = users_information_df_p2['user_id'].astype(str)

# Merge the DataFrames on 'user_id'
merged_df = pd.merge(tweets_df, users_information_df_p2[['user_id', 'community']], on='user_id', how='left')

# Rename 'community' column to 'community_period_2_russo_ukraine'
merged_df.rename(columns={'community': 'community_period_2_russo_ukraine'}, inplace=True)

# Change the values 0.0 into 0 and 1.0 into 1 while preserving NaN values
merged_df['community_period_2_russo_ukraine'] = merged_df['community_period_2_russo_ukraine'].astype('Int64')

# Get the distribution of 'community_period_2_russo_ukraine'
community_distribution = merged_df['community_period_2_russo_ukraine'].value_counts(dropna=False)

# Print the distribution
print(community_distribution)


# %%
# Merge community info w/ original data set
# Whole Period incl topics

# Read the CSV and Feather files
users_information_df_3 = pd.read_csv('/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/results/all_periods/users_information.csv')

# Rename 'user_id' to 'author_id' in users_information_df_p3 for the rest of the analysis
users_information_df_p3 = users_information_df_3.rename(columns={'author_id': 'user_id'})

# Convert 'user_id' in both DataFrames to the same data type
# Choose str or int based on your data context
users_information_df_p3['user_id'] = users_information_df_p3['user_id'].astype(str)

# Merge the DataFrames on 'user_id'
merged_df = pd.merge(merged_df, users_information_df_p3[['user_id', 'community']], on='user_id', how='left')

# Rename 'community' column to 'community_period_2_russo_ukraine'
merged_df.rename(columns={'community': 'community_all_periods_russo_ukraine'}, inplace=True)

# Change the values 0.0 into 0 and 1.0 into 1 while preserving NaN values
merged_df['community_all_periods_russo_ukraine'] = merged_df['community_all_periods_russo_ukraine'].astype('Int64')

# Get the distribution of 'community_period_2_russo_ukraine'
community_distribution = merged_df['community_all_periods_russo_ukraine'].value_counts(dropna=False)

# Print the distribution
print(community_distribution)


# %%
# Save the DataFrame as a Feather file
merged_df.to_feather('/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/data/bigsss_tweets_w_topic_community.feather')

# %%
