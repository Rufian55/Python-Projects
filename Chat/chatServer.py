#!/usr/bin/env python
"""*************************************************************************************
* chatServer.py is the source file for the server side chat module.
* "Compile" with provided makefile - resulting file is chatserve with mode == 760.
* You must start the chatserve server prior to running chatclient and use the
* port number chatserve is running on in the command line call when starting chatclient.
* Usage: <chatserve executable name> <port number>
* On nix type systems, hostname can be retrieved by calling "hostname -s".
* To shutdown chatserve, enter Ctrl+c. To end current chat session with client and 
* listen for new connections, enter "\quit", w/o the " " marks, at the message prompt.
*************************************************************************************"""
from socket import *
import signal, sys

NAMEBUFFER = 10
MESSAGEBUFFER = 500

def signalHandler(signal, frame):
    """ Handles Ctrl+c keyboard interrupt [1] """
    print "\nThanks for chatting with ChatServe!"
    sys.exit(0)

def startServer():
    """ Set up chatserve host to listen on user defined port number. [2][4][5] """
    serverPort = sys.argv[1]
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', int(serverPort)))
    serverSocket.listen(1)
    return serverSocket

def getUserName():
    """ Returns user inputed userName for use as chatserve prompt. """
    userName = raw_input("Please enter a userName <= 10 characters: ")
    while len(userName) == 0 or len(userName) > NAMEBUFFER:
        userName = raw_input("Error! Please enter a userName <= 10 characters: ")
    print "Greetings {}, ChatServe is ready to receive messages!".format(userName) # Citation [3]
    return userName


def handshake(connectionSocket, userName):
    """ Exchanges userNames with the incoming connection. """
    clientName = connectionSocket.recv(NAMEBUFFER)
    connectionSocket.send(userName)
    return clientName


def chat(connectionSocket, clientName, userName):
    """ Initializes and waits to begin a two user chat session between chatclient & chatserve. [2][4][5] """
    while 1:
        """ Receive Messages. """
        messageReceived = connectionSocket.recv(MESSAGEBUFFER)
        if messageReceived == "":
            print "Connection closed by chatclient \"{}\".".format(clientName)
            print "Waiting for new connection..."
            break
        print "{}> {}".format(clientName, messageReceived)

        """ Send Messages """
        message2send = ""
        while len(message2send) == 0 or len(message2send) > MESSAGEBUFFER:
            message2send = raw_input("{}> ".format(userName))
        if message2send == "\quit":
            print "Connection closed."
            print "Waiting for new connection."
            break
        connectionSocket.send(message2send)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: chatserve <Port Number>"
        exit(1)

    """ Register signal handler for SIGINT [1] """
    signal.signal(signal.SIGINT, signalHandler)
    
    print "\nSend '\quit' (w/o '') to end chat with current client."
    print "Enter Ctrl+c to Stop ChatServe at any time."

    serverSocket = startServer()
    userName = getUserName()

    """ Process messages - chat() does the heavy lifting. """
    while 1:
        connectionSocket, address = serverSocket.accept()
        clientName = handshake(connectionSocket, userName)
        print "Received connection on address {}".format(address)
        chat(connectionSocket, clientName, userName)
        connectionSocket.close()

""" CITATIONS:
[1] http://stackoverflow.com/questions/1112343/how-do-i-capture-sigint-in-python
[2] https://www.tutorialspoint.com/python/python_networking.htm
[3] https://pyformat.info/
[4] Lecture and materials as professed by Mr. Stephen Redding, Oregon State University, 2017
[5] Computer Networking, A Top-Down Approach, 6th Ed., Section 2.7, Kurose & Ross, 2013
"""
