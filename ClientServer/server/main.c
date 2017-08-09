/**************************************************************************************
* Program main.c is the driver file for the ftserver compilation.
* Chris Kearns, CS372-400-Spring_2017, Project 2, 4 June 2017
* kearnsc@oregonstate.edu
* To start the server: ftserver <Port>, to stop the server, Ctrl-c
* Program is the server side of an ftp directory and file transfer program
* utilizing defined ports from 1024 to 65535 and the commands -l and -g.
* Command -l is for send/recv the directory listing the server process is running in.
* Command -g is for send/recv a specific file as requested by the client/user.
* See also ftclient.py and its executable ftclient.
* Compile with enclosed makefile.
* Usage: ftserver <portNum>
*************************************************************************************/
#include "ftserver.h"

int main(int argc, char **argv) {

	registerSignalHandler();

	//Test for appropirate user supplied args from command line.
	if (argc != 2 || atoi(argv[1]) > PORTHIGH || atoi(argv[1]) < PORTLOW) {
		fprintf(stderr, "Usage: ftserver <Port #> \n"
			"Port number must be >= 1024 and <= 65535.\n");
		exit(1);
	}

	printf("Server %s open on port %s. Enter Ctrl-c to stop server.\n", argv[0], argv[1]);

	struct addrinfo * serverAddress = getServer_addrinfo_Struct(argv[1]);
	int socketFD = createSocket(serverAddress);
	bindSocket(socketFD, serverAddress);
	listen4Connection(socketFD);
	acceptConnection(socketFD);
	freeaddrinfo(serverAddress);  // Citation [8]

	return 0;
}

/* CITATIONS: Code within ftserver.h, ftserver.c, and main.c adapted from the following:
[1] https://linux.die.net/man/3/gai_strerror
[2] http://man7.org/linux/man-pages/man3/memset.3.html
[3] https://linux.die.net/man/3/socket
[4] Adapted from program signalsInActionDemo.c, B. Brewster, Oregon State Universtiy, 2016
[5] http://man7.org/linux/man-pages/man2/bind.2.html
[6] http://man7.org/linux/man-pages/man2/listen.2.html
[7] http://man7.org/linux/man-pages/man2/accept.2.html
[8] https://linux.die.net/man/3/freeaddrinfo
[9] https://linux.die.net/man/2/socket
[10] https://linux.die.net/man/2/connect
[11] http://faq.cprogramming.com/cgi-bin/smartfaq.cgi?answer=1046380353&id=1044780608
[12] http://stackoverflow.com/questions/2014033/send-and-receive-a-file-in-socket-programming-in-linux-with-c-c-gcc-g
[13] http://man7.org/linux/man-pages/man2/open.2.html
[14] http://man7.org/linux/man-pages/man2/read.2.html
[15] https://linux.die.net/man/3/write
[16] https://linux.die.net/man/3/send
[17] https://linux.die.net/man/3/recv
[18] https://linux.die.net/man/3/sprintf
*/
