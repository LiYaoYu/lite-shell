#!/usr/bin/env python3

import os
import sys
import tty
import termios
import re
import getpass
import socket
from subprocess import *

class Lite_shell:
    def __init__(self):
        self.__home_dir = os.environ["HOME"] 
        self.__conf_filename = self.__home_dir + "/" + ".y_shell.config"
        self.__log_filename = self.__home_dir + "/" + ".ysh_history"

        self.__stdin_fd = sys.stdin.fileno()
        self.__tty_attr = termios.tcgetattr(self.__stdin_fd)

        self.__prompt_info = self.__set_prompt_info()
        self.__delim = "\t|\r|\n|\a| " # used in re format

        self.__history = []

        self.__alias_cmd = {}

        self.__built_in_cmd = {
            "cd": self.__change_dir,
            "history": self.__show_history,
            "exit": self.__exit_litesh
        }

        self.__event_keys = {
            "\x1b[A": self.__get_prev_cmd_with_prefix,
            "\x1b[B": self.__get_next_cmd_with_prefix,
            "\t": self.__complete_cmd_with_prefix
        }

        self.__color_prefix = {
            "red": "\033[1;31m",
            "green": "\033[1;32m",
            "blue": "\033[1;34m",
            "cyan": "\033[1;36m",
            "white": "\033[1;37m",
            "reset": "\033[0m"
        }


    def load_config(self):
        try:
            f = open(self.__conf_filename, 'r')
            lines = f.readlines()
            f.close()
        except FileNotFoundError:
            return

        for line in lines:
            if line[0:6] == "alias ":
                # strip() due to the uncareful CR/LF in config file
                self.__set_alias(line[6:].strip())


    def load_history(self):
        try:
            f = open(self.__log_filename, 'r')
            lines = f.readlines()
            f.close()
            self.__history = lines

        except FileNotFoundError:
            f = open(self.__log_filename, 'x')
            f.close()
            return


    def init_terminal(self):
        tty.setraw(sys.stdin.fileno())


    def run_shell(self):
        ret = 0 # initial value
        while (True):
            self.__prompt = self.__get_prompt(ret)
            self.__show_prompt()
            line = self.__get_input()

            # handle empty input
            if line == "":
                ret = 0
                continue

            self.__update_history(line)
            cmd = self.__parse_input(line, False)
            ret = self.__exec_cmd(cmd)


    def __set_prompt_info(self):
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        return "debug ➜  " + self.username + "@" + self.hostname + " "


    def __set_alias(self, alias):
        res = alias.split('=')
        self.__alias_cmd[res[0]] = res[1]


    def __get_git_branch_name(self):
        try:
            out = check_output(["git", "branch"], stderr = STDOUT).decode("utf8")
        except CalledProcessError:
            return ""

        if out == "":
            return out

        cur = next(line for line in out.split("\n") if line.startswith("*"))
        return cur.strip("*").strip()


    def __get_prompt(self, status):
        # USER@HOSTNAME
        if status == 0:
            prompt_info =  self.__color_prefix["green"] + self.__prompt_info
        else:
            prompt_info =  self.__color_prefix["red"] + self.__prompt_info

        # CURRENT_DIRECTORY
        pwd = os.getcwd()
        if pwd == self.__home_dir:
            cwd = self.__color_prefix["cyan"] + "~"
        else:
            cwd = self. __color_prefix["cyan"] + os.path.split(pwd)[-1]

        # BRANCH_INFORMATION
        branch = self.__get_git_branch_name()
        if branch == "":
            git_info = ""
        else:
            git_info = "{0}git:({1}{2}{3}) ".format(self.__color_prefix["blue"],
                                                    self.__color_prefix["red"],
                                                    branch,
                                                    self.__color_prefix["blue"])

        return prompt_info + cwd + " " + git_info + self.__color_prefix["reset"]


    def __show_prompt(self):
            print(self.__prompt, end = "")
            sys.stdout.flush()


    def __get_prev_cmd_with_prefix(self, prefix):
        # TODO: return cmd
        print("prev")


    def __get_next_cmd_with_prefix(self, prefix):
        # TODO: return cmd
        print("next")


    def __complete_cmd_with_prefix(self, prefix):
        # TODO: return cmd
        print("comp")


    def __get_input(self):
        c = ""
        cmd = ""
        while c != '\n':
            try:
                c = sys.stdin.read(1)
            except EOFError: # TODO: this is useless currently
                self.__exit_litesh()
            finally:
                termios.tcsetattr(self.__stdin_fd, termios.TCSADRAIN, self.__tty_attr)

            if c == '\x1b': # handle event keys with prefix '\x1b'
                c += sys.stdin.read(2)
                cmd = self.__event_keys[c](cmd)
            elif c in self.__event_keys: # handle event keys with single char
                cmd = self.__event_keys[c](cmd)
            else:
                cmd += c

        return cmd.strip()


    def __update_history(self, line):
        self.__history.append(line + '\n')
        with open(self.__log_filename, 'a') as f:
            f.write(line + '\n')


    def __parse_input(self, line, is_recursive):
        line = line.strip(' ')
        cmd = re.split(self.__delim, line)

        if (not is_recursive) and (cmd[0] in self.__alias_cmd):
            cmd[0] = self.__alias_cmd[cmd[0]]
            return self.__parse_input(cmd[0], True) + cmd[1:]
        else:
            return cmd


    def __change_dir(self, cmd):
        if len(cmd) == 1:
            path = self.__home_dir
        else:
            path = cmd[1]

        os.chdir(path)


    def __show_history(self, cmd):
        for line in self.__history:
            print(line, end = "")


    def __exit_litesh(self, cmd):
        sys.exit()


    def __exec_cmd(self, cmd):
        if cmd[0] in self.__built_in_cmd:
            self.__built_in_cmd[cmd[0]](cmd)
            return 0 # 0 indicates the success cmd execution

        try:
            ret = run(cmd).returncode
        except FileNotFoundError: 
            print("lsh: command {0} not found".format(cmd[0]))
            ret = -1 # -1 indicates the fail cmd execution

        return ret



def main():
    sh = Lite_shell()

    sh.load_config()
    sh.load_history()
    sh.init_terminal()

    sh.run_shell()


if __name__ == "__main__":
    main()
