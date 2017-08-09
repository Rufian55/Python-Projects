#!/usr/bin/python3
###############################################################################
# python script: mypython.py        
# 1. When executed, creates 3 files in the same directory as mypython.py, each
#    named differently (the name of which is up to the developer), which remain
#    there after mypython.py finishes executing. Each of the 3 files contains 
#    exactly 10 random characters from the lowercase alphabet, with no spaces
#    ("hoehdgwkdq", for example). The final (eleventh) character of each file 
#    is the newline character.
# 2. When executed, mypython.py prints out on screen the contents of the 3
#    files it is creating.
# 3. When executed, after the file contents of all three files have been 
#    printed, prints out two random integers (whose range is from 1 to 42,
#    inclusive), and finaaly prints out the product of the two numbers.
###############################################################################
import sys
import random
import string

#############################################################
# function randomAlpha()
# param:    none.
# return:   random string of 10 lowercase alpha chars + '\n'
#############################################################
def randomAlpha():
    count = 0
    rString = ''
    while (count < 10):
        var = random.choice(string.ascii_lowercase)
        rString = rString + var
        count += 1
    rString = rString + '\n'
    return rString

# Our three random strings with newlines!
chrisString_1 = randomAlpha()
chrisString_2 = randomAlpha()
chrisString_3 = randomAlpha()

# A list our random strings for ease of use.
strList = [ chrisString_1, chrisString_2, chrisString_3 ]

# A list for colored fonts and backgrounds.
color = ['\x1b[6;30;42m', '\x1b[1;37;41m', '\x1b[1;37;44m', '\x1b[1;35;44m', '\x1b[0m']

# File 1
chrisFile = open('chrisFile_1', 'w')
chrisFile.write(strList[0])
chrisFile.close()

# Note print statements only take the first 10 chars, omitting the '\n' to suppress printing of blank colored line.
print("\nRandom String written to '%s' is: %s%s%s\n" % (chrisFile.name, color[0], strList[0][0:10], color[4]))
print("Now Opening for reading newly created '%s'.\n" % chrisFile.name)
try:
	chrisFile = open('chrisFile_1', 'r')
except IOError:
	print("Error opening/reading file '%s'." % chrisFile.name)
else:
	print("The content read back from '%s' is: %s%s%s\n" % (chrisFile.name, color[0], chrisFile.read()[0:10], color[4]))
	chrisFile.close()

# File 2
chrisFile = open('chrisFile_2', 'w')
chrisFile.write(strList[1])
chrisFile.close()

# Note print statements only take the first 10 chars, omitting the '\n' to suppress printing of blank colored line.
print("\nRandom String written to '%s' is: %s%s%s\n" % (chrisFile.name, color[1], strList[1][0:10], color[4]))
print("Now Opening for reading newly created '%s'.\n" % chrisFile.name)
try:
	chrisFile = open('chrisFile_2', 'r')
except IOError:
	print("Error opening/reading file '%s'." % chrisFile.name)
else:
	print("The content read back from '%s' is: %s%s%s\n" % (chrisFile.name, color[1], chrisFile.read()[0:10], color[4]))
	chrisFile.close()

# File 3
chrisFile = open('chrisFile_3', 'w')
chrisFile.write(strList[2])
chrisFile.close()

# Note print statements only take the first 10 chars, omitting the '\n' to suppress printing of blank colored line.
print("\nRandom String written to '%s' is: %s%s%s\n" % (chrisFile.name, color[2], strList[2][0:10], color[4]))
print("Now Opening for reading newly created '%s'.\n" % chrisFile.name)
try:
	chrisFile = open('chrisFile_3', 'r')
except IOError:
	print("Error opening/reading file '%s'." % chrisFile.name)
else:
	print("The content read back from '%s' is: %s%s%s\n" % (chrisFile.name, color[2], chrisFile.read()[0:10], color[4]))
	chrisFile.close()

print("%s...and since, technically, I did chop of the '\\n' chars to print %s\n\
%s   the random strings above in color without hideous colored blank lines,%s\n\
%s   here they are again with the \\n's intact and now properly%s\n\
%s   satisfying the specifications. <(^)%s\n" % (color[1], color[4], color[1], color[4], color[1], color[4], color[1], color[4]))

print(strList[0])
print(strList[1])
print(strList[2])

# Random Numbers.
print("\n%sRandom integers from the set \"1 to 42\" inclusive!%s\n" % (color[3], color[4]))
random.seed()
x = random.randrange(1,42,1)
y = random.randrange(1,42,1)
print("First random integer is: %d\n" % x)
print("Second random integer is: %d\n" % y)
print("The product of these two integers is: %d\n" % (x*y))

