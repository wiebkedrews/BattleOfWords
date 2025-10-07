# %%
import contractions  
import html
import json
import numpy as np
import pandas as pd 
import re
import regex

from textacy import preprocessing

DATA_PATH = '/root/data/bigsss/analysis_drews/bigsss_russo_ukraine/with_topics/data/'  


# Functions
def clean_text(text):
    text = str(text)
    text = html.unescape(text)  # Replaces HTML characters
    text = re.sub('VIDEO:|AUDIO:', ' ', text)  # Removes specific tags like 'VIDEO:' 
    text = re.sub(r'http\S+|www.\S+|bit.ly/\S+|pic.twitter\S+', ' ', text)  # Removes URLs
    text = preprocessing.normalize.quotation_marks(text)  
    text = text.encode('ascii', 'ignore').decode()  # Removes non ASCII characters 
    text = re.sub(r'\s+', ' ', text).strip()  # Removes unicode whitespace characters
    text = re.sub(r'\\r|\\n|\\t|\\f|\\v', ' ', text)  # For messy data, removes unicode whitespace characters
    text = re.sub(r'(^|[^@\w])@(\w{1,15})\b', ' ', text)  # Replaces twitter handles and emails
    text = preprocessing.replace.emails(text, repl=' ') 
    text = re.sub(r'\$\w*', ' ', text)  # Removes tickers
    text = preprocessing.remove.accents(text)   
    text = text.replace('-', ' ').replace('–', ' ')  # Replaces dashes and special characters
    text = preprocessing.normalize.unicode(text)  
    text = regex.compile('[ha][ha]+ah[ha]+').sub('haha', text)  
    text = text.replace('&', ' and ')  
    text = re.sub(r'([A-Za-z])\1{2,}', r'\1', text)  # Removes repeated characters
    text = re.sub(r'\b([a-zA-Z]{1,3})(\.[a-zA-Z]{1,3}\.?)+\b', lambda match: match.group(0).replace('.', ''), text)  # Handles abbreviations with multiple dots
    text = contractions.fix(text, slang=True)  
    text = regex.compile(r'(?:(?=\b(?:\p{Lu} +){2}\p{Lu})|\G(?!\A))\p{Lu}\K +(?=\p{Lu}(?!\p{L}))').sub('', text)  # Replaces kerned
    text = text.lower()
    text = re.sub(r'[^a-zA-Z]+', ' ', text)  # Removes numbers, special characters, etc.
    text = preprocessing.normalize.whitespace(text)  # Normalises whitespace 
    return text


def extract_info(lst):
    '''Extracts information from a list of dictionaries and concatenates the values.'''
    values = [list(d.values()) for d in lst if isinstance(d, dict)]
    return ','.join(str(value) for sublist in values for value in sublist)


# Load and transform raw tweets 
with open(DATA_PATH + 'bigsss_tweets.json', 'r') as file:
    data = json.load(file)

df = pd.DataFrame(data) 

df = df[['id', 'author_id', 'created_at', 'text', 'referenced_tweets']]  # Keep certain columns


# Extract info from df_raw['referenced_tweets'] and split column. Assign its values to two new columns 
df['referenced_tweets'] = df['referenced_tweets'].apply(extract_info)

split_values = df['referenced_tweets'].str.split(',', n=1, expand=True)

df['action'] = split_values[0]
df['action_id'] = split_values[1]


# Load translated tweets 
df_translated = pd.read_feather(DATA_PATH + 'bigsss_tweets_translated.feather')

df_translated = df_translated[['id', 'text_translated', 'name', 'username', 'day', 'month', 'year', 'dob', 'full_name', 'sex', 'country', 'nat_party', 'nat_party_abb', 'eu_party_group', 'eu_party_abbr', 'commission_dummy', 'party_id', 'eu_position', 'lrgen', 'lrecon', 'galtan', 'eu_eu_position', 'eu_lrgen', 'eu_lrecon', 'eu_galtan']]  # Keep certain columns


# Convert IDs to str 
df_translated['id'] = df_translated['id'].astype(str)

df['id'] = df['id'].astype(str)


# Merge data frames 
df_merged = pd.merge(df_translated, df, on='id', how='inner')

df_merged = df_merged[['id', 'author_id', 'created_at', 'text', 'text_translated', 'action', 'action_id', 'name', 'username', 'day', 'month', 'year', 'dob', 'full_name', 'sex', 'country', 'nat_party', 'nat_party_abb', 'eu_party_group', 'eu_party_abbr', 'commission_dummy', 'party_id', 'eu_position', 'lrgen', 'lrecon', 'galtan', 'eu_eu_position', 'eu_lrgen', 'eu_lrecon', 'eu_galtan']]  # Keep certain columns


# Rename 'author_id' column to 'user_id'
df_merged = df_merged.rename(columns={'author_id': 'user_id'})


# Clean tweets
df_merged['text_clean'] = df_merged['text_translated'].apply(clean_text)

# Remove empty cells
df_merged = df_merged.replace(r'^\s*$', np.nan, regex=True)  
df_merged = df_merged.dropna(subset=['text_clean'])


# Save tweets
df_merged.to_feather(DATA_PATH + 'bigsss_tweets_FINAL.feather')


# %%