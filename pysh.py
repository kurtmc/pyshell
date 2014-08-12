#!/usr/bin/python3
import curses
import os
from prompt import Prompt
import shlex

def is_builtin(command):
    if command in ["cd"]:
        return True
    else:
        return False

def do_builtin(args):
    if args[0] == "cd":
        os.chdir(args[1])


def main():
    # Setup curses
    # documentation https://docs.python.org/3.3/howto/curses.html
    # https://docs.python.org/3/library/curses.html
    #stdscr = curses.initscr()

    currentDirectory = os.getcwd()
    print(currentDirectory)


    while True:
        #/* read command line until “end of file” */
        #/* parse command line */
        commandLine = input("$ ")
        """Break the line into shell words.
        """
        lexer = shlex.shlex(commandLine, posix=True)
        lexer.whitespace_split = False
        lexer.wordchars += '#$+-,./?@^='
        args = list(lexer)
        

        if "&" in commandLine:
            amper = True
        else:
            amper = False

        if is_builtin(args[0]):
            do_builtin(args)
        else:


            pid = os.fork()
            if pid == 0:
                if "|" in commandLine:

                    (read, write) = os.pipe()

                    if os.fork() == 0: # Child process
                        os.close(read)
                        write = os.fdopen(write, 'w')

                        os.execlp(commandLine)

                    os.close(write)
                    read = os.fdopen(read)


                # Check if command ins build in and execute, else use os.execvp
                if not is_builtin(args[0]):
                    os.execvp(args[0], args)



        if amper == False and not is_builtin(args[0]):
            os.wait()


if __name__ == "__main__":
    main()
