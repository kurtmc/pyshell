#!/usr/bin/python3
import os
import subprocess

def main():
	while True:
		command = input("pysh> ");
		runCommand(command)
def runCommand(command):
	os.system(command)
	#subprocess.call(command)
	
		

if __name__ == "__main__":
	main()
