/********************************************************************************
* Program ftserver.c is the definitions file for the ftserver compilation.
* Chris Kearns, CS372-400-Spring_2017, Project 2, 4 June 2017
* kearnsc@oregonstate.edu
*********************************************************************************/
#include "ftserver.h"

/* Registers signal handler or SIGINT (typically stdin Ctrl-c. Citation [4]. */
void registerSignalHandler() {
	struct sigaction SIGINT_action;
	SIGINT_action.sa_handler = catchSIGINT;
	sigfillset(&SIGINT_action.sa_mask);
	SIGINT_action.sa_flags = 0;
	/* Register SIGINT signals to the respective struct for handling. */
	sigaction(SIGINT, &SIGINT_action, NULL);
}


/* Signal Interupt received (typically Ctrl-c from stdin)  [4] */
void catchSIGINT(int signo) {
	fprintf(stderr, "\nSignal %d raised.\n", signo);
	char* message = "Caught SIGINT, exiting gracefully...\n";
	write(STDOUT_FILENO, message, 37);
	exit(2);
}


/* Builds the addrinfo struct 'serverAddress' and returns it to the caller.
 * paramm: port number (user supplied) originally from the command line.
 * returns: addrinfo struct serverAddress.	See Citations [1] & [2] */
struct addrinfo* getServer_addrinfo_Struct(char *portNum) {
	int status;
	struct addrinfo hints;
	struct addrinfo *serverAddress;
	
	// Setup for IPv4 or Ipv6 Protocol.
	memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = 0;
	hints.ai_flags = AI_PASSIVE;

	if((status = getaddrinfo(NULL, portNum, &hints, &serverAddress)) != 0) {
		fprintf(stderr, "Call to getaddrinfo() for server failed: %s\n", gai_strerror(status));
		exit(1);
	}
	
	return serverAddress;
}


/* Instantiates a socket endpoint for struct addrinfo *serverAddress object. Citation [9].
 * param:	*serverAddress - pointer to the serverAddress addrinfo struct.
 * return: The resulting socket file descriptor. */
int createSocket(struct addrinfo *serverAddress){
	int socketFD;
	if ((socketFD = socket((serverAddress)->ai_family, serverAddress->ai_socktype, serverAddress->ai_protocol)) == -1) {
		fprintf(stderr, "Error on call to socket()\n");
		exit(1);
	}
	return socketFD;
}


/* Binds a socket to the server's 'struct addrinfo * serverAddress'.  Citation [5]
 * param: socketFD - the socket file descriptor.
 * param:	serverAddress - a struct * addrinfo. */
void bindSocket(int socketFD, struct addrinfo *serverAddress) {
	if (bind(socketFD, serverAddress->ai_addr, serverAddress->ai_addrlen) == -1) {
		close(socketFD);
		fprintf(stderr, "Error on call to bind().\n");
		exit(1);
	}
}


/* Listens for a new connections from a client attempt via socketFD.  Citation [6]
 * The maximum connections queue is set at 5. 
 * param: socektFD - the socket file descriptor as specified in addrinfo struct.*/
void listen4Connection(int socketFD){
	if(listen(socketFD, 5) == -1){
		close(socketFD);
		fprintf(stderr, "Error on call to listen().\n");
		exit(1);
	}
}


/* Continuouly waits to accept a new connection. On receipt, calls the request
* handler handleRequest() on a NEW socket file descriptor. Control returns
* here for NEW file descriptor close() on return from the call to handleRequest().
* param: socketFD - the socket the server is listening on.  Citation [7] */
void acceptConnection(int socketFD) {
	struct sockaddr_storage clientAddress;
	socklen_t addressSize;
	int newFD;
	while (1) {
		addressSize = sizeof(clientAddress);
		if ((newFD = accept(socketFD, (struct sockaddr *)&clientAddress, &addressSize)) == -1)
			continue;
		_handleRequest(newFD);
		close(newFD);
	}
}


/* Handles requests from client.  Will handle directory list transfer, file transfer, bad commands,
 * bad filenames, and message send()/recv() errors.  Functions send()/recv() not error handled as
 * server can recover from minor communication errors after initialization.
 * param: newFD - the newly created socket for data transfer. Citations [16], [17], & [18] */
void _handleRequest(int newFD) {
	char portNum[6];			// Client port number for data transfer.
	char command[UCMDLEN];		// Users command.
	char ipAddress[BUFFLEN];		// Client ipAddress.
	char *onSuccess = "pass";
	char *onFailure = "fail";
	memset(portNum, 0, sizeof(portNum));
	memset(command, 0, sizeof(command));
	memset(ipAddress, 0, sizeof(ipAddress));
	int numFiles, result = 0;

	/* Initialzation block tests send()/recv() for good 
	   message exchange on initialzation. Exits on failure.*/
	if(recv(newFD, portNum, sizeof(portNum) - 1, 0) > 0)		// Receive portNum client expecting data on.
		result++;
	if(send(newFD, onSuccess, strlen(onSuccess), 0) > 0)		// Confirm.
		result++;
	if (recv(newFD, command, sizeof(command) - 1, 0) > 0)		// Receive the user command.
		result++;
	if (send(newFD, onSuccess, strlen(onSuccess), 0) > 0)		// Confirm.
		result++;
	if (recv(newFD, ipAddress, sizeof(ipAddress) - 1, 0) > 0)	// Receive the client's ipAddress.
		result++;
	if(result == 5)
		printf("Incoming connection from %s\n", ipAddress);
	else {
		printf("Error on receiving client socket and user command details.\n");
		exit(1);
	}

	// User has requested the directory list. Function send()/recv() errors ignored.
	if(strcmp(command, "-l") == 0){
		send(newFD, onSuccess, strlen(onSuccess),0);
		printf("List directory requested on port %s\n", portNum);
		printf("Sending directory contents to %s:%s\n", ipAddress, portNum);
		char **files = _buildDirFileArray(BUFFLEN);
		numFiles = _getFilesAndCount(files);						// Array files passed by reference.
		_sendDirectory(ipAddress, portNum, files, numFiles);
		_manageMemory(files, BUFFLEN);
	}
	// User has requested a specific file.
	else if(strcmp(command, "-g") == 0){
		send(newFD, onSuccess, strlen(onSuccess), 0);				// Confirm command received.
		char filename[100];										// Container for fileNname string.
		memset(filename, 0, sizeof(filename));
		recv(newFD, filename, sizeof(filename) - 1, 0);
		printf("File \"%s\" requested on port %s\n", filename, portNum);
		char **files = _buildDirFileArray(BUFFLEN);
		int numFiles = _getFilesAndCount(files);
		_Bool fileExists = _fileIsInDir(files, numFiles, filename);
		
		if(fileExists){
			printf("Sending \"%s\" to client on %s:%s\n", filename, ipAddress, portNum);
			char *fileFound = "File_found";
			send(newFD, fileFound, strlen(fileFound), 0);
			char newFilename[BUFFLEN];							// Build new fileName to handle "./"
			memset(newFilename, 0, sizeof(newFilename));
			strcpy(newFilename, "./");
			char *preAppend = newFilename + strlen(newFilename);
			preAppend += sprintf(preAppend, "%s", filename);
			_sendFile(ipAddress, portNum, newFilename);
		}
		// User requested file not found.
		else{												
			printf("File \"%s\" requested on port %s.\n", filename, portNum);
			printf("File not found. Sending error message to %s:%s\n", ipAddress, portNum);
			char * fileNotFound = "File not found";
			send(newFD, fileNotFound, BUFFLEN, 0);
		}
		_manageMemory(files, BUFFLEN);
	}
	// Bad command received, send error message to client.
	else{													
		send(newFD, onFailure, strlen(onFailure), 0);
		printf("Invalid command received from client.\n");
	}
	printf("ftserver is resuming wait for incoming connections.\n");
}


/* Builds the addrinfo struct 'clientAddress' and returns it to the caller.
 *	paramm: portNum - client's portNum derived from function _handleRequest().
 *	returns: addrinfo struct clientAddress.	See Citations [1] & [2] */
struct addrinfo* _getClient_addrinfo_Struct(char *ipAddress, char *portNum) {
	int status;
	struct addrinfo hints;
	struct addrinfo * clientAddress;

	// Setup for IPv4 or Ipv6 Protocol.
	memset(&hints, 0, sizeof hints);
	hints.ai_family = AF_INET;
	hints.ai_socktype = SOCK_STREAM;
	hints.ai_protocol = 0;
	hints.ai_flags = AI_PASSIVE;

	if ((status = getaddrinfo(ipAddress, portNum, &hints, &clientAddress)) != 0) {
		fprintf(stderr, "Call to getaddrinfo() for client failed: %s\n", gai_strerror(status));
		exit(1);
	}

	return clientAddress;
}


/* Sends the directory listing per user request -l.  Note call to sleep() for slow client.
* param: ipAddress - the ipAddress of the client.
* param: portNum - the port number on which the client is expecting data transmission.
* param: files - the array of file c-strings to be sent.
* param: numFiles - the number of files in the directory less "." & ".."  Citation [16] */
void _sendDirectory(char *ipAddress, char *portNum, char **files, int numFiles) {
	sleep(SLEEP);
	struct addrinfo *clientAddress = _getClient_addrinfo_Struct(ipAddress, portNum);
	int dataSocketFD = createSocket(clientAddress);
	_connectSocket(dataSocketFD, clientAddress);

	int i;
	for (i = 0; i < numFiles; i++) {
		send(dataSocketFD, files[i], BUFFLEN, 0);
	}

	char *endOfTransmission = "|_serverDone_|";
	if ((send(dataSocketFD, endOfTransmission, strlen(endOfTransmission), 0)) == -1)
		printf("Error on call to send(). End of Transmission message may not have been sent!\n");

	close(dataSocketFD);
	freeaddrinfo(clientAddress);
}


/* Reads and writes (sends) the user specified file using the datasocketFD to the
* specified ipAddress and portNum.  Note call to sleep() for slow client.
* Note an inner and outer while loop for ensuring all Bytes are read & written.
* param: ipAddress - the ip address of the client.
* param: portNum - the CLIENT'S data port number derived within handelRequest().
* param: filename - the user requested file name.  Citations [12], [13], [14] & [15] */
void _sendFile(char *ipAddress, char *portNum, char *fileName) {
	printf("Sleeping while slow client sets up sockets.\n");
	sleep(SLEEP);
	int bytesRead, bytesWritten, fileDescriptor;
	char readBuffer[MAXCHUNK];
	void *ptr2readBuffer = NULL;

	struct addrinfo * clientAddress = _getClient_addrinfo_Struct(ipAddress, portNum);
	int dataSocketFD = createSocket(clientAddress);
	_connectSocket(dataSocketFD, clientAddress);
	memset(readBuffer, 0, sizeof(readBuffer));

	if ((fileDescriptor = open(fileName, O_RDONLY)) == -1) {
		printf("Error %s on call to open() %s.\n", strerror(errno), fileName);
	}

	// Outer loop until entire file is read into readBuffer
	while (1) {
		bytesRead = read(fileDescriptor, readBuffer, sizeof(readBuffer) - 1);
		if (bytesRead == 0)
			break;
		if (bytesRead == -1) {
			printf("Error %s on call to read() %s.\n", strerror(errno), fileName);
			return;
		}
		ptr2readBuffer = readBuffer;

		// Inner loop until entire readBuffer is sent.
		while (bytesRead > 0) {
			bytesWritten = send(dataSocketFD, ptr2readBuffer, sizeof(readBuffer), 0);
			if (bytesWritten < 0) {
				fprintf(stderr, "Error on call to write() readbuffer to socket\n");
				return;
			}
			bytesRead -= bytesWritten;
			ptr2readBuffer += bytesWritten;
		}
		memset(readBuffer, 0, sizeof(readBuffer));
	}

	memset(readBuffer, 0, sizeof(readBuffer));
	strcpy(readBuffer, "|_server is done_|");
	send(dataSocketFD, readBuffer, sizeof(readBuffer), 0);

	close(fileDescriptor);
	close(dataSocketFD);
	freeaddrinfo(clientAddress);
}


/* Connects a socket to a clientAddress per it's addrinfo struct.  Citation [10].
* param: socketFD - a socket file descriptor
* param: clientAddress - a pointer to the clientAddress addrinfo struct. */
void _connectSocket(int socketFD, struct addrinfo *clientAddress) {
	int status;
	if ((status = connect(socketFD, clientAddress->ai_addr, clientAddress->ai_addrlen)) == -1) {
		fprintf(stderr, "Call to connect() socket failed.\n");
		exit(1);
	}
}


/* Builds a container for sending fileName strings to client on -l command.
* param: numfiles - the number of files to be sent.  */
char** _buildDirFileArray(int numFiles) {
	char **dirContainer = malloc(numFiles * sizeof(char *));
	int i;
	for (i = 0; i < numFiles; i++) {
		dirContainer[i] = malloc(BUFFLEN * sizeof(char));
		memset(dirContainer[i], 0, (sizeof(char) * BUFFLEN));
	}
	return dirContainer;
}


/* Copys directory entries into our files[] array and returns the filecount. Citation [11]
* param: files - the files[] array passed by reference.
* returns: the count of files in the directory less "." and ".."  */
int _getFilesAndCount(char **files) {
	DIR *dirPtr;
	struct dirent *dir;
	dirPtr = opendir(".");
	int numFiles = 0;
	if (dirPtr) {
		while ((dir = readdir(dirPtr)) != NULL) {
			if (dir->d_type == DT_REG) {
				strcpy(files[numFiles], dir->d_name);
				numFiles++;
			}
		}
		closedir(dirPtr);
	}
	return numFiles;
}


/* Tests for a user specified file in the current directory - returns accordingly.
* param: files - the array of file names to be tested
* param: numfiles - the number of files in the array
* param: fileName - the user provided filename to be tested.
* returns: True or false Boolean. */
_Bool _fileIsInDir(char **files, int numFiles, char *fileName) {
	int fileIsThere = false;
	int i;
	for (i = 0; i < numFiles; i++) {
		if (strcmp(files[i], fileName) == 0) {
			fileIsThere = true;
		}
	}
	return fileIsThere;
}


/* Frees memory allocated to files array container.
* param: files - the array allocated by a call to _buildDirFileArray().
* param: numFiles - the number of files (array[numFiles][]) */
void _manageMemory(char **files, int numFiles) {
	int i;
	for (i = 0; i < numFiles; i++) {
		free(files[i]);
	}
	free(files);
}
