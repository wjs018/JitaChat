"""This program first reads in the sqlite database made by ParseAuthors.py.
Then, after just a little data cleaning, it undergoes PCA decomposition.
After being decomposed via PCA, the author data is then clustered by way of a
K-means clustering algorithm. The number of clusters can be set by changing
the value of n_clusters."""

import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

if __name__ == '__main__':
    
    # Filepath of sqlite database made by ParseAuthors.py
    
    db_path = '/media/sf_G_DRIVE/jita1407/authors.sqlite'
    
    # Load this into a dataframe
    
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    dataframe = pd.read_sql_query("SELECT * FROM Authors", conn)
    conn.close()
    
    # Get rid of some redundant data to make analysis cleaner and more straightforward
    
    dataframe = dataframe.drop(['int_skew', 'unique_messages'], axis=1)
    
    # Separate out our list of Authors from the data about them
    
    authors = dataframe.ix[:,1].copy()
    data = dataframe.ix[:,2:7].copy()
    
    # Set up our PCA decomposition
    
    pca = PCA()
    pca.fit(data.as_matrix())
    
    # Transform our data into features calculated by PCA
    
    transformed = pca.transform(data.as_matrix())
    
    # Cluster our data according to K-means
    
    n_clusters = 2      # number of clusters to organize data into
    n_init = 20         # number of times to replicate clustering
    n_jobs = 1          # number of processors to use for clustering (-1 for all)
    
    kmeans = KMeans(n_clusters=n_clusters, n_init=n_init, n_jobs=n_jobs).fit(transformed)
    
    # Get the results of the clustering
    
    centers = kmeans.cluster_centers_
    labels = kmeans.labels_
    
    # Make some plots
    
    # Plot explained variance for each PCA component
    
    #plt.bar(np.arange(len(pca.explained_variance_)), pca.explained_variance_)
    
    