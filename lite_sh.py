#!/usr/bin/env python3

import os
import sys
import re
import getpass
import socket
from subprocess import *

class Lite_shell:
    def __init__(self):
        self.__home_dir = os.environ["HOME"] 
        self.__log_filename = self.__home_dir + "/" + ".lsh_history"
        
        self.__prompt_info = self.__set_prompt_info()
        self.__delim = "\t|\r|\n|\a| " # used in re format

        self.__history = []

        self.__built_in_cmd = {
            "cd": self.change_dir,
            "history": self.show_history,
            "exit": self.exit_litesh
        }


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


    def __set_prompt_info(self):
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        return "➜  " + self.username + "@" + self.hostname + " "
        

    def __get_git_branch_name(self):
        try:
            out = check_output(["git", "branch"], stderr = STDOUT).decode("utf8")
        except CalledProcessError:
            return ""

        if out == "":
            return out

        cur = next(line for line in out.split("\n") if line.startswith("*"))
        return cur.strip("*").strip()


    def __get_prompt(self):
        pwd = os.getcwd()
        
        if pwd == self.__home_dir:
            cwd = "~"
        else:
            cwd = os.path.split(pwd)[-1]

        branch = self.__get_git_branch_name()
        git_info = "git:({0}) ".format(branch) if branch != "" else ""
        return self.__prompt_info + cwd + " " + git_info


    def read_input(self):
        try:
            return input(self.__prompt)
        except EOFError:
            self.exit_litesh()


    def update_history(self, line):
        self.__history.append(line)
        with open(self.__log_filename, 'a') as f:
            f.write(line + '\n')


    def parse_input(self, line):
        line = line.strip(' ')
        cmd = re.split(self.__delim, line)
        return cmd


    def change_dir(self, cmd):
        if len(cmd) == 1:
            path = self.__home_dir
        else:
            path = cmd[1]

        os.chdir(path)


    def show_history(self, cmd):
        for line in self.__history:
            print(line, end = "")


    def exit_litesh(self, cmd):
        sys.exit()


    def exec_cmd(self, cmd):
        if cmd[0] in self.__built_in_cmd:
            self.__built_in_cmd[cmd[0]](cmd)
            return

        try:
            out = run(cmd)
        except FileNotFoundError: 
            print("lsh: command {0} not found".format(cmd[0]))


    def run_shell(self):
        while (True):
            self.__prompt = self.__get_prompt()
            line = self.read_input()

            self.update_history(line)
            cmd = self.parse_input(line)
            self.exec_cmd(cmd)



def main():
    sh = Lite_shell()

    sh.load_history()

    sh.run_shell()


if __name__ == "__main__":
    main()
