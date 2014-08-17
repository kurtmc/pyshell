#!/usr/bin/python3
import os
import stat
import sys
import shlex

history = list()

PROMPT = "psh> "


def is_builtin(command):
    if command in ["cd", "history", "h", "exit"]:
        return True
    else:
        return False


def do_builtin(args):
    # cd
    if args[0] == "cd":
        try:
            # The correct behaviour of cd with no arguments is to cd to the users home directory (test2 is wrong)
            if len(args) < 2:
                os.chdir(os.path.expanduser("~"))
            else:
                os.chdir(args[1])
        except FileNotFoundError:
            print("cd: " + args[1] + ": No such file or directory")

    # history
    if (args[0] == "history" or args[0] == "h") and len(args[1:]) == 0:
        hist_len = len(history)
        for_range = 10 if hist_len > 10 else hist_len
        for i in range(for_range):
            print(str(i + 1) + ": " + str.join(" ", history[hist_len - for_range + i]))
    elif (args[0] == "history" or args[0] == "h") and len(args[1:]) != 0:
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

    pid = os.fork()
    if pid == 0:
        while "|" in args:  # Piping

            pipe_index = args.index("|")
            first_command = args[0]
            first_args = args[0:pipe_index]

            args = args[pipe_index + 1:]

            #pipe = os.pipe()
            (read, write) = os.pipe()

            if os.fork() == 0:  # Child process
                # First component of command line
                os.dup2(write, sys.stdout.fileno())
                # stdout now goes to pipe
                # child process does command
                os.execvp(first_command, first_args)

            # Second component of command line
            os.dup2(read, sys.stdin.fileno())
            # standard input now comes from the pipe



        # If it is a built in command it can be done in the parent?
        if is_builtin(args[0]):
            do_builtin(args)
            sys.exit(0)  # Kill the child process
        # Check if command ins build in and execute, else use os.execvp
        if not is_builtin(args[0]):
            os.execvp(args[0], args)


def get_args_from_string(input_args):
    lexer = shlex.shlex(input_args, posix=True)
    lexer.whitespace_split = False
    lexer.wordchars += '#$+-,./?@^='
    args = list(lexer)
    return args


def main():
    # Setup curses
    # documentation https://docs.python.org/3.3/howto/curses.html
    # https://docs.python.org/3/library/curses.html
    # stdscr = curses.initscr()

    while True:

        # Read in command
        try:
            command_line = input(PROMPT)

            mode = os.fstat(0).st_mode
            if stat.S_ISFIFO(mode):  # stdin is piped
                print(command_line)
            elif stat.S_ISREG(mode):  # stdin is redirected
                print(command_line)

        except EOFError:  # If there is an EOFError then input was piped in and the shell should be terminated
            sys.exit(0)

        # Turn command_line input into words in list
        args = get_args_from_string(command_line)

        # Set ampersand flag
        if "&" == args[-1]:
            amper = True
            args = args[:-1]
            print(args)
        else:
            amper = False

        # Flag for built in command
        builtin = False

        # Special cases:
        # for command for exit command
        if args[0] == "exit":
            do_builtin(args)
            builtin = True

        if args[0] == "cd":
            do_builtin(args)
            builtin = True

        if not builtin:
            execute_args(args)

        #Parent continues here

        # Wait for the command if no ampersand and not built in
        if amper == False:
            try:
                os.wait()
            except ChildProcessError:
                pass


if __name__ == "__main__":
    main()
