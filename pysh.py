#!/usr/bin/python3
import os
import subprocess
import socket

def stripByteArray(byteArray):
	return str(byteArray[:len(byteArray)-1].decode("utf-8"))

def getPrompt():
	proc = subprocess.Popen(["whoami"], stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()
	# Get user information so that it can be displayed on command line input
	username = stripByteArray(out)
	proc = subprocess.Popen(["uname", "-n"], stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()
	host = socket.gethostname()#stripByteArray(out)	
	proc = subprocess.Popen(["pwd"], stdout=subprocess.PIPE, shell=True)
	(out, err) = proc.communicate()
	pwd = stripByteArray(out)
	return username + "@" + host + ":" + pwd + "> "

def main():
	while True:
		command = input(getPrompt());
		runCommand(command)
def runCommand(command):
	os.system(command)
	#subprocess.call(command)
	
		

if __name__ == "__main__":
	main()
