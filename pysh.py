#!/usr/bin/python3
import curses
import os
from prompt import Prompt
import shlex

history = list()

def is_builtin(command):
    if command in ["cd", "history", "exit"]:
        return True
    else:
        return False

def do_builtin(args):
    # cd
    if args[0] == "cd":
        os.chdir(args[1])

    # history
    if args[0] == "history" and len(args[1:]) == 0:
        hist_len = len(history)
        for_range = 10 if hist_len > 10 else hist_len
        for i in range(for_range):
            print(str(i+1) + ": " + str.join(" ", history[hist_len - for_range + i]))
    elif args[0] == "history" and len(args[1:]) != 0:
        hist_len = len(history)
        if hist_len < 11:
            index = int(args[1]) - 1
        else:
            index = int(args[1]) - 10 + hist_len - 2

        execute_args(history[index])

    # exit
    if args[0] == "exit":
        exit()

def execute_args(args):
    # store command in history
    global history
    history.append(args)


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
        if amper == False:
            try:
                os.wait()
            except ChildProcessError:
                pass


if __name__ == "__main__":
    main()
