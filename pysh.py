#!/usr/bin/python3
import os
import stat
import sys
import shlex
import subprocess
import signal

history = list()
amper = False
background_pid = 0
job_list = dict()
current_args = None

PROMPT = "psh> "
HOME = os.getcwd()
STAY_IN_SHELL_AFTER_SCRIPT = True
BUILTIN_COMMANDS = ["cd", "history", "h", "exit", "jobs", "fg", "bg", "kill"]


# Signal handlers
def ctrl_z_handle(signum, frame):
    os.kill(background_pid, signal.SIGTSTP)
    global current_args
    add_to_job_list(background_pid, current_args)

# This should probably kill a running process
def ctrl_c_handle(signum, frame):
    print()
    sys.exit(0)

signal.signal(signal.SIGTSTP, ctrl_z_handle)
signal.signal(signal.SIGINT, ctrl_c_handle)


def is_builtin(command):
    if command in BUILTIN_COMMANDS:
        return True
    else:
        return False

def add_to_job_list(job_pid, job_args):
    if len(job_list.keys()) == 0:
        job_number = 1
    else:
        job_number = max(job_list.keys()) + 1
    job_list[job_number] = (job_pid, job_args)
    print("[" + str(job_number) + "]\t" + str(job_pid))

def get_job_pid(job_no):
    if job_no in job_list.keys():
        return job_list[job_no][0]
    else:
        return None


def get_last_stopped_job_pid():
    last_stopped = None
    for job_no in job_list.keys():
        if get_state_of_pid(job_list[job_no][0]) == "Stopped":
            last_stopped = job_list[job_no][0]
    return last_stopped

def get_last_non_done_pid():
    last = None
    for job_no in job_list.keys():
        if get_state_of_pid(job_list[job_no][0]) != "Done":
            last = job_list[job_no][0]
    return last


def get_history_args(select):
    hist_len = len(history)
    if hist_len < 11:
        index = int(select) - 1
    else:
        index = int(select) - 10 + hist_len - 2
    return history[index]


def do_builtin(args):
    # cd
    if args[0] == "cd":
        try:
            # The correct behaviour of cd with no arguments is to cd to the users home directory (but since the
            # assignment has specified incorrect behaviour I suppose I can implement it)
            if len(args) < 2:
                os.chdir(HOME)
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
        execute_args(get_history_args(args[1]))

    # jobs
    if (args[0] == "jobs"):
        for job_no in job_list:
            job_pid = job_list[job_no][0]
            job_command = str.join(" ", job_list[job_no][1])
            print("[" + str(job_no) + "] <" + str(get_state_of_pid(job_pid)) + "> " + job_command + " &")


    # bg
    if (len(args) < 2 and args[0] == "bg"):
        os.kill(get_last_stopped_job_pid(), signal.SIGCONT)
    elif (len(args) >= 2 and args[0] == "bg"):
        job_pid = get_job_pid(int(args[1]))
        if job_pid != None:
            os.kill(job_pid, signal.SIGCONT)
        else:
            print("There is no job " + str(args[1]))

    # kill
    if (args[0] == "kill"):
        pass

    # exit
    if args[0] == "exit":
        exit()


def execute_args(args):
    # store command in history
    global history
    if not (args[0] in ["h", "history"] and len(args) > 1 and args[1].isdigit()):
        history.append(args)
    else:
        history.append(get_history_args(args[1]))

    pid = os.fork()
    global background_pid
    background_pid = pid
    if pid == 0:

        while "|" in args:  # Piping
            # Check the pipe syntax is correct
            if args[-1] == "|" or \
                            "||" in args or \
                            args[0] == "|":
                print("Invalid use of pipe \"|\".")
                sys.exit(1)

            pipe_index = args.index("|")
            first_command = args[0]
            first_args = args[0:pipe_index]

            args = args[pipe_index + 1:]

            # pipe = os.pipe()
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

def get_state_of_pid(pid):
    # From the man page
    # D    uninterruptible sleep (usually IO)
    # R    running or runnable (on run queue)
    # S    interruptible sleep (waiting for an event to complete)
    # T    stopped, either by a job control signal or because it is being traced
    # W    paging (not valid since the 2.6.xx kernel)
    # X    dead (should never be seen)
    # Z    defunct ("zombie") process, terminated but not reaped by its paren
    ps = subprocess.Popen(["ps", "-p", str(pid), "-o", "state="], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result, error = ps.communicate()
    result = result.decode("utf-8").strip()

    if result == "Z":
        result = "Zombie"
    elif result == "S":
        result = "Sleeping"
    elif result == "T":
        result = "Stopped"
    elif result == "":
        result = "Done"

    return result





# Removes old and defunct processes from the jobs list
def check_for_nonrunning_processes():
    global job_list
    jobs_to_remove = list()
    # Check if jobs are still active
    if len(job_list) > 0:
        jobs_to_remove = list()
        for job_no in job_list:
            job_pid = job_list[job_no][0]
            if get_state_of_pid(job_pid) == "Z":
                jobs_to_remove.append(job_no)
                os.waitpid(job_pid, 0) # Wait for the zombie

    # Remove the zombies
    #if len(jobs_to_remove) > 0:
    #    for item in jobs_to_remove:
    #        del job_list[item]


def main():
    # Setup curses
    # documentation https://docs.python.org/3.3/howto/curses.html
    # https://docs.python.org/3/library/curses.html
    # stdscr = curses.initscr()

    # Declare all my nice global variables
    global amper
    global background_pid
    global job_list

    while True:



        # Read in command
        try:
            command_line = input(PROMPT)
            if command_line == "":  # Check if just enter was pressed
                continue

            mode = os.fstat(0).st_mode
            if stat.S_ISFIFO(mode):  # stdin is piped
                print(command_line)
            elif stat.S_ISREG(mode):  # stdin is redirected
                print(command_line)

        except EOFError:  # If there is an EOFError then input was piped in and the shell should be terminated
            sys.stdin = open("/dev/tty")
            if not STAY_IN_SHELL_AFTER_SCRIPT:
                sys.exit(0)

        check_for_nonrunning_processes()

        # Turn command_line input into words in list
        args = get_args_from_string(command_line)

        # Update the args of the current command
        global current_args
        current_args = args

        # Set ampersand flag
        if "&" == args[-1]:
            amper = True
            args = args[:-1]
        else:
            amper = False

        # Flag for built in command
        builtin = False

        # Special cases in parent process
        # for command for exit command
        if args[0] == "exit":
            do_builtin(args)
            builtin = True

        # cd
        if args[0] == "cd":
            do_builtin(args)
            builtin = True

        # fg
        if (len(args) < 2 and args[0] == "fg"):
            job_pid = get_last_stopped_job_pid()
            #print(job_pid)
            os.kill(job_pid, signal.SIGCONT)
            amper = False  # a nice little hack
            #os.waitpid(job_pid, 0)
            builtin = True
        elif (len(args) >= 2 and args[0] == "fg"):
            job_pid = get_job_pid(int(args[1]))
            if job_pid is not None:
                #print(job_pid)
                os.kill(job_pid, signal.SIGCONT)
                amper = False  # a nice little hack
                #os.waitpid(job_pid, 0)
            else:
                print("There is no job " + args[1])
                amper = True
            builtin = True

        # kill
        if (len(args) >= 2 and args[0] == "kill"):
            try:
                os.kill(int(args[1]), signal.SIGKILL)
            except ProcessLookupError:
                print("Process number " + args[1] + " could not be found")
            builtin = True
        elif (len(args) < 2 and args[0] == "kill"):
            try:
                os.kill(get_last_non_done_pid(), signal.SIGKILL)
            except TypeError:
                print("No jobs to kill")
            builtin = True


        if not builtin:
            execute_args(args)

        # Parent continues here

        # Wait for the command if no ampersand and not built in
        if amper == False:
            try:
                os.wait()
            except ChildProcessError:
                pass
            except InterruptedError:
                pass
        else:
            if not builtin:
                # Add processes to jobs
                add_to_job_list(background_pid, args)




if __name__ == "__main__":
    #while True:
        #try:
    main()
        #except:
        #    pass
