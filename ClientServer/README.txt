CS-372-400-S17, Chris Kearns, kearnsc@oregonstate.edu, 7 May 2017

Assuming you have unzipped to a working directory on one of the OSU 
three flip servers:

zip payload:
	README.txt (this file)
	makefile
	chatClient.c
	chatServer.py

Enter 'make' without the quotation marks.
This will generate two executables:
	chatserve
	chatclient

Prior to starting chatserve, retrieve the hostname to start
chatclient by entering "hostname -s" from the command line,
ON THE MACHINE CHATSERVE WILL BE STARTED ON. This hostname 
will be used when starting chatclient in step 2.

Step 1: Start chatserve by entering:
	chatserve <non common port_number of your choice>

Enter your user_name and chatserve will go into listening status.
Once a client connects you will see the message "Greetings <your 
user_name>, ChatServe is ready to receive messages!" 

When chatclient intitiates a connection to clientserve, the message
"Received connection on address ('client's IP address', client's Port
number)" will be displayed.  Client messages first, so you have to
wait for the client's first message before you can respond.

When chatclient sends a message, it will be displayed with their
user_name preceding it, and your message prompt with your user_name
preceding it will immediately follow, ready to accept your message.
500 characters is the maximum message size.

Send chatclient "\quit" w/o the "" to end the connection to chatclient.
clientserve will go back into listening status and display "Connection 
closed" followed by "Waiting for new connection".  On clientserve, a
"Connection closed by server." followed by "Chatserve user <user_name>
closed connection." will be displaye.

To shut down chatserve completely, enter Ctrl+c.

Step 2: Start chatclient by entering:
	chatclient <hostname> <same common port_number as above>

Enter your user_name (pick a different one) and the prompt will appear,
ready to accept and send your message.  500 characters is the maximum
message size.

Enter '\quit' to end the connection and exit chatclient. chatserve
will go back into listening status.  You can reconnect with the same port
number at any time as long as chatserve is still running.

Each new message received by either side will be preceded by the other
sides user_name.

Type "make clean" from the command line and the chatserve and chatclient
executables will be removed.  Source files will not.