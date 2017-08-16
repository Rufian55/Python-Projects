/****************************************************************************************
* chatClient.c is the source file for the client side chat module.
* Commpile individually as "gcc chatclient.c -g -Wall -o chatclient" or with provided
* makefile.  You must start the chatserve server prior to running chatclient and use the
* port number chatserve is running on in the command line call when starting chatclient.
* Usage: <chatclient executable name> <hostname> <port number>
* On nix type systems, hostname can be retrieved by calling "hostname -s" in the directory
* that chatserve is running.
* To quit, enter "\quit", w/o the quotation marks, at the message prompt.
****************************************************************************************/
#include <errno.h>
#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <unistd.h>

#define MESSAGE_BUFFER 500
#define NAME_BUFFER 10

// Prototypes.
void getUserName(char *userNameBuffer);
struct addrinfo *getAddressInfo(char *inputAddr, char *port);
int createSocket(struct addrinfo *result);
void connectSocket(int socketFD, struct addrinfo *res);
void handshake(int socketFD, char *userName, char *serverName);
void chat(int socketFD, char *userName, char *serverName);


int main(int argc, char **argv) {
	if (argc != 3) {
		fprintf(stderr, "Usage: <executableName> <hostName> <portNumber>\n");
		exit(1);
	}
	char userNameBuffer[NAME_BUFFER];
	char serverNameBuffer[NAME_BUFFER];

	getUserName(userNameBuffer);
	struct addrinfo *result = getAddressInfo(argv[1], argv[2]);
	int socketFD = createSocket(result);
	connectSocket(socketFD, result);
	handshake(socketFD, userNameBuffer, serverNameBuffer);
	chat(socketFD, userNameBuffer, serverNameBuffer);
	freeaddrinfo(result);

	return 0;
}

/* Modifies in place userNameBuffer with user provided "userName"
   string of between 1 and 10 character length inclusive. */
void getUserName(char *userNameBuffer) {
	printf("Please enter your 10 character userName: ");
	scanf("%10s", userNameBuffer);
	fflush(stdin);
}

/* Returns a pointer to the struct addrinfo *result that will herein be populated with
   the hostname and port number as provided by argv[1] and argv[2] per getaddrinfo().
   The hints parameter specifies the preferred socket type, or protocol - here IPv4
   (AF_INET) and TCP (SOCK_STREAM).  Program terminates on an invalid host:portNumber. [1][2]*/
struct addrinfo *getAddressInfo(char *inputAddress, char *port) {
	int errorStatus;
	struct addrinfo hints, *result;

	memset(&hints, 0, sizeof hints);	// Initial null set of hints addrinfo struct.
	hints.ai_family = AF_INET;		// IPv4.
	hints.ai_socktype = SOCK_STREAM;	// TCP.

	/* Populate results addrinfo struct from running instance of chatserve and if needed,
	   the hints addrinfo struct data as populated above. */
	if ((errorStatus = getaddrinfo(inputAddress, port, &hints, &result)) != 0) {
		fprintf(stderr, "getaddrinfo() error: %s\nPlease check the hostname and port number!\n",
			   gai_strerror(errorStatus));
		exit(1);
	}

	return result;
}


/* Returns a socket file descriptor from the addrinfo *results struct. [3]*/
int createSocket(struct addrinfo *result) {
	int socketFD;
	if ((socketFD = socket(result->ai_family, result->ai_socktype, result->ai_protocol)) == -1) {
		fprintf(stderr, "Error creating socket.\n");
		exit(1);
	}
	return socketFD;
}


/* Connect to the remote host through socketFD using the addrinfo *result struct. [4]*/
void connectSocket(int socketFD, struct addrinfo *result) {
	int errorStatus;
	if ((errorStatus = connect(socketFD, result->ai_addr, result->ai_addrlen)) == -1) {
		fprintf(stderr, "Error connecting socket.\n");
		exit(1);
	}
}


/* Sends the chatclient userName and receives the chatserve userName. */
void handshake(int socketFD, char *userNameBuffer, char *serverNameBuffer) {
	send(socketFD, userNameBuffer, strlen(userNameBuffer), 0);
	recv(socketFD, serverNameBuffer, NAME_BUFFER, 0);
}


/* Conducts an alternating two way chat between this program and a running
   instance of chatserve on a remote host. */
void chat(int socketFD, char *userName, char *serverName) {
	char messageIn[MESSAGE_BUFFER];	// Buffer for incoming messages.
	char messageOut[MESSAGE_BUFFER];	// Buffer for outgoing messages.
	int numBytesSent = 0;
	int errorStatus = NULL;

	// Clear both message buffers as a precaution.
	memset(messageIn, 0, sizeof(messageIn));
	memset(messageOut, 0, sizeof(messageOut));

	// Receive message so client is postioned to be the chat initiator.
	fgets(messageIn, MESSAGE_BUFFER, stdin);
	fflush(stdin);

	// Chat send/receive loop. Call to break exits program.
	while (1) {
		printf("%s> ", userName);				// User prompt.
		fgets(messageOut, MESSAGE_BUFFER, stdin);	// Get user's message to send.
		fflush(stdin);

		if (strcmp(messageOut, "\\quit\n") == 0) {
			break;
		}

		// Send the user's message via socketFD / test for and exit on errors. [5]
		if ((numBytesSent = send(socketFD, messageOut, strlen(messageOut), 0)) == -1) {
			fprintf(stderr, "Error sending data to chatserve host.\n");
			exit(1);
		}

		// Receive a message via socketFD / test for and exit on errors. [5]
		if ((errorStatus = recv(socketFD, messageIn, MESSAGE_BUFFER, 0)) == -1) {
			fprintf(stderr, "Error receiving data from chatserve host.\n");
			exit(1);
		} else if (errorStatus == 0) {
			printf("Connection closed by server.\n");
			break;
		} else {
			printf("%s> %s\n", serverName, messageIn);
		}

		// Reset message buffers to null.
		memset(messageIn, 0, sizeof(messageIn));
		memset(messageOut, 0, sizeof(messageOut));
	}

	close(socketFD);
	printf("Chatserve user \"%s\" closed connection.\n", serverName);
}

/* CITATIONS:
[1] http://beej.us/guide/bgnet/output/html/singlepage/bgnet.html#getaddrinfo
[2] http://stackoverflow.com/questions/755308/whats-the-hints-mean-for-the-addrinfo-name-in-socket-programming
[3] http://beej.us/guide/bgnet/output/html/singlepage/bgnet.html#socket
[4] http://beej.us/guide/bgnet/output/html/singlepage/bgnet.html#connect
[5] http://beej.us/guide/bgnet/output/html/singlepage/bgnet.html#sendrecv
*/
