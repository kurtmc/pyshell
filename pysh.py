#!/usr/bin/python3
import curses
from os import execvp
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
        
        #if (/* command line contains & */)
        #   amper = 1;
        #else
        #   amper = 0;
        if "&" in commandLine:
            amper = True
        else:
            amper = False
        #/* for commands not part of the shell command language */
        #if (fork() == 0)
        #{
        pid = os.fork()
        if pid == 0:

        #   if (/* piping */)
        #   {
            if "|" in commandLine:
        #      pipe(fildes);
                (read, write) = os.pipe()
        #      if (fork() == 0)
        #      {
                if os.fork() == 0: # Child process
                    os.close(read)
                    write = os.fdopen(write, 'w')
        #         /* first component of command line */
        #         close(stdout);
        #         dup(fildes[1]);
        #         close(fildes[1]);
        #         close(fildes[0]);
        #         /* stdout now goes to pipe */
        #         /* child process does command */
        #         execlp(command1, command1, 0);
                    os.execlp(commandLine)
        #      }
                # Parent process
                os.close(write)
                read = os.fdopen(read)
        #      /* second component of command line */
        #      close(stdin);
        #      dup(fildes[0]);
        #      close(fildes[0]);
        #      close(fildes[1]);
        #      /* standard input now comes from the pipe */
        #   }
        #   execve(command2, command2, 0);
            execvp(args)
        #}
        #/* parent continues over here...
        #* waits for child to exit if required
        #*/
        #if (amper == 0)
        #   retid = wait(&status);
        os.wait()


if __name__ == "__main__":
    main()
