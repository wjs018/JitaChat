# Jita Chatlog Analysis

This is a Python 2.x repo with programs to parse and analyze the saved chatlog from the Jita solar system in EVE Online. Eventually, I want to implement some type of machine learning (likely k-means clustering with the possibility of building a classifier in the future) to help distinguish human chat participants from automated ones. The data is unlabeled, so some type of unsupervised learning will need to be initially performed before any kind of supervised classification can take place.

The chatlog being used to develop this can be downloaded [here](https://drive.google.com/open?id=0B2mu_j-30Ue-WWFfQ1o5bFh3Sjg) and is provided courtesy of [Chribba](https://www.reddit.com/user/ChribbaX).

## Contents

This is very much a work in progress. A rough outline of the programs and what they do:

* ParseLog.py - This parses the .log file into a sqlite database for faster data analysis later.

## Dependencies

* Python 2.x

## Contact

* Walter Schwenger, wjs018@gmail.com
