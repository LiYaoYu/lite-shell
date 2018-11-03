#!/usr/bin/env python3

import re

class CmdParser:
    def __init__(self):
        self.delim = "\t|\r|\n|\a| " # used in re format

        self.alias_cmd = {}


    def set_alias(self, alias):
        res = alias.split('=')
        self.alias_cmd[res[0]] = res[1]


    def parse_input(self, line, is_recursive):
        # TODO: consider "", '', (), [], {}
        line = line.strip(' ')
        cmd = re.split(self.delim, line)

        if (not is_recursive) and (cmd[0] in self.alias_cmd):
            cmd[0] = self.alias_cmd[cmd[0]]
            return self.parse_input(cmd[0], True) + cmd[1:]
        else:
            return cmd


def test():
    cmd_parser = CmdParser()

    cmd_parser.set_alias("t=test")
    cmd_parser.parse_input("ls -al", True) == ["ls", "-al"]


if __name__ == "__main__":
    test()
