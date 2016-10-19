#=========================================================================
# Parses Jita chat logs and puts them into a sqlite database.
#=========================================================================

import codecs
import datetime as dt
import sqlite3
import re

from nltk.stem import SnowballStemmer

def parse_logfile(logfile_path, sqlite_path):
    """Parses a jita chat log file given by the logfile_path and
    dumps it into a sqlite database saved at sqlite_path. The
    database does not need to exist prior to execution."""
    
    # Filepaths

    log_path = logfile_path
    db_path = sqlite_path

    # Open and/or create files

    f = codecs.open(log_path, 'rb', 'utf-16')
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()

    # Read the first line (unused)

    header_line = f.readline()

    # Check to see if the table already exists

    c.execute(
        "SELECT * FROM sqlite_master WHERE name = 'ChatLog' and type = 'table';")
    tableExists = c.fetchall()

    # Drop the existing table if it exists

    if tableExists:
        c.execute("DROP TABLE ChatLog")

    # Create our database table

    c.execute("CREATE TABLE ChatLog(" +
              "messageTime TIMESTAMP, " +
              "author TEXT, " +
              "message TEXT, " +
              "messageClean TEXT, " +
              "authorLength INTEGER, " +
              "authorNonAlpha INTEGER, " +
              "authorNonAlNum INTEGER, " +
              "authorCapitals INTEGER, " +
              "authorNumbers INTEGER, " +
              "messageNonAlpha INTEGER, " +
              "messageNonAlNum INTEGER, " +
              "messageNumbers INTEGER, " +
              "messageLength INTEGER, " +
              "messageCapitals INTEGER, " +
              "messageInterval INTEGER);")

    # Keep track of the number of poorly formatted lines (for debugging)

    bad_lines = 0

    # Initialize a dictionary to keep track of message intervals

    last_message = {}
    
    # Initialize our Snowball stemmer
    
    stemmer = SnowballStemmer("english")

    # Iterate through the file

    for line in f:

        # If the line doesn't start with the timestamp, just skip to the next

        if line[0] != '2':
            bad_lines += 1
            continue

        # Extract the timestamp string of the message

        timestamp = line[0:19]

        # Convert this string to a datetime object

        message_time = dt.datetime.strptime(timestamp, "%Y.%m.%d %H:%M:%S")

        # Extract author of the message as well as message contents, stripping
        # the newline characters at the end
        #
        # There are some lines that don't unpack successfully, thus the try
        # block. In total though, this number is very very small, ~0.003%

        try:
            [author, message] = line[20:].strip().split('\t')
        except:
            bad_lines += 1
            continue

        # Length of message

        message_length = len(message)

        # Get length of author's name

        author_length = len(author)

        # Take away all the non-alphanumeric characters

        author_sub = re.sub("[^a-zA-Z0-9 ]", '', author)

        # Find the difference in lengths to get the number of non-alphanumeric
        # characters

        author_nonalnum = author_length - len(author_sub)

        # Do the same thing with no numbers to find the number of digits 0-9

        author_sub = re.sub("[^a-zA-Z ]", '', author)
        author_nonalpha = author_length - len(author_sub)

        # Find the number of numbers in the author name

        author_numbers = len(re.sub("[^0-9]", '', author))

        # Count the number of capitals

        author_capitals = len(re.sub("[^A-Z]", '', author))

        # Check for non-alphabet, non-whitespace characters in message contents

        # Take away all the non-alphanumeric characters from the message

        message_temp = re.sub("[^a-zA-Z0-9 ]", '', message)
        message_nonalnum = message_length - len(message_temp)

        message_temp = re.sub("[^a-zA-Z ]", '', message)
        message_nonalpha = message_length - len(message_temp)

        # Count the number of capitals

        message_capitals = len(re.sub("[^A-Z]", '', message))

        # Count the number of numbers

        message_numbers = len(re.sub("[^0-9]", '', message))

        # Use regular expressions to replace text within brackets, [], as just
        # ContractLink

        message_sub = re.sub("\[[^]]*\]", 'ContractLink', message)

        # Use regular expressions to replace (Item Exchange) as just
        # ContractLink

        message_sub = re.sub("\(Item Exchange\)", 'ContractLink', message_sub)

        # Use regular expressions to replace (Auction) as just ContractLink

        message_sub = re.sub("\(Auction\)", 'ContractLink', message_sub)

        # Use regular expressions to replace (Courier) as just ContractLink

        message_sub = re.sub("\(Courier\)", 'ContractLink', message_sub)

        # Use regular expressions to replace detected urls with urlLink
        # This snippet of code from https://gist.github.com/uogbuji/705383

        url_pattern = re.compile(
            ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

        message_sub = re.sub(url_pattern, 'urlLink', message_sub)

        # Now, let's just get rid of all non-alphanumeric characters left in
        # the message

        message_sub = re.sub("[^a-zA-Z0-9 ]", '', message_sub)

        # Compress excess whitespace in message_sub

        message_sub = re.sub("\s+", ' ', message_sub).strip()
        
        # Now, let's stem the message with nltk
        
        message_list = message_sub.split(' ')
        message_stemmed_list = []
        
        for word in message_list:
            message_stemmed_list.append(stemmer.stem(word))
        
        message_sub_stemmed = " ".join(message_stemmed_list)

        # Find the interval between this message and the previous one by the
        # same author if it exists

        if author in last_message:

            # Get the time elapsed since last message

            message_interval = (
                message_time - last_message[author]).total_seconds()

            # Set the new last_message value

            last_message[author] = message_time

        else:

            # Set the value of last_message for the author

            last_message[author] = message_time

            # Set interval to -1 so it is ignored easily later

            message_interval = -1

        # Write our results to the sqlite database

        c.execute("INSERT INTO ChatLog (" +
                  "messageTime, " +
                  "author, " +
                  "message, " +
                  "messageClean, " +
                  "authorLength, " +
                  "authorNonAlpha, " +
                  "authorNonAlNum, " +
                  "authorCapitals, " +
                  "authorNumbers, " +
                  "messageNonAlpha, " +
                  "messageNonAlNum, " +
                  "messageNumbers, " +
                  "messageLength, "
                  "messageCapitals, " +
                  "messageInterval) " +
                  "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (message_time,
                                                             author,
                                                             message,
                                                             message_sub_stemmed,
                                                             author_length,
                                                             author_nonalpha,
                                                             author_nonalnum,
                                                             author_capitals,
                                                             author_numbers,
                                                             message_nonalpha,
                                                             message_nonalnum,
                                                             message_numbers,
                                                             message_length,
                                                             message_capitals,
                                                             message_interval))

    # Write our changes to the sqlite file

    conn.commit()

    # Finish up by closing our files

    f.close()
    conn.close()
    
    # Return the number of wrongly formatted lines (optional, but useful for debugging)
    
    return bad_lines

if __name__ == '__main__':

    # Filepaths

    log_path = '/media/sf_G_DRIVE/jita1407/jita.log'
    db_path = '/media/sf_G_DRIVE/jita1407/jita.sqlite'

    # Call our parsing function
    
    parsed = parse_logfile(log_path, db_path)