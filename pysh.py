#!/usr/bin/python3
import curses
from prompt import Prompt

def main():
    # Setup curses
    # documentation https://docs.python.org/3.3/howto/curses.html
    # https://docs.python.org/3/library/curses.html
    stdscr = curses.initscr()


    while True:
        c = stdscr.getch()
        if c == ord('p'):
            print("yay print document")
        elif c == ord('q'):
            break  # Exit the while loop
        elif c == curses.KEY_HOME:
            x = y = 0

if __name__ == "__main__":
    main()
