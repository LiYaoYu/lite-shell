#!/usr/bin/env python3

import sys
import tty
import termios
import curses
import curses.ascii

from enum import IntEnum
from subprocess import run


class Keys(IntEnum):
    KEY_UP = curses.KEY_UP
    KEY_DOWN = curses.KEY_DOWN
    KEY_LEFT = curses.KEY_LEFT
    KEY_RIGHT = curses.KEY_RIGHT

    KEY_BACKSPACE = curses.KEY_BACKSPACE
    KEY_DELETE = curses.ascii.DEL
    KEY_ENTER = curses.ascii.NL
    KEY_TAB = curses.ascii.TAB

    KEY_CTRL_L = ord(curses.ascii.ctrl('L'))
    KEY_CTRL_D = ord(curses.ascii.ctrl('D'))



class InputHandler():
    def __init__(self, stdscr, tty_addr):
        globals().update(Keys.__members__)

        self.prefix = str()
        self.stdscr = stdscr
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
        self.prefix = "clear"
        return True


    def catch_EOF(self):
        self.prefix += "exit"
        return True


    def get_input(self, fd, history):
        c = None
        self.prefix = ""
        is_emergency_event = False
        while True:
            tty.setraw(fd)
            c = self.stdscr.getch()
            termios.tcsetattr(self.stdin_fd, termios.TCSANOW, self.tty_addr)

            if c in self.event_keys:
                is_emergency_event = self.event_keys[c]()
            else:
                self.prefix += chr(c)
                sys.stdout.write(chr(c))
                sys.stdout.flush()

            if c == KEY_ENTER or is_emergency_event == True:
                break

        return self.prefix.strip()


def test():
    input_handler = InputHandler(termios.tcgetattr(sys.stdin.fileno()))

    input_handler.get_prev_cmd_with_prefix("a", ["abc"])
    input_handler.get_next_cmd_with_prefix("a", ["abc"])
    input_handler.complete_cmd_with_prefix("a")
    input_handler.get_input(sys.stdin.fileno(), ["history"])


if __name__ == "__main__":
    test()
