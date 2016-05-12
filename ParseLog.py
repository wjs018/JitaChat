#=========================================================================
# Parses Jita chat logs and puts them into a sqlite database.
#=========================================================================

import codecs
import datetime as dt
import sqlite3
import re

if __name__ == '__main__':

    # Filepaths

    log_path = '/media/sf_G_DRIVE/jita1407/jita.log'
    db_path = '/media/sf_G_DRIVE/jita1407/jita.sqlite'

    # Open and/or create files

    f = codecs.open(log_path, 'rb', 'utf-16')
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    c = conn.cursor()

    # Read the first line (unused)

    header_line = f.readline()
    
    # Create our database table
    
    c.execute("CREATE TABLE ChatLog(" +
          "messageTime, " +
          "author TEXT, " +
          "message TEXT, " +
          "messageClean TEXT, " +
          "authorNonAlpha INTEGER, " +
          "authorCapitals INTEGER, " +
          "messageNonAlpha INTEGER, " +
          "messageNonAlNum INTEGER, " +
          "messageNumbers INTEGER, " +
          "messageLength INTEGER);")

    # Iterate through the file

    for line in f:
        
        if line[0] != '2':
            continue

        # Extract the timestamp string of the message

        timestamp = line[0:19]

        # Convert this string to a datetime object

        message_time = dt.datetime.strptime(timestamp, "%Y.%m.%d %H:%M:%S")

        # Extract author of the message as well as message contents, stripping
        # the newline characters at the end
        
        try:
            [author, message] = line[20:].strip().split('\t')
        except:
            continue

        # Some iterative variables to initiate before subsequent loops

        author_nonalpha = 0
        author_capitals = 0
        message_capitals = 0
        message_nonalpha = 0
        message_nonalnum = 0
        message_numbers = 0
        
        # Length of message
        
        message_length = len(message)

        # Check for non-alphabet, non-whitespace characters in an author's name

        for i in range(len(author)):
            if not author[i].isalpha() or not author[i] == ' ':
                author_nonalpha += 1
            
            # Check for number of capital letters
            
            if author[i].isupper():
                author_capitals += 1

        # Check for non-alphabet, non-whitespace characters in message contents

        for i in range(len(message)):
            if not message[i].isalpha() or not message[i] == ' ':
                message_nonalpha += 1

            # Check if it is instead numeric as well

            if not message[i].isalnum() or not message[i] == ' ':
                message_nonalnum += 1
            
            # Check for number of capital letters
            
            if message[i].isupper():
                message_capitals += 1

        message_numbers = message_nonalpha - message_nonalnum

        # Use regular expressions to replace text within brackets, [], as just
        # ContractLink

        message_sub = re.sub("\[[^]]*\]", 'ContractLink', message)

        # Use regular expressions to replace (Item Exchange) as just
        # ContractLink

        message_sub = re.sub("\(Item Exchange\)", 'ContractLink', message_sub)

        # Use regular expressions to replace (Auction) as just ContractLink

        message_sub = re.sub("\(Auction\)", 'ContractLink', message_sub)

        # Use regular expressions to replace detected urls with urlLink
        # This snippet of code from https://gist.github.com/uogbuji/705383

        url_pattern = re.compile(
            ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')
        
        message_sub = re.sub(url_pattern, 'urlLink', message_sub)
        
        # Now, let's just get rid of all non-alphanumeric characters left in the message
        
        message_sub = re.sub("[^a-zA-Z0-9 ]", '', message_sub)
        
        # Compress excess whitespace in message_sub
        
        message_sub = re.sub("\s+", ' ', message_sub).strip()
        
        # Write our results to the sqlite database
        
        c.execute("INSERT INTO ChatLog (" +
                  "messageTime, " + 
                  "author, " +
                  "message, " +
                  "messageClean, " +
                  "authorNonAlpha, " +
                  "authorCapitals, " +
                  "messageNonAlpha, " +
                  "messageNonAlNum, " +
                  "messageNumbers, " +
                  "messageLength) " +
                  "VALUES (?,?,?,?,?,?,?,?,?,?)", (message_time,
                                                   author,
                                                   message,
                                                   message_sub,
                                                   author_nonalpha,
                                                   author_capitals,
                                                   message_nonalpha,
                                                   message_nonalnum,
                                                   message_numbers,
                                                   message_length))
    
    # Write our changes to the sqlite file
    
    conn.commit()
    
    # Finish up by closing our files
    
    f.close()
    conn.close()
        