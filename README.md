# Jita Chatlog Analysis

This is a Python 2.x repo with programs to parse and analyze the saved chatlog from the Jita solar system in EVE Online. I set out to see if there was a machine-learning method by which I could distinguish between human message authors and automated message authors. In total, there is more than 2.4 million messages in this data set. The details of the analysis I did can be found in the Procedure Walkthrough section.

Since I can only intermittently work on this project, I have structured the program to create sqlite databases along the analysis pipeline so that data can be stored in a non-volatile way and accessed at a much later time. This is an absolutely necessary step for the initial chatlog analysis due to the size since it couldn't be stored in memory in something like a Pandas dataframe. Similarly, in `ParseAuthors.py` I cap the amount of messages to analyze using Tf-Idf due to the memory limitations of my hardware. I do make sure that the messages that are use are randomly sampled from the entire corpus so hopefully it provides a representative sample of that author's work.

The chatlog being used to develop this can be downloaded [here](https://drive.google.com/open?id=0B2mu_j-30Ue-WWFfQ1o5bFh3Sjg) and is provided courtesy of [Chribba](https://www.reddit.com/user/ChribbaX).

## Contents

* `ParseLog.py` - This parses the .log file into a sqlite database for faster data analysis later.
* `ParseAuthors.py` - This analyzes the database created by `ParseLog.py` and builds a new database that houses aggregated and normalized data on a per-author basis. This will be the information used in the machine learning algorithm.
* `ClusterAuthors.py` - This first reads in the database created by `ParseAuthors.py`. After cleaning up the data a little bit, it then decomposes the data using PCA. Once the data is transformed using this new set of basis vectors, it is then clustered using k-means. By default, it is run using two clusters (ideally bots and not bots), but this can be changed by the user.

## Procedure Walkthrough

The first thing that I do with the data is parse it from a giant .log file into a sqlite database. This is done so that the contents is in a much nicer format to search using queries than just a giant plaintext file. This step also performs a bunch of cleaning operations and feature finding on the log. For example, text that is an in-game link to something in the client is replaced with a standard phrase depending on what it was linking so that it is better analyzed later. Similarly, urls are replaced with a standard phrase and non-alphanumeric characters as well as excess whitespace are removed.

Once the message log has been cleaned and saved into a searchable database, I go through the message log and aggregate information by author. Statistics like the average time between messages, the number of messages, the fraction of those messages that are unique are gathered. Most importantly the author's message corpus is analyzed using tf-idf in order to find an average cosine similarity score for each message. This score is normalized to range from 0 to 1 where higher scores mean it is more similar. Using these scores, I find the 10, 20, 30, ..., 80, and 90th percentile similarity score of the author's messages. This set of data, along with (0,0) and (1,1) allow me to form a curve similar to a ROC curve. Finding the area under this curve gives an indication of how similar the messages by the user were. A higher area under the curve indicates that high similarity scores were measured at lower percentiles, therefore a high degree of similarity overall. After all the feature finding, some features are rescaled and then the entire author list with data is saved as an sqlite database for future use.

Finally, I read in the author data from the database. I then eliminate some data that is redundant due to being combinations of other columns in the data. I then decompose the remaining data into its primary components using PCA. This was done so that some features would have the best chance of illustrating a wide spread and therefore separation of the clusters. After being tranformed by PCA, K-means clustering is run with two clusters. My thinking at the time was that this would be bots and non-bots, however that doesn't seem to be the case so far. I write more about ways this can be improved in the next section.

## Results and Future Work

Using the default values in the programs here, I have found that I don't really end up with a population of users that exhibit bot-like behavior and a population that seems human. Instead, it seems as though I almost exclusively end up with bots. To the point that if I am also selecting real users, they are sufficiently rare that they are not being selected as a separate cluster with k-means. This leads me to the conclusion that real users have mostly abandoned attempting to chat in Jita due to the shear volume of chat from the automated users.

There are ways that this analysis might be improved. First, mainly due to computation limitations, I only included authors that had more than 10 messages that followed the author's previous entry by less than 20 minutes. This turned out to be only about 20% of the total number of authors. It is possible that real users are hidden in the ~80% of users that don't post often enough to make it past that screening. If that were the case though, it would be an indication that the sheer volume of messages by other users make a sustained conversation among non-automated users all but impossible.

Second, I believe that the frac_unique could be made into a much more informative feature with a hefty amount of preprocessing. Basically, my thinking is that one way in which automated users can make a large portion of their messages unique is by including another random user's name in their message. Because Jita always has well in excess of 1000 users active at any time, choosing a name at random to include in your message would guarantee you a high fraction of unique messages despite an unnaturally high message volume. In order to count these as duplicate messages then, the messages would need to searched for character names and then those will be stemmed to something so as to correctly calculate the fraction of unique messages. This problem becomes difficult rather quickly however. Character names in EVE can be up to a 3-gram, meaning that there are an exceptionally large number of possible character names to check for in the entire message log. Also, even if we were to compile a list of all the authors in the message log to check against, the automated user could have included the name of a character that didn't speak, so whose name would not appear in the message log. This could be circumvented by searching an external database of all EVE characters such as [this](https://evewho.com/pilot/) by [Squizz Caphinator](https://www.reddit.com/u/squizz). However, even this isn't a perfect solution as characters are created and destroyed daily so there is no guarantee that this database is always up to date. The real solution ts that this problem would best be solved by better message logging. Indicating what is and isn't a link to a character name in the log would allow easily parsing names. The game client indicates this, so it is information that is known on the user's end, but it is just logged as plaintext.

Finally, there could be additional features that might prove informative. Things like the proportion of a message that is special characters, capital letters, numbers, whitespace, etc. could help indicate automated from human users. Another feature I thought might be informative is temporal distribution of the user's posting. If there is a user posting many many messages but they are all in a 2-4 hour window each day, that might just be a very active real user. However, if there is a user that has a similar volume of posts, but is active 20+ hours each day they post, that might be a good indication that the user is automated.

## Dependencies

* Python 2.x
* Numpy
* sklearn 0.18 or newer

## Contact

* Walter Schwenger, wjs018@gmail.com
