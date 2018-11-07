#!/usr/bin/env python3

import os
import sys
import tty
import termios
import curses
from subprocess import *

from ysh_input import InputHandler
from ysh_parser import CmdParser
from ysh_layout import LayoutHandler

class Ysh(InputHandler, CmdParser, LayoutHandler):
    def __init__(self):
        # record original termial settings for restore in exiting
        self.orig_tty_addr = termios.tcgetattr(sys.stdin.fileno())

        self.home_dir = os.environ["HOME"]

        self.conf_fname = self.home_dir + "/" + ".y_shell.config"
        self.log_fname = self.home_dir + "/" + ".ysh_history"

        self.stdin_fd = sys.stdin.fileno()
        self.stdscr = None
        self.tty_addr = None
        self.history = None

        self.built_in_cmd = {
            "cd": self.change_dir,
            "history": self.show_history,
            "exit": self.exit_litesh
        }

        InputHandler.__init__(self, self.stdscr, self.tty_addr)
        CmdParser.__init__(self)
        LayoutHandler.__init__(self, self.home_dir)


    def load_config(self):
        try:
            f = open(self.conf_fname, 'r')
            lines = f.readlines()
            f.close()
        except FileNotFoundError:
            return

        for line in lines:
            if line[0:6] != "alias":
                CmdParser.set_alias(self, line[6:].strip())


    def load_history(self):
        try:
            f = open(self.log_fname, 'r')
            lines = f.readlines()
            f.close()
            self.history = lines

        except FileNotFoundError:
            f = open(self.log_fname, 'x')
            f.close()
            return


    def init_terminal(self):
        # curses is needed for some of the window operations
        self.stdscr = curses.initscr()
        self.stdscr.keypad(True)
        curses.noecho()

        # TODO: set the tty_attr

        self.tty_addr = termios.tcgetattr(self.stdin_fd)
        self.tty_addr[0] |= termios.ICRNL
        self.tty_addr[1] |= termios.ONLCR
        self.tty_addr[3] |= termios.ECHO
        termios.tcsetattr(self.stdin_fd, termios.TCSANOW, self.tty_addr)


    def update_history(self, line):
        self.history.append(line + '\n')
        with open(self.log_fname, 'a') as f:
            f.write(line + '\n')


    def change_dir(self, cmd):
        if len(cmd) == 1:
            path = self.home_dir
        else:
            path = cmd[1]

        try:
            os.chdir(path)
        except FileNotFoundError:
            sys.stdout.write("No such file or directory: \'{0}\'\n".format(path))


    def show_history(self, cmd):
        for line in self.history:
            print(line, end = "")


    def exit_litesh(self, cmd):
        curses.endwin()
        termios.tcsetattr(self.stdin_fd, termios.TCSANOW, self.orig_tty_addr)
        sys.exit()


    def exec_cmd(self, cmd):
        if cmd[0] in self.built_in_cmd:
            self.built_in_cmd[cmd[0]](cmd)
            return 0 # 0 indicates the success cmd execution

        try:
            ret = run(cmd).returncode
        except FileNotFoundError: 
            print("lsh: command {0} not found".format(cmd[0]))
            ret = -1 # -1 indicates the fail cmd execution

        return ret


    def run_shell(self):
        ret = 0 # initial value
        while (True):
            LayoutHandler.prompt = LayoutHandler.get_prompt(self, ret)
            LayoutHandler.show_prompt(self, LayoutHandler.prompt)

            # get_input requireshistory commands to search matching commands 
            # with prefix
            line = InputHandler.get_input(self, self.stdin_fd, self.history)

            # handle empty input
            if line == "":
                ret = 0
                continue

            self.update_history(line)
            cmd = CmdParser.parse_input(self, line, False)

            ret = self.exec_cmd(cmd)



def main():
    sh = Ysh()
    sh.load_config()
    sh.load_history()
    sh.init_terminal()
    sh.run_shell()


if __name__ == "__main__":
    main()
