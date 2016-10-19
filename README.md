# Jita Chatlog Analysis

This is a Python 2.x repo with programs to parse and analyze the saved chatlog from the Jita solar system in EVE Online. Eventually, I want to implement some type of machine learning (likely k-means clustering with the possibility of building a classifier in the future) to help distinguish human chat participants from automated ones. The data is unlabeled, so some type of unsupervised learning will need to be initially performed before any kind of supervised classification can take place. 

Since I can only intermittently work on this project, I have structured the program to create sqlite databases along the analysis pipeline so that data can be stored in a non-volatile way and accessed at a much later time. This is an absolutely necessary step for the initial chatlog analysis due to the size since it couldn't be stored in memory in something like a Pandas dataframe. Similarly, in `ParseAuthors.py` I cap the amount of messages to analyze using Tf-Idf due to the memory limitations of my hardware. I do make sure that the messages that are use are randomly sampled from the entire corpus so hopefully it provides a representative sample of that author's work.

The chatlog being used to develop this can be downloaded [here](https://drive.google.com/open?id=0B2mu_j-30Ue-WWFfQ1o5bFh3Sjg) and is provided courtesy of [Chribba](https://www.reddit.com/user/ChribbaX).

## Contents

This is very much a work in progress. A rough outline of the programs and what they do:

* `ParseLog.py` - This parses the .log file into a sqlite database for faster data analysis later.
* `ParseAuthors.py` - This analyzes the database created by `ParseLog.py` and builds a new database that houses aggregated and normalized data on a per-author basis. This will be the information used in the machine learning algorithm.

## Dependencies

* Python 2.x

## Contact

* Walter Schwenger, wjs018@gmail.com
