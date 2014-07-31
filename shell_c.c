/* read command line until "end of file" */
while (read(stdin, buffer, numchars))
{
	/* parse command line */
	if (/* command line contains & */)
		amper = 1;
	else
		amper = 0;
	/* for commands not part of the shell command language */
	if (fork() == 0)
	{
		if (/* piping */)
		{
			pipe(fildes);
			if (fork() == 0)
			{
				/* first component of command line */
				close(stdout);
				dup(fildes[1]);
				close(fildes[1]);
				close(fildes[0]);
				/* stdout now goes to pipe */
				/* child process does command */
				execlp(command1, command1, 0);
			}
			/* second component of command line */
			close(stdin);
			dup(fildes[0]);
			close(fildes[0]);
			close(fildes[1]);
			/* standard input now comes from the pipe */
		}
		execve(command2, command2, 0); // Python: os.execvp
	}
	/* parent continues over here...
	 * waits for child to exit if required
	 */
	if (amper == 0)
		retid = wait(&status);
}
