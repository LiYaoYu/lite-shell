#!/usr/bin/env python3

import os
import sys
import getpass
import socket
from subprocess import *

class LayoutHandler:
    def __init__(self, home_dir):
        self.home_dir = home_dir
        self.prompt_info = self.set_prompt_info()

        self.color_prefix = {
            "red": "\033[1;31m",
            "green": "\033[1;32m",
            "blue": "\033[1;34m",
            "cyan": "\033[1;36m",
            "white": "\033[1;37m",
            "reset": "\033[0m"
        }


    def set_prompt_info(self):
        user = getpass.getuser()
        host = socket.gethostname()
        return "debug ➜  " + user + "@" + host + " " # TODO


    def get_git_branch_name(self):
        try:
            out = check_output(["git", "branch"], stderr = STDOUT).decode("utf8")
        except CalledProcessError:
            return ""

        if out == "":
            return out

        cur = next(line for line in out.split("\n") if line.startswith("*"))
        return cur.strip("*").strip()


    def get_prompt(self, status):
        # USER@HOSTNAME
        if status == 0:
            prompt_info = self.color_prefix["green"] + self.prompt_info
        else:
            prompt_info =  self.color_prefix["red"] + self.prompt_info

        # CURRENT_DIRECTORY
        pwd = os.getcwd()
        if pwd == self.home_dir:
            cwd = self.color_prefix["cyan"] + "~"
        else:
            cwd = self.color_prefix["cyan"] + os.path.split(pwd)[-1]

        # BRANCH_INFORMATION
        branch = self.get_git_branch_name()
        if branch == "":
            git_info = ""
        else:
            git_info = "{0}git:({1}{2}{3}) ".format(self.color_prefix["blue"],
                                                    self.color_prefix["red"],
                                                    branch,
                                                    self.color_prefix["blue"])

        return prompt_info + cwd + " " + git_info + self.color_prefix["reset"]


    def show_prompt(self, prompt):
            sys.stdout.write(prompt)
            sys.stdout.flush()


def test():
    import os

    layout_handler = LayoutHandler(os.environ["HOME"])

    layout_handler.set_prompt_info();
    layout_handler.get_git_branch_name();
    layout_handler.get_prompt(0)
    layout_handler.show_prompt("test_prompt")


if __name__ == "__main__":
    test()
