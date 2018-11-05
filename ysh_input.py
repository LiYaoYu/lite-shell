#!/usr/bin/env python3

import sys
import termios

from enum import Enum
from subprocess import run

class StrEnum(str, Enum):
    pass

class Keys(StrEnum):
    KEY_UP = "\x1b[A"
    KEY_DOWN = "\x1b[B"
    KEY_RIGHT = "\x1b[C"
    KEY_LEFT = "\x1b[D"

    KEY_DELETE = "\x1b[3"
    KEY_BACKSPACE = "\x7f"

    KEY_TAB = "\t"
    KEY_CTRL_L = "\x0c" # <Ctrl> L
    KEY_CTRL_D = "\x04" # <Ctrl> D



class InputHandler():
    def __init__(self, tty_addr):
        globals().update(Keys.__members__)

        self.prefix = ""
        self.tty_addr = tty_addr

        self.event_keys = {
            KEY_UP: self.get_prev_cmd_with_prefix,
            KEY_DOWN: self.get_next_cmd_with_prefix,
            KEY_RIGHT: self.mv_cur_right,
            KEY_LEFT: self.mv_cur_left,

            KEY_DELETE: self.erase_next_char,
            KEY_BACKSPACE: self.erase_prev_char,

            KEY_TAB: self.complete_cmd_with_prefix,
            KEY_CTRL_L: self.clear_screen,
            KEY_CTRL_D: self.catch_EOF,
        }


    def get_prev_cmd_with_prefix(self):
        # TODO: return cmd
        print("prev", end = "")
        sys.stdout.flush()
        return ""


    def get_next_cmd_with_prefix(self):
        # TODO: return cmd
        print("next")
        sys.stdout.flush()
        return ""

    def mv_cur_right(self):
        # TODO
        print("mv_cur_right")
        return""


    def mv_cur_left(self):
        # TODO
        print("mv_cur_left")
        return""


    def erase_prev_char(self):
        # TODO
        print("erase_prev_char")
        return ""


    def erase_next_char(self):
        # TODO
        print("erase_next_char")
        return ""


    def complete_cmd_with_prefix(self):
        # TODO: return cmd
        print("comp")
        sys.stdout.flush()
        return ""


    def clear_screen(self):
        run("clear")
        return ""


    def catch_EOF(self):
        sys.exit()


    def get_char(self):
        c = sys.stdin.read(1)
        for k in self.event_keys:
            if c in k and c not in self.event_keys:
                c += sys.stdin.read(1)
                continue
        return c


    def get_input(self, fd, history):
        c = ""
        cmd = ""
        while c != '\n':
            c = self.get_char()
            termios.tcsetattr(self.stdin_fd, termios.TCSANOW, self.tty_addr)

            if c in self.event_keys: # handle event keys with single char
                cmd = self.event_keys[c]()
            else:
                cmd += c

        return cmd.strip()


def test():
    input_handler = InputHandler(termios.tcgetattr(sys.stdin.fileno()))

    input_handler.get_prev_cmd_with_prefix("a", ["abc"])
    input_handler.get_next_cmd_with_prefix("a", ["abc"])
    input_handler.complete_cmd_with_prefix("a")
    input_handler.get_input(sys.stdin.fileno(), ["history"])


if __name__ == "__main__":
    test()
