######################################################################
# cs372-400-S17	Introduction to Networks	07 May 2017	Project 1
# Chris Kearns		kearnsc@oregonstate.edu
# File: makefile
# Description: makefile for project 1.
# To execute the makefile, type "make", to delete the executables,
# type "make clean".
# To start the server: chatserver <port number>
# To start the client: chatclient <hostname> <port number> 
######################################################################
CXX = gcc
CXXFLAGS += -Wall
CXXFLAGS += -g

default:
	${CXX} ${CXXFLAGS} chatClient.c -o chatclient
	cp chatServer.py chatserve
	chmod u+x chatserve

clean:
	rm -f chatclient chatserve