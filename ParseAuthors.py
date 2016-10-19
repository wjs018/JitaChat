"""This program provides functions to analyze the parsed chatlog.

__main__ builds a new SQLite database that stores the analyzed chatlog on a per
author basis. This data can then be used for later analysis."""

import sqlite3
#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer


def get_authors(dataframe, limit=None):
    """Returns an array of all the unique authors from a pandas dataframe"""
    
    authors = dataframe.author.unique()
    
    if limit:
        authors = np.random.permutation(authors)[0:limit]
    
    return authors

def get_clean_messages(author, dataframe, limit=None, min_interval=None, max_interval=None, rand=False):
    """Retrieve the cleaned messages by a given author from a dataframe.
    min_interval, max_interval allow for only messages with a certain range of
    messageInterval to be selected. if True, rand will randomize the output
    and if limit is set, will randomly draw from the total number of messages."""
    
    clean_messages = dataframe.loc[dataframe['author'] == author]
    
    if min_interval:
        clean_messages = clean_messages.loc[clean_messages['messageInterval'] >= min_interval]
    
    if max_interval:
        clean_messages = clean_messages.loc[clean_messages['messageInterval'] <= max_interval]
    
    if rand:
        clean_messages = clean_messages.sample(frac=1).reset_index(drop=True)
    
    if limit:
        clean_messages = clean_messages.head(limit)
    
    clean_messages = clean_messages.messageClean
    
    return clean_messages

def get_intervals(author, dataframe, limit=None, min_interval=None, max_interval=None, rand=False):
    """Retrieve a list of the intervals between messages for a given author
    from a dataframe."""
    
    interval_list = dataframe.loc[dataframe['author'] == author]
    
    if min_interval:
        interval_list = interval_list.loc[interval_list['messageInterval'] >= min_interval]
    
    if max_interval:
        interval_list = interval_list.loc[interval_list['messageInterval'] <= max_interval]
    
    if rand:
        interval_list = interval_list.sample(frac=1).reset_index(drop=True)
    
    if limit:
        interval_list.head(limit)
    
    interval_list = interval_list.messageInterval
    
    return interval_list

def find_area(x_data, y_data):
    """Finds the area under the curve given by points (x_data, y_data) using
    the trapezoid rule. Input data must be ordered."""
    
    area = 0
    
    for i in range(len(x_data)-1):
        
        a_x = x_data[i]
        a_y = y_data[i]
        b_x = x_data[i+1]
        b_y = y_data[i+1]
        
        area += (b_x - a_x) * 0.5 * (b_y + a_y)
    
    return area

def normalize(data):
    """Normalizes an array of data by subtracting the mean from each value and
    dividing by the standard deviation. This essentially replaces each value
    with the t-statistic for that value."""
    
    data = (data - np.mean(data)) / np.std(data)
    
    return data


if __name__ == '__main__':
    
    # Filepath of local .sqlite database from ParseLog.py
    
    db_path = '/media/sf_G_DRIVE/jita1407/jita.sqlite'
    
    # Load db into a pandas dataframe
    
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    dataframe = pd.read_sql_query("SELECT * FROM ChatLog", conn, parse_dates=["messageTime"])
    conn.close()
    
    # Get the list of authors
    
    #author_limit = 1000
    author_limit = None
    
    author_list = get_authors(dataframe, limit=author_limit)
    author_shortlist = []
    
    print 'Got Authors'
    
    # Specify the parameters of the message search we will use
    
    limit = 5000        # more messages than this and memory on my machine runs out
    min_interval = 0    # ignores first post
    max_interval = 1200 # ignore messages with more than a 20 minute gap
    #max_interval = None
    rand = True         # randomize message selection
    
    # Search for messages by a given author
    
    for name in author_list:
        
        author_dict = {}
        author_dict['author'] = name
        
        # Get the total number of messages by the author and unique messages
        
        all_messages = get_clean_messages(name, dataframe)
        num_messages = len(all_messages)
        author_dict['num_messages'] = num_messages
        unique_messages = len(all_messages.unique())
        author_dict['unique_messages'] = unique_messages
        frac_unique = float(unique_messages) / float(num_messages)
        author_dict['frac_unique'] = frac_unique
        
        # Get a random sample of up to 5000 messages by the author falling
        # within a certain interval range
        
        messages = get_clean_messages(name, dataframe, limit, 
                                      min_interval=min_interval, 
                                      max_interval=max_interval, rand=rand)
        
        # Check to make sure there are qualifying messages
        
        if len(messages) <= 10:
            continue
        
        # Convert messages to TF-IDF features to measure similarity
        
        vectorizer = TfidfVectorizer()
        try:
            tfidf = vectorizer.fit_transform(messages)
        except:
            continue
        
        # Find the cosine distance between messages
        
        normalized_matrix = (tfidf * tfidf.T).A
        
        # Find the mean for each message, renormalize, find percentiles
        
        means = normalized_matrix.mean(axis=0)
        means = np.divide(means, np.amax(means))
        
        mean_percentiles = np.percentile(means, np.linspace(10,90, num=9))
        
        # Find area under a mean_percentiles vs. percentiles curve, 1.0 = all percentiles are 1.0 (similar to ROC)
        
        x_data = np.linspace(0, 1.0, num=11)
        y_data = np.append(np.insert(mean_percentiles, 0, 0), 1.0)
        
        mean_area = find_area(x_data, y_data)
        
        author_dict['mean_area'] = mean_area
        
        # Get interval data and calculate percentiles
        
        intervals = get_intervals(name, dataframe, min_interval=min_interval,
                                  max_interval=max_interval)
        
        # Calculate some additional statistics on intervals
        
        median_int = np.percentile(intervals, 50)
        mean_int = np.mean(intervals)
        std_int = np.std(intervals)
        skew_int = 3 * (mean_int - median_int) / std_int
        
        author_dict['int_median'] = median_int
        author_dict['int_mean'] = mean_int
        author_dict['int_std'] = std_int
        author_dict['int_skew'] = skew_int
        
        # Add this dict to our list of author names
        
        author_shortlist.append(author_dict)
        
        if len(author_shortlist) % 1000 == 0:
            print str(len(author_shortlist)) + ' authors'
    
    # Make this list of dicts into a dataframe
    
    short_dataframe = pd.DataFrame(author_shortlist)
    
    # Normalize some of the variables that can be on a very different scale
    
    short_dataframe.num_messages = normalize(short_dataframe.num_messages)
    short_dataframe.unique_messages = normalize(short_dataframe.unique_messages)
    short_dataframe.int_mean  = normalize(short_dataframe.int_mean)
    short_dataframe.int_median = normalize(short_dataframe.int_median)
    short_dataframe.int_std = normalize(short_dataframe.int_std)
    
    # Write new sqlite database with author information
    
    db2_path = '/media/sf_G_DRIVE/jita1407/authors.sqlite'
    conn = sqlite3.connect(db2_path)
    
    short_dataframe.to_sql('Authors', conn, if_exists='replace')
    
    conn.commit()
    conn.close()