################################################################################
# cs372-400-S17	Introduction to Networks	04 Jun 2017	Project 2
# Chris Kearns		kearnsc@oregonstate.edu
# File: makefile
# Description: makefile for project 2 server side.
# To execute the makefile, type "make", to delete the executable 
# type "make clean".
# To start the server: ftserver <Port>, to stop the server, Ctrl-c 
###############################################################################
CXX = gcc
CXXFLAGS += -Wall
CXXFLAGS += -g

default:
	${CXX} ${CXXFLAGS} ftserver.c ftserver.h main.c -o ftserver

clean:
	rm -f ftserver