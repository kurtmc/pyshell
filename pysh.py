#!/usr/bin/python3
import curses
import os
from prompt import Prompt
import shlex

def is_builtin(command):
    if command in ["cd", "history"]:
        return True
    else:
        return False

def do_builtin(args):
    if args[0] == "cd":
        os.chdir(args[1])
    if args[0] == "history" and len(args[1:]) == 0:
        print("yay history")
    elif args[0] == "history" and len(args[1:]) != 0:
        print("history " + str(args))

def execute_args(args):
    # If it is a built in command it can be done in the parent?
    if is_builtin(args[0]):
        do_builtin(args)
    else:  # Else do things in the child process
        pid = os.fork()
        if pid == 0:
            if "|" in args:

                (read, write) = os.pipe()

                if os.fork() == 0: # Child process
                    os.close(read)
                    write = os.fdopen(write, 'w')

                    os.execlp(args)

                os.close(write)
                read = os.fdopen(read)


            # Check if command ins build in and execute, else use os.execvp
            if not is_builtin(args[0]):
                os.execvp(args[0], args)


def main():
    # Setup curses
    # documentation https://docs.python.org/3.3/howto/curses.html
    # https://docs.python.org/3/library/curses.html
    #stdscr = curses.initscr()

    history = list()

    while True:

        # Read in command
        commandLine = input("$ ")

        # Turn commandLine input into words in list
        lexer = shlex.shlex(commandLine, posix=True)
        lexer.whitespace_split = False
        lexer.wordchars += '#$+-,./?@^='
        args = list(lexer)

        # Set ampersand flag
        if "&" == args[-1]:
            amper = True
            args = args[:-1]
            print(args)
        else:
            amper = False


        execute_args(args)




        # Wait for the command if no ampersand and not built in
        if amper == False and not is_builtin(args[0]):
            os.wait()

if __name__ == "__main__":
    main()
