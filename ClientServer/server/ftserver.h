/********************************************************************************
* Program ftserver.h is the header file for the ftserver compilation.
*********************************************************************************/
#ifndef FTSERVER_H
#define FTSERVER_H

#include <arpa/inet.h>
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <netdb.h>
#include <signal.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

//Constants
#define PORTLOW 1024	// Lowest port number server will accept.
#define PORTHIGH 65535	// Hightest Port number server will accept.
#define BUFFLEN 100		// General pupose buffer length (# dir files, fileName len, ipAddress len)
#define UCMDLEN 3		// Maximum length of a user command.
#define MAXCHUNK 1024	// When sending, maximum chunk in Bytes.
#define SLEEP 2		// Sleep interval to allow python clients to set up their sockets.

// Prototypes.
void registerSignalHandler();
void catchSIGINT(int signo);
struct addrinfo *getServer_addrinfo_Struct(char *portNum);
int createSocket(struct addrinfo * serverAddress);
void bindSocket(int socketFD, struct addrinfo *serverAddress);
void listen4Connection(int socketFD);
void acceptConnection(int socketFD);

// FYI Only - Prototypes for internal functions (not required).
struct addrinfo *_getClient_addrinfo_Struct(char *ipAddress, char *portNum);
void _connectSocket(int socketFD, struct addrinfo *serverAddress);
char ** _buildDirFileArray(int numFiles);
int _getFilesAndCount(char **files);
_Bool _fileIsInDir(char **files, int numFiles, char *fileName);
void _sendFile(char *ipAddress, char *portNum, char *fileName);
void _sendDirectory(char *ipAddress, char *portNum, char **files, int numFiles);
void _handleRequest(int newFD);
void _manageMemory(char **files, int numFiles);

#endif
