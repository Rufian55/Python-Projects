#!/bin/python
"""-------------------------------------------------------------------------------------------------
* ftclient.py is the client side source file for ftclient.
* Chris Kearns, CS372-400-Spring_2017, Project 2, 4 June 2017. kearnsc@oregonstate.edu
* Program is the client side of an ftp directory and file transfer program
* utilizing defined ports from 1024 to 65535 and the commands -l and -g.
* Command -l is for send/recv the directory listing the server process is running in.
* Command -g is for send/recv a specific file as requested by the client/user.
* See also ftserver.c and its executable ftserver.
* Compile with enclosed makefile.
* To get the server's directory:
    Usage: ftclient <Server hostName> <server portNum> <command \"-l\"> <client portNum>
* to get a file from server usage:
    Usage: ftclient <Server hostName> <server portNum> <command \"-g\"> <fileName> <client portNum>
* SERVER MUST BE RUNNING PRIOR TO ANY CLIENT PROCESS BEING INSTANTIATED!
 ------------------------------------------------------------------------------------------------"""
from socket import *
import sys, os.path

""" Convenience "faux" constants. """
BUFFSIZE = 100
MAXCHUNK = 1024
PORTLOW = 1024
PORTHIGH = 65535


def test4ValidArgs():
    """ An if/else chain that tests for command line argument validity. """
    if len(sys.argv) < 5 or len(sys.argv) > 6:
        print "Error! Invalid number of command line arguments."
        usage()
        exit(1)
    elif (len(sys.argv) == 5 and (not isInt(sys.argv[2]) or not isInt(sys.argv[4]))):
        print "Error! Both Server portNum and Client portNum must be integers!"
        usage()
        exit(1)
    elif (len(sys.argv) == 5 and sys.argv[3] != "-l"):
        print "Error! 5 arguments allows -l command only!"
        usage()
        exit(1)
    elif (len(sys.argv) == 6 and (not isInt(sys.argv[2]) or not isInt(sys.argv[5]))):
        print "Error! Both Server portNum and Client portNum must be integers!"
        usage()
        exit(1)
    elif (len(sys.argv) == 6 and sys.argv[3] != "-g"):
        print "Error! 6 arguments allows -g command only!"
        usage()
        exit(1)
    elif (sys.argv[1] != "flip1" and sys.argv[1] != "flip2" and sys.argv[1] != "flip3"):
        print "Error! Invalid server name, please use flip1, flip2, or flip3 for Server HostName."
        usage()
        exit(1)
    elif (int(sys.argv[2]) > PORTHIGH or int(sys.argv[2]) < PORTLOW):
        print "Error! Invalid server portNum. Must be >= 1024 and <= 65535."
        usage()
        exit(1)
    elif (sys.argv[3] != "-l" and sys.argv[3] != "-g"):
        print "Error! Invalid user command. Use -l for list server directory or -g for get a file.\nOmit the word \"command\""
        usage()
        exit(1)
    elif (sys.argv[3] == "-l" and (int(sys.argv[4]) > PORTHIGH or int(sys.argv[4]) < PORTLOW)):
        print "Error! Invalid client portNum specified. Must be >= 1024 and <= 65535."
        usage()
        exit(1)
    elif (sys.argv[3] == "-g" and (int(sys.argv[5]) > PORTHIGH or int(sys.argv[5]) < PORTLOW)):
        print "Error! Invalid client portNum specified. Must be >= 1024 and <= 65535."
        usage()
        exit(1)


def usage():
    """ Prints usage information. """
    print "Usage: ftclient <Server hostName> <server portNum> <command \"-l\"> <client portNum>"
    print "or"
    print "Usage: ftclient <Server hostName> <server portNum> <command \"-g\"> <fileName> <client portNum>"


def isInt(anArg):
    """ Test for port numbers are integers. Citation [1] """
    result = True
    num = 0
    for aChar in anArg:
        if '0' <= aChar <= '9':
            num  = num * 10 + ord(aChar) - ord('0')
        else:
            result = False
    return result


def createSocket():
    """ Builds and returns a socket for data transfer from server. Citation [3][5] """
    if sys.argv[3] == "-l":
        index = 4
    elif sys.argv[3] == "-g":
        index = 5
    clientDataPort = int(sys.argv[index])
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.bind(('', clientDataPort))
    clientSocket.listen(1)
    socketFD, addr = clientSocket.accept()
    return socketFD


def getClientIPaddress():
    """ Derives and returns client IP address. See Citation [2]. """
    sockPuppet = socket(AF_INET, SOCK_DGRAM)
    sockPuppet.connect(("8.8.8.8", 80))
    ipAddress = sockPuppet.getsockname()[0]
    return ipAddress


def connect2Server():
    """ Connects client to server and returns the clientSocket file descriptor
        for subsequent data transfer. Note machine name is the full URL. Citation [3][6] """
    serverName = sys.argv[1]+".engr.oregonstate.edu"
    serverPort = int(sys.argv[2])
    clientControlSocketFD = socket(AF_INET, SOCK_STREAM)
    clientControlSocketFD.connect((serverName, serverPort))
    return clientControlSocketFD


def getDirList(socketFD):
    """ Receives and prints the directory files as sent by ftserver. Citation [6]"""
    print "Receiving directory structure from {}:{}".format(sys.argv[1], sys.argv[4])
    fileName = socketFD.recv(BUFFSIZE)
    while fileName != "|_serverDone_|":
        print fileName
        fileName = socketFD.recv(BUFFSIZE)


def getFile(socketFD, fileName):
    """ Opens user specified file for writing via a file descriptor, reads in data
        from server, and writes it to the file after testing for file already exists
        and polling user for direction. Citations [4][7][8]"""
    print "Receiving \"{}\" from {}:{}".format(sys.argv[4], sys.argv[1], sys.argv[5])    
    if os.path.isfile(fileName):
        print "Attention! {} already exists in ftclient's current directory!".format(fileName)
        print "Do you wish to overwrite {}?".format(fileName)
        usersDesire = raw_input('Enter \"y\" or \"Y\" to overwrite, any other char to abort: ')
        if usersDesire == 'y' or usersDesire == 'Y':
            writeFile(socketFD)
            return True
        else:
            print "File {} write operation aborted.".format(fileName)
            return False
    else:
        writeFile(socketFD)
        return True


def writeFile(socketFD):
    """ Writes/overwrites file (sys.argv[4]) to ftclient's local directory. """
    fd = open(sys.argv[4], "w")
    tempBuffer = socketFD.recv(MAXCHUNK)
    while "|_server is done_|" not in tempBuffer:
        fd.write(tempBuffer)
        tempBuffer = socketFD.recv(MAXCHUNK)
    fd.close()


def processRequests(clientControlSocketFD):
    """ Using the passed in clientControlSocket file descriptor, executes logic for
        -l vs. -g requests, processes send() and recv() messages, instantiates a
        clientDataSocket for transferring data from ftserver, and closes data socket. [3][4]"""
    if sys.argv[3] == "-l":
        portNum = 4
    elif sys.argv[3] == "-g":
        portNum = 5
    """ Send ftclient's portNum so ftserver knows what port to send to. """
    clientControlSocketFD.send(sys.argv[portNum])
    """ Confirmation. """
    clientControlSocketFD.recv(MAXCHUNK)
    """ Match data flows with ftserver's _handleReqeust() internal method. """
    if sys.argv[3] == "-l":
        clientControlSocketFD.send("-l")
    else:
        clientControlSocketFD.send("-g")
    """ Confirmation. """
    clientControlSocketFD.recv(MAXCHUNK)
    """ Send ftclients local ipAddres to receive data on. """
    clientControlSocketFD.send(getClientIPaddress())
    """ Receive the requested data. """
    response = clientControlSocketFD.recv(MAXCHUNK)

    if response == "fail":
        print "Server received an invalid command"
        return
    if sys.argv[3] == "-g":
        clientControlSocketFD.send(sys.argv[4])
        response = clientControlSocketFD.recv(MAXCHUNK)
        if response != "File_found":
            print "{}:{} says FILE NOT FOUND".format(sys.argv[1], sys.argv[2])
            return
    """ Instantiate client's data socket for data transfer calls. """
    clientDataSocketFD = createSocket()
    if sys.argv[3] == "-l":
        getDirList(clientDataSocketFD)
    elif(sys.argv[3] == "-g"):
        result = getFile(clientDataSocketFD, sys.argv[4])
        if result:
            print "File transfer complete."
    clientDataSocketFD.close()


if __name__ == "__main__":
    """ The main() driver function. """
    test4ValidArgs()
    clientControlSocketFD = connect2Server()
    processRequests(clientControlSocketFD)
    clientControlSocketFD.close()


"""
CITATIONS Code adapted from the following sources as annotated above:
[1] https://mail.python.org/pipermail/python-list/2003-August/190235.html
[2] http://stackoverflow.com/questions/24196932/how-can-i-get-the-ip-address-of-eth0-in-python
[3] https://docs.python.org/2/howto/sockets.html
[4] https://stackoverflow.com/questions/289035/receiving-data-over-a-python-socket
[5] https://pythontips.com/2013/08/06/python-socket-network-programming/
[6] https://docs.python.org/2/library/socket.html
[7] https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-using-python
[8] https://stackoverflow.com/questions/3345202/getting-user-input
"""