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
        self.__conf_filename = self.__home_dir + "/" + ".lite_shell.config"
        self.__log_filename = self.__home_dir + "/" + ".lsh_history"
        
        self.__prompt_info = self.__set_prompt_info()
        self.__delim = "\t|\r|\n|\a| " # used in re format

        self.__history = []

        self.__alias_cmd = {}

        self.__built_in_cmd = {
            "cd": self.change_dir,
            "history": self.show_history,
            "exit": self.exit_litesh
        }


    def __set_alias(self, alias):
        res = alias.split('=')
        self.__alias_cmd[res[0]] = res[1]


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


    def __get_prompt(self, status):
        # USER@HOSTNAME
        if status == 0:
            prompt_info =  "\033[1;32m" + self.__prompt_info
        else:
            prompt_info =  "\033[1;31m" + self.__prompt_info

        # CURRENT_DIRECTORY
        pwd = os.getcwd()
        if pwd == self.__home_dir:
            cwd = "\033[1;34m" + "~"
        else:
            cwd = "\033[1;34m" + os.path.split(pwd)[-1]

        # BRANCH_INFORMATION
        branch = self.__get_git_branch_name()
        if branch == "":
            git_info = ""
        else:
            git_info = "\033[1;37m" + "git:({0}) ".format(branch)

        reset_color = "\033[0m"

        return prompt_info + cwd + " " + git_info + reset_color


    def __read_input(self):
        try:
            return input(self.__prompt)
        except EOFError:
            self.exit_litesh()


    def __update_history(self, line):
        self.__history.append(line + '\n')
        with open(self.__log_filename, 'a') as f:
            f.write(line + '\n')


    def __parse_input(self, line, is_recursive):
        line = line.strip(' ')
        cmd = re.split(self.__delim, line)

        if (not is_recursive) and (cmd[0] in self.__alias_cmd):
            cmd[0] = self.__alias_cmd[cmd[0]]
            return self.__parse_input(cmd[0], True)
        else:
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
            self.__prompt = self.__get_prompt(ret)
            line = self.__read_input()

            self.__update_history(line)
            cmd = self.__parse_input(line, False)
            ret = self.exec_cmd(cmd)



def main():
    sh = Lite_shell()

    sh.load_history()
    sh.load_config()

    sh.run_shell()


if __name__ == "__main__":
    main()
