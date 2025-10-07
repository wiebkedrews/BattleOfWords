#####Sentiment analysis#####
# https://www.geeksforgeeks.org/twitter-sentiment-analysis-on-russia-ukraine-war-using-python/?ref=rp
# https://www.kaggle.com/code/scratchpad/notebook0a29e8a9a2/edit


# %%
# Import Libraries
 
from textblob import TextBlob
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import nltk
nltk.download('vader_lexicon')
import re
import string
import seaborn as sns
import plotly.express as px  # Add this import at the beginning
import plotly.graph_objects as go

from PIL import Image
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.stem import SnowballStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer

from nltk.sentiment.vader import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

# Define paths
TWEETS_PATH = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/data/'  
SENTIMENT_RESULTS_PATH = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/sentiment_results/'  


# %%
# load data
tweets_df = pd.read_feather(TWEETS_PATH + 'bigsss_tweets_w_topic_community.feather')


# %%
# Run sentiment analysis: Here, polarity_scores is a method which will  give us scores of the following categories - Positive, Negative, Neutral, Compound. The compound score is the sum of positive, negative & neutral scores which is then normalized between -1(most extreme negative) and +1 (most extreme positive). The more Compound score closer to +1, the higher the positivity of the text. Read other scores as: 49.2% Positive, 0% Negative, 50.8% Neutral.

scores = []
# Declare variables for scores
compound_list = []
positive_list = []
negative_list = []
neutral_list = []
for text in tweets_df['text_clean']:
    score = analyzer.polarity_scores(str(text))
    scores.append({
        "sentiment_compound": score["compound"],
        "positive": score["pos"],
        "negative": score["neu"],
        "neutral": score["neg"]
    })
    
sentiments_score = pd.DataFrame.from_dict(scores)
tweets_df_temp = tweets_df.join(sentiments_score)
tweets_df_temp.head()
tweets_df = tweets_df_temp.copy()


# %%
# Create a variable that identifies extreme sentiments

# create a list of our conditions
conditions_1 = [
    (tweets_df['sentiment_compound'] <= -0.6),
    (tweets_df['sentiment_compound'] > -0.6) & (tweets_df['sentiment_compound'] <= -0.2),
    (tweets_df['sentiment_compound'] > -0.2) & (tweets_df['sentiment_compound'] <= 0.2),
    (tweets_df['sentiment_compound'] > 0.2) & (tweets_df['sentiment_compound'] <= 0.6),
    (tweets_df['sentiment_compound'] > 0.6)
    ]

# create a list of the values we want to assign for each condition
values = ['extremely negative', 'negative', 'neutral', 'positive', 'extremely positive']

# create a new column and use np.select to assign values to it using our lists as arguments
tweets_df['extreme_sentiment'] = np.select(conditions_1, values)
tweets_df.head()


# %%
# Pie chart of extreme sentiments

df_plot = pd.DataFrame(tweets_df.groupby(['extreme_sentiment'])['extreme_sentiment'].count()).rename(columns={"extreme_sentiment":"Counts"}).assign(
    Percentage=lambda x: (x.Counts/ x.Counts.sum())*100)
df_plot

# Desired order
order = ['extremely negative', 'negative', 'neutral', 'positive', 'extremely positive']

# Reorder the DataFrame
df_plot = df_plot.reindex(order)

# Directly assign colors to sentiments
colors = {
    'extremely negative': 'darkred',
    'negative': 'lightcoral',
    'neutral': 'white',
    'positive': 'lightblue',
    'extremely positive': 'darkblue'
}

# Extract the colors for the pie chart based on the order
pie_colors = [colors[sentiment] for sentiment in order]

# Generate the labels list
labels = [f"{index} [{int(row['Counts'])}]" for index, row in df_plot.iterrows()]

fig, axe = plt.subplots(figsize=(10, 5))
wedges, texts, autotexts = axe.pie(df_plot["Counts"].values, startangle=90, autopct="%2.2f%%", colors=pie_colors)

# Set edgecolor for each wedge
for wedge in wedges:
    wedge.set_edgecolor('black')

# Adjust the font size of the autotexts
for autotext in autotexts:
    autotext.set(size=8)

plt.style.use('default')
axe.legend(wedges, labels, title="Sentiments", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), prop={'size': 8})
plt.title(f'% of Sentiment Tweets with Extreme Values')
plt.axis('equal')

# Save the plot as an HTML file
fig = px.pie(df_plot, values='Counts', names=df_plot.index, color=df_plot.index,
             color_discrete_map=colors, title=f'% of Sentiment Tweets with Extreme Values')
fig.write_html(SENTIMENT_RESULTS_PATH + 'extreme_sentiment_pie_chart.html')

plt.show()


# %%
#Create a variable that identifies sentiments (3 categories)

# create a list of our conditions
conditions_2 = [
    (tweets_df['sentiment_compound'] <= -0.4),
    (tweets_df['sentiment_compound'] > -0.4) & (tweets_df['sentiment_compound'] <= 0.4),
    (tweets_df['sentiment_compound'] > 0.4)
    ]

# create a list of the values we want to assign for each condition
values = ['negative', 'neutral', 'positive']

# create a new column and use np.select to assign values to it using our lists as arguments
tweets_df['sentiment'] = np.select(conditions_2, values)
tweets_df.head()


# %%
# Pie chart of 3 categories of sentiments

# some visualizations
df_plot = pd.DataFrame(tweets_df.groupby(['sentiment'])['sentiment'].count()).rename(columns={"sentiment":"Counts"}).assign(
    Percentage=lambda x: (x.Counts/ x.Counts.sum())*100)
df_plot

# Desired order
order = ['negative', 'neutral', 'positive']

# Reorder the DataFrame
df_plot = df_plot.reindex(order)

# Directly assign colors to sentiments
colors = {
    'negative': 'darkred',
    'neutral': 'white',
    'positive': 'darkblue'
}

# Extract the colors for the pie chart based on the order
pie_colors = [colors[sentiment] for sentiment in order]

# Generate the labels list
labels = [f"{index} [{int(row['Counts'])}]" for index, row in df_plot.iterrows()]

fig, axe = plt.subplots(figsize=(10, 5))
wedges, texts, autotexts = axe.pie(df_plot["Counts"].values, startangle=90, autopct="%2.2f%%", colors=pie_colors)

# Set edgecolor for each wedge
for wedge in wedges:
    wedge.set_edgecolor('black')

# Adjust the font size of the autotexts
for autotext in autotexts:
    autotext.set(size=8)

plt.style.use('default')
axe.legend(wedges, labels, title="Sentiments", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), prop={'size': 8})
plt.title(f'% of Sentiment Tweets')
plt.axis('equal')

# Save the plot as an HTML file
fig = px.pie(df_plot, values='Counts', names=df_plot.index, color=df_plot.index,
             color_discrete_map=colors, title=f'% of Sentiment')
fig.write_html(SENTIMENT_RESULTS_PATH + 'sentiment_pie_chart.html')

plt.show()


# %%
# top 50 positive tweets
tweets_df.nlargest(n=50, columns=['sentiment_compound'])["text_translated"]


# %%
# top 50 negative tweets
tweets_df.nsmallest(n=50, columns=['sentiment_compound'])["text_translated"]


# %%
#Sentiment over time
#Change of absolute sentiments over time per week

# Convert 'created_at' to datetime format
tweets_df['created_at'] = pd.to_datetime(tweets_df['created_at'])

# Resample the data to weekly frequency
weekly_counts = tweets_df.groupby([pd.Grouper(key='created_at', freq='W'), 'extreme_sentiment']).size().reset_index(name='count')

# Filter out weeks after the last week with data
last_week_with_data = weekly_counts['created_at'].max()
weekly_counts = weekly_counts[weekly_counts['created_at'] <= last_week_with_data]

# Define the color mapping
color_map = {
    "extremely positive": "darkblue",
    "positive": "lightblue",
    "neutral": "white",
    "negative": "lightcoral",
    "extremely negative": "darkred"
}

# Plotting the histogram for absolute sentiments over time (weekly)
fig = px.bar(
    weekly_counts, 
    x="created_at", 
    y="count",
    color="extreme_sentiment", 
    title=f"Weekly Absolute Number of Sentiment Tweets",
    labels={"created_at": "Week", "count": "Number of Tweets"},
    category_orders={"Extreme_Sentiment": ["Extremely Positive", "Positive", "Neutral", "Negative", "Extremely Negative"]},
    color_discrete_map=color_map
)

# Add a vertical line marking the week of the Russian invasion
invasion_date = "2022-02-24"
fig.add_vline(x=invasion_date, line_width=2, line_dash="dash", line_color="orange")

# Add a dummy scatter plot to act as a legend entry for the vertical line
fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='orange', width=2, dash='dash'), name='Russian Invasion'))

fig.update_layout(legend_title_text='Legend')

fig.write_html(SENTIMENT_RESULTS_PATH + 'absolute_sentiment_over_time.html')

fig.show()


# %%
#Change of relative sentiments over time per week

# Step 1: Calculate total tweets per week
total_tweets_per_week = tweets_df.groupby(pd.Grouper(key='created_at', freq='W')).size().reset_index(name='total_count')

# Step 2: Calculate the count of each sentiment per week (already done above as 'weekly_counts')

# Step 3: Merge total counts with weekly_counts and calculate proportions
weekly_counts = weekly_counts.merge(total_tweets_per_week, on='created_at')
weekly_counts['proportion'] = weekly_counts['count'] / weekly_counts['total_count']

# Step 4: Plotting the histogram for relative sentiments over time (weekly)
fig = px.bar(
    weekly_counts,
    x="created_at",
    y="proportion",
    color="extreme_sentiment",
    title=f"Weekly Relative Sentiment Tweets",
    labels={"created_at": "Week", "proportion": "Proportion of Tweets"},
    category_orders={"extreme_sentiment": ["extremely positive", "positive", "neutral", "negative", "extremely negative"]},
    color_discrete_map=color_map
)

# To make it stacked bar chart
fig.update_layout(barmode='stack')

# Add a vertical line marking the week of the Russian invasion
fig.add_vline(x=invasion_date, line_width=2, line_dash="dash", line_color="orange")

# Add a dummy scatter plot to act as a legend entry for the vertical line
fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', line=dict(color='orange', width=2, dash='dash'), name='Russian Invasion'))

fig.update_layout(legend_title_text='Legend')

fig.write_html(SENTIMENT_RESULTS_PATH + 'relative_sentiment_over_time.html')

fig.show()


# %%
# Save the DataFrame as a Feather file

tweets_df.to_feather(TWEETS_PATH + 'bigsss_tweets_w_topic_community_sentiment.feather')


# %% 
# Convert feather to csv so it's readable in other programs

# Read the feather file
#tweets_df = pd.read_feather(TWEETS_PATH + 'bigsss_tweets_w_topic_community_sentiment.feather')

# Convert and save as a CSV file
tweets_df.to_csv(TWEETS_PATH + 'bigsss_tweets_w_topic_community_sentiment.csv', index=False)
