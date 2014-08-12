#!/usr/bin/python3
import curses
import os
from prompt import Prompt
import shlex

def main():
    # Setup curses
    # documentation https://docs.python.org/3.3/howto/curses.html
    # https://docs.python.org/3/library/curses.html
    #stdscr = curses.initscr()


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


              
            os.execvp(args[0], args)

        if amper == False:
            os.wait()


if __name__ == "__main__":
    main()
