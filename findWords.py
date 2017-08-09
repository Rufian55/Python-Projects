#!/usr/bin/python
# File: findWords.py
# Last Update: 11/20/2016
# Description: Take in a File and 'highlight' words within the file that match the words in the list.
# Built with Python 2.7.11

# Imports
import os
import re
import sys
import mysql.connector
from mysql.connector import errorcode


# Function to getting the list of words from MySQL database
def getWords():
    # Set variables
    words_list = ['Agreement']

    # Make a connection to the server and get the values
    # Source: https://scriptingmysql.wordpress.com/2011/09/09/retrieving-data-from-mysql-via-python/
    # Issue with getting connection to MySQL server
    #2003: Can't connect to MySQL server on 'oniddb.cws.oregonstate.edu:3306' (10060 A connection attempt failed because the connected party did not properly respond after a period of time, or established connection failed because connected host has failed to respond)
    #On Flip, my message is: 1130: Host 'flip3.engr.oregonstate.edu' is not allowed to connect to this MySQL
    try:
        cnx = mysql.connector.connect(user='aUserName', password='',
                                     host='aHostWith-db', database='db_name')
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        # Prepare a cursor object using cursor() method
        cursor = cnx.cursor()
        # Execute the SQL query using execute() method
        cursor.execute("select TCName from legal")
        # Fetch all of the rows from the query
        data = cursor.fetchall()

        # Append each data into the words_list
        for w in data:
            words_list.append(w[0])

        # Close the cursor object
        cursor.close()

        # Close the connection
        cnx.close()

    print words_list

    return words_list

# Function to ensure the file in arguments exists
def isFileValid(filename):
    if os.path.exists(filename):
        print ("Input file exists")
    else:
        print("Invalid File Path, File Doesn't Exist!  Please try again.")
        sys.exit(1)

# Function to open the file
def openFile(file_name):
    try:
        the_file = open(file_name)
    except IOError as e:
        print("Unable to open the file", file_name)
        the_file = ""
    return the_file

# Function to read through file, find words matching in the list, copy file to out file and highlight words
def fileParser(words_list, i_file, o_file):
    # Set variables
    out_file = open(o_file, 'a')

    # Loop through entire contents of input file and write to output file
    # Source: http://stackoverflow.com/questions/16922214/reading-a-text-file-and-splitting-it-into-single-words-in-python
    with open(i_file, 'r') as input_file:
        for line in input_file:
            for word in line.split():
                for w in words_list:
                    if w in word:
                        word = "<b>" + word + "</b>"
                        print ("Found a word!!!!")
                word = " " + word
                out_file.write(word)
            out_file.write("\n")

    out_file.close()
    input_file.close()


# Main management of program
def main():
    # Set variables
    num_args = len(sys.argv)

    # Check to make sure there are 2 args
    if num_args != 3:
        print ("Usage: findWords.py <inputFile> <outputFile>")
        sys.exit(1)

    # Get list of words in database
    words_list = getWords()

    # Ensure infile exists and open
    i_file = sys.argv[1]
    isFileValid(i_file)

    # Open the output file
    o_file = sys.argv[2]
    if os.path.exists(o_file):
        try:
            os.remove(o_file)
            print("Removing old output file")
        except OSError:
            print ("output file does not exist, creating new one")

    # Read through the file compare words in file with those in list and highlight matches
    fileParser(words_list, i_file, o_file)


main ()