"""
Nuqql UI Windows
"""

import curses
import math

from types import SimpleNamespace

# screen and main windows
MAIN_WINS = {}


class Win:
    """
    Base class for Windows
    """

    def __init__(self, config, conversation, title):
        # configuration
        self.config = config

        # conversation
        self.conversation = conversation

        # window title
        self.title = " " + title + " "

        # create new window and new pad
        size_y, size_x = self.config.get_size()
        pos_y, pos_x = self.config.get_pos()
        self.win = curses.newwin(size_y, size_x, pos_y, pos_x)
        self.pad = curses.newpad(size_y - 2, size_x - 2)

        # window state
        self.state = SimpleNamespace(
            # is window active?
            active=False,
            # position inside pad
            pad_y=0,
            pad_x=0,
            # cursor positions
            cur_y=0,
            cur_x=0
        )

        # keymaps/bindings
        self.keyfunc = {}
        self._init_keyfunc()

    def _redraw_win(self):
        """
        Redraw entire window
        """

        # if terminal size is invalid, stop here
        if not self.config.is_terminal_valid():
            return

        # screen/window properties
        win_size_y, win_size_x = self.win.getmaxyx()
        self.win.clear()

        # color settings on
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
        self.win.attron(curses.color_pair(1) | curses.A_BOLD)

        # window border
        max_y, max_x = MAIN_WINS["screen"].getmaxyx()
        if not win_size_y == max_y or not win_size_x == max_x:
            self.win.border()

        # window title
        max_title_len = min(len(self.title), win_size_x - 3)
        title = self.title[:max_title_len]
        if title != "":
            title = title[:-1] + " "
        self.win.addstr(0, 2, title)

        # color settings off
        self.win.attroff(curses.color_pair(1) | curses.A_BOLD)

        self.win.refresh()

    def _move_pad(self):
        """
        Move the pad
        """

        # get window size
        win_size_y, win_size_x = self.win.getmaxyx()

        # get current cursor positions
        self.state.cur_y, self.state.cur_x = self.pad.getyx()

        # move pad right, if cursor leaves window area on the right
        if self.state.cur_x > self.state.pad_x + (win_size_x - 3):
            self.state.pad_x = self.state.cur_x - (win_size_x - 3)

        # move pad left, if cursor leaves current pad position on the left
        if self.state.cur_x < self.state.pad_x:
            self.state.pad_x = self.state.cur_x

        # move pad down, if cursor leaves window area at the bottom
        if self.state.cur_y > self.state.pad_y + (win_size_y - 3):
            self.state.pad_y = self.state.cur_y - (win_size_y - 3)

        # move pad up, if cursor leaves current pad position at the top
        if self.state.cur_y < self.state.pad_y:
            self.state.pad_y = self.state.cur_y

    def _check_borders(self):
        """
        Check borders
        """

        # get sizes
        win_size_y, win_size_x = self.win.getmaxyx()
        pad_size_y, pad_size_x = self.pad.getmaxyx()

        # do not move visible area too far to the left
        if self.state.pad_x < 0:
            self.state.pad_x = 0

        # do not move visible area too far to the right
        if self.state.pad_x + (win_size_x - 3) > pad_size_x:
            self.state.pad_x = pad_size_x - (win_size_x - 3)

        # do not move visible area too far up
        if self.state.pad_y < 0:
            self.state.pad_y = 0

        # do not move visible area too far down
        if self.state.pad_y + (win_size_y - 3) > pad_size_y:
            self.state.pad_y = pad_size_y - (win_size_y - 3)

    def redraw_pad(self):
        """
        Redraw pad in window
        """

        # implemented in other classes

    def redraw(self):
        """
        Redraw the window
        """

        self._redraw_win()
        self.redraw_pad()

    def resize_win(self, win_y_max, win_x_max):
        """
        Resize window
        """

        # if terminal size is invalid, stop here
        if not self.config.is_terminal_valid():
            return

        # TODO: change function parameters?
        self.win.resize(win_y_max, win_x_max)

    def move_win(self, pos_y, pos_x):
        """
        Move window
        """

        # if terminal size is invalid, stop here
        if not self.config.is_terminal_valid():
            return

        self.win.mvwin(pos_y, pos_x)

    def _go_back(self, *args):
        """
        User input: go back
        """

        # implemented in sub classes

    def _cursor_right(self, *args):
        """
        User input: cursor right
        """

        # implemented in sub classes

    def _cursor_left(self, *args):
        """
        User input: cursor left
        """

        # implemented in sub classes

    def _cursor_down(self, *args):
        """
        User input: cursor down
        """

        # implemented in sub classes

    def _cursor_up(self, *args):
        """
        User input: cursor up
        """

        # implemented in sub classes

    def _send_msg(self, *args):
        """
        User input: send message
        """

        # implemented in sub classes

    def _delete_char(self, *args):
        """
        User input: delete character
        """

        # implemented in sub classes

    def _cursor_msg_start(self, *args):
        """
        User input: move cursor to message start
        """

        # implemented in sub classes

    def _cursor_msg_end(self, *args):
        """
        User input: move cursor to message end
        """

        # implemented in sub classes

    def _cursor_line_start(self, *args):
        """
        User input: move cursor to line start
        """

        # implemented in sub classes

    def _cursor_line_end(self, *args):
        """
        User input: move cursor to line end
        """

        # implemented in sub classes

    def _delete_line_end(self, *args):
        """
        User input: delete from cursor to end of current line
        """

        # implemented in sub classes

    def _delete_line(self, *args):
        """
        User input: delete current line
        """

        # implemented in sub classes

    def _zoom_win(self, *args):
        """
        User input: zoom current window
        """

        # implemented in sub classes

    def _init_keyfunc(self):
        """
        Initialize key to function mapping
        """

        self.keyfunc = {
            "GO_BACK": self._go_back,
            "CURSOR_RIGHT": self._cursor_right,
            "CURSOR_LEFT": self._cursor_left,
            "CURSOR_DOWN": self._cursor_down,
            "CURSOR_UP": self._cursor_up,
            "SEND_MSG": self._send_msg,
            "DEL_CHAR": self._delete_char,
            "CURSOR_MSG_START": self._cursor_msg_start,
            "CURSOR_MSG_END": self._cursor_msg_end,
            "CURSOR_LINE_START": self._cursor_line_start,
            "CURSOR_LINE_END": self._cursor_line_end,
            "DEL_LINE_END": self._delete_line_end,
            "DEL_LINE": self._delete_line,
            "WIN_ZOOM": self._zoom_win,
        }


class ListWin(Win):
    """
    Class for List Windows
    """

    def __init__(self, config, conversation, title):
        Win.__init__(self, config, conversation, title)

        # list entries/message log
        self.list = []

    def add(self, entry):
        """
        Add entry to internal list
        """

        # add entry to own list
        self.list.append(entry)

        # if terminal size is invalid, stop here
        if not self.config.is_terminal_valid():
            return

        # if this window belongs to an active conversation, redraw it
        if self.conversation.is_active():
            self.redraw()
        elif self is MAIN_WINS["log"]:
            # if this is the main log, display it anyway if there is nothing
            # else active
            if self.conversation.is_any_active():
                return
            self.redraw()

    def redraw_pad(self):
        """
        Redraw pad in window
        """

        # if terminal size is invalid, stop here
        if not self.config.is_terminal_valid():
            return

        # screen/pad properties
        pos_y, pos_x = self.config.get_pos()
        win_size_y, win_size_x = self.win.getmaxyx()
        pad_size_y, pad_size_x = self.pad.getmaxyx()
        self.state.cur_y, self.state.cur_x = self.pad.getyx()
        self.pad.clear()

        # make sure pad has correct width (after resize)
        if pad_size_x != win_size_x - 2:
            self.pad.resize(pad_size_y, win_size_x - 2)
            pad_size_x = win_size_x - 2

        # set colors
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.pad.attron(curses.color_pair(2))

        # store last selected entry
        last_selected = self.list[self.state.cur_y]

        # sort list
        self.list.sort()

        # make sure all names fit into pad
        if len(self.list) > pad_size_y - 1:
            self.pad.resize(len(self.list) + 1, pad_size_x)

        # if there is an active conversation or last selected conversation was
        # moved, move cursor to it
        for index, conv in enumerate(self.list):
            if conv.is_active() or conv is last_selected:
                self.state.cur_y = index

        # print names in list window
        for index, conv in enumerate(self.list):
            # get name of element; cut if it's too long
            name = conv.get_name()
            name = name[:pad_size_x-1] + "\n"

            # print name
            if index == self.state.cur_y:
                # cursor is on conversation, highlight it in list
                self.pad.addstr(name, curses.A_REVERSE)
            else:
                # just show the conversation in list
                self.pad.addstr(name)

        # reset colors
        self.pad.attroff(curses.color_pair(2))

        # move cursor back to original or active conversation's position
        self.pad.move(self.state.cur_y, self.state.cur_x)

        # check if visible part of pad needs to be moved and display it
        self._move_pad()
        self._check_borders()
        self.pad.refresh(self.state.pad_y, self.state.pad_x,
                         pos_y + 1, pos_x + 1,
                         pos_y + win_size_y - 2,
                         pos_x + win_size_x - 2)

    def _cursor_msg_start(self, *args):
        # TODO: use other method and keybind with more fitting name?
        # jump to first conversation
        if self.state.cur_y > 0:
            self.pad.move(0, 0)

    def _cursor_msg_end(self, *args):
        # TODO: use other method and keybind with more fitting name?
        # jump to last conversation
        lines = len(self.list)
        if self.state.cur_y < lines - 1:
            self.pad.move(lines - 1, self.state.cur_x)

    def _cursor_line_start(self, *args):
        # TODO: use other method and keybind with more fitting name?
        # move cursor up one page until first entry in log
        win_size_y, unused_win_size_x = self.win.getmaxyx()

        if self.state.cur_y > 0:
            if self.state.cur_y - (win_size_y - 2) >= 0:
                self.pad.move(self.state.cur_y - (win_size_y - 2),
                              self.state.cur_x)
            else:
                self.pad.move(0, self.state.cur_x)

    def _cursor_line_end(self, *args):
        # TODO: use other method and keybind with more fitting name?
        # move cursor down one page until last entry in log
        win_size_y, unused_win_size_x = self.win.getmaxyx()

        lines = len(self.list)
        if self.state.cur_y < lines:
            if self.state.cur_y + win_size_y - 2 < lines:
                self.pad.move(self.state.cur_y + win_size_y - 2,
                              self.state.cur_x)
            else:
                self.pad.move(lines - 1, self.state.cur_x)

    def _cursor_up(self, *args):
        # move cursor up until first entry in list
        if self.state.cur_y > 0:
            self.pad.move(self.state.cur_y - 1, self.state.cur_x)

    def _cursor_down(self, *args):
        # move cursor down until end of list
        if self.state.cur_y < len(self.list) - 1:
            self.pad.move(self.state.cur_y + 1, self.state.cur_x)

    def process_input(self, char):
        """
        Process input from user (character)
        """

        self.state.cur_y, self.state.cur_x = self.pad.getyx()

        # look for special key mappings in keymap or process as text
        if char in self.config.keymap:
            func = self.keyfunc[self.config.keybinds[self.config.keymap[char]]]
            func()
        elif char == "q":
            self.state.active = False
            return  # Exit the while loop
        elif char == "\n":
            # create windows, if they do not exists
            if not self.list[self.state.cur_y].has_windows():
                self.list[self.state.cur_y].create_windows()
            # activate conversation
            self.list[self.state.cur_y].activate()
        elif char == "h":
            # create windows, if they do not exists
            if not self.list[self.state.cur_y].has_windows():
                self.list[self.state.cur_y].create_windows()
            # activate conversation's history
            self.list[self.state.cur_y].activate_log()
        # display changes in the pad
        self.redraw_pad()


class LogWin(Win):
    """
    Class for Log Windows
    """

    def __init__(self, config, conversation, title):
        Win.__init__(self, config, conversation, title)

        # window in zoomed/fullscreen mode
        self.zoomed = False

        # list entries/message log
        self.list = []

    def add(self, entry):
        """
        Add entry to internal list
        """

        # add entry to own list
        self.list.append(entry)

        # if terminal size is invalid, stop here
        if not self.config.is_terminal_valid():
            return

        # if this window belongs to an active conversation, redraw it
        if self.conversation.is_active():
            self.redraw()
        elif self is MAIN_WINS["log"]:
            # if this is the main log, display it anyway if there is nothing
            # else active
            if self.conversation.is_any_active():
                return
            self.redraw()

    def _get_num_log_lines(self, pad_size_x):
        """
        Get number of lines in log, depending on number of messages and how
        many lines each message uses.
        """

        lines = 0
        for msg in self.list:
            parts = msg.read(mark_read=False).split("\n")
            lines += len(parts) - 1
            for part in parts:
                if len(part) >= pad_size_x:
                    lines += math.floor(len(part) / pad_size_x)
        return lines

    def _print_log(self, props):
        """
        dump log messages and resize pad according to new lines added
        """

        # make sure lines fit into pad
        lines = self._get_num_log_lines(props.pad_size_x)
        if lines >= props.pad_size_y:
            self.pad.resize(lines + 1, props.pad_size_x)

        for msg in self.list:
            # define colors for own and buddy's messages
            # TODO: move all color definitions to config part?
            curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
            curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)

            # set colors and attributes for message:
            # * unread messages are bold
            # * read messages are normal
            if not msg.own:
                # message from buddy
                if msg.is_read:
                    # old message
                    self.pad.attroff(curses.A_BOLD)
                    self.pad.attron(curses.color_pair(3) | curses.A_NORMAL)
                else:
                    # new message
                    self.pad.attroff(curses.A_NORMAL)
                    self.pad.attron(curses.color_pair(3) | curses.A_BOLD)
            else:
                # message from you
                if msg.is_read:
                    # old message
                    self.pad.attroff(curses.A_BOLD)
                    self.pad.attron(curses.color_pair(4) | curses.A_NORMAL)
                else:
                    # new message
                    self.pad.attroff(curses.A_NORMAL)
                    self.pad.attron(curses.color_pair(4) | curses.A_BOLD)

            # output message
            self.pad.addstr(msg.read())

    def _get_properties(self):
        """
        Get window/pad properties, depending on max size and zoom
        """

        props = SimpleNamespace()
        props.max_y, props.max_x = MAIN_WINS["screen"].getmaxyx()
        if self.zoomed:
            # window is currently zoomed
            props.pos_y, props.pos_x = 0, 0
            props.pos_y_off, props.pos_x_off = 1, 0
            props.win_size_y, props.win_size_x = props.max_y, props.max_x
            props.pad_size_y, props.pad_size_x = (props.max_y - 2, props.max_x)
            props.pad_y_delta, props.pad_x_delta = 2, 0
        else:
            # window is not zoomed
            props.pos_y, props.pos_x = self.config.get_pos()
            props.pos_y_off, props.pos_x_off = 1, 1
            props.win_size_y, props.win_size_x = self.config.get_size()
            # use actual pad size, it will be resized later if necessary
            props.pad_size_y, props.pad_size_x = self.pad.getmaxyx()
            props.pad_y_delta, props.pad_x_delta = 2, 2

        return props

    def _pad_refresh(self, props):
        """
        Helper for running move_pad(), check_borders(), and pad.refresh()
        """
        self._move_pad()
        self._check_borders()
        self.pad.refresh(self.state.pad_y, self.state.pad_x,
                         props.pos_y + props.pos_y_off,
                         props.pos_x + props.pos_x_off,
                         props.pos_y + props.win_size_y - props.pad_y_delta,
                         props.pos_x + props.win_size_x - props.pad_x_delta)

    def redraw_pad(self):
        # if terminal size is invalid, stop here
        if not self.config.is_terminal_valid():
            return

        # screen/pad properties
        props = self._get_properties()

        # if window was resized, resize pad size according to new window size
        if props.pad_size_x != props.win_size_x - props.pad_x_delta:
            props.pad_size_x = props.win_size_x - props.pad_x_delta
            self.pad.resize(props.pad_size_y, props.pad_size_x)
        if props.pad_size_y != props.win_size_y - props.pad_y_delta:
            props.pad_size_y = props.win_size_y - props.pad_y_delta
            self.pad.resize(props.pad_size_y, props.pad_size_x)
            self.state.pad_y = 0  # reset pad position

        # print log
        self.pad.clear()
        self._print_log(props)

        # check if visible part of pad needs to be moved and display it
        self.state.cur_y, self.state.cur_x = self.pad.getyx()
        self._pad_refresh(props)

    def _cursor_msg_start(self, *args):
        # TODO: use other method and keybind with more fitting name?
        # jump to first line in log
        if self.state.cur_y > 0 or self.state.cur_x > 0:
            self.pad.move(0, 0)
            props = self._get_properties()
            self._pad_refresh(props)

    def _cursor_msg_end(self, *args):
        # TODO: use other method and keybind with more fitting name?
        # jump to last line in log
        props = self._get_properties()
        lines = self._get_num_log_lines(props.pad_size_x)
        if self.state.cur_y < lines:
            self.pad.move(lines, self.state.cur_x)
            self._pad_refresh(props)

    def _cursor_line_start(self, *args):
        # TODO: use other method and keybind with more fitting name?
        # move cursor up one page until first entry in log
        props = self._get_properties()
        if self.state.cur_y > 0:
            if self.state.cur_y - (props.win_size_y - props.pad_y_delta) >= 0:
                self.pad.move(self.state.cur_y - (props.win_size_y -
                                                  props.pad_y_delta),
                              self.state.cur_x)
            else:
                self.pad.move(0, self.state.cur_x)
            self._pad_refresh(props)

    def _cursor_line_end(self, *args):
        # TODO: use other method and keybind with more fitting name?
        # move cursor down one page until last entry in log
        props = self._get_properties()
        lines = self._get_num_log_lines(props.pad_size_x)
        if self.state.cur_y < lines:
            if self.state.cur_y + props.win_size_y - props.pad_y_delta < lines:
                self.pad.move(self.state.cur_y + props.win_size_y -
                              props.pad_y_delta, self.state.cur_x)
            else:
                self.pad.move(lines, self.state.cur_x)
            self._pad_refresh(props)

    def _cursor_up(self, *args):
        # move cursor up until first entry in list
        if self.state.cur_y > 0:
            self.pad.move(self.state.cur_y - 1, self.state.cur_x)
            self.state.cur_y, self.state.cur_x = self.pad.getyx()
            props = self._get_properties()
            self._pad_refresh(props)

    def _cursor_down(self, *args):
        # move cursor down until end of list
        props = self._get_properties()
        lines = self._get_num_log_lines(props.pad_size_x)
        if self.state.cur_y < lines:
            self.pad.move(self.state.cur_y + 1, self.state.cur_x)
            self.state.cur_y, self.state.cur_x = self.pad.getyx()
            self._pad_refresh(props)

    def _zoom_win(self, *args):
        """
        Zoom in and out of log window
        """

        # get positions and sizes for zoomed and normal mode
        if self.zoomed:
            self.zoomed = False
        else:
            self.zoomed = True
        props = self._get_properties()

        # resize window and pad
        self.resize_win(props.win_size_y, props.win_size_x)
        self.move_win(props.pos_y, props.pos_x)
        self.pad.resize(props.win_size_y - props.pad_y_delta,
                        props.win_size_x - props.pad_x_delta)
        self._move_pad()
        self._check_borders()

        # redraw everything
        if self.zoomed:
            self.redraw()
        else:
            MAIN_WINS["screen"].clear()
            MAIN_WINS["screen"].refresh()
            self.conversation.wins.list_win.redraw()
            self.conversation.wins.log_win.redraw()
            self.conversation.wins.input_win.redraw()

    def _go_back(self, *args):
        # if window was zoomed, switch back to normal view
        if self.zoomed:
            self._zoom_win()

        # reactivate input window
        self.state.active = True
        self.conversation.wins.input_win.state.active = True

    def process_input(self, char):
        """
        Process user input
        """

        self.state.cur_y, self.state.cur_x = self.pad.getyx()

        # look for special key mappings in keymap or process as text
        if char in self.config.keymap:
            func = self.keyfunc[self.config.keybinds[self.config.keymap[char]]]
            func()

        # display changes in the pad
        # TODO: switch this back on and remove redraw code from other methods?
        # self.redraw_pad()


class InputWin(Win):
    """
    Class for Input Windows
    """

    def __init__(self, config, conversation, title):
        Win.__init__(self, config, conversation, title)

        # input message
        self.msg = ""

    def redraw_pad(self):
        # if terminal size is invalid, stop here
        if not self.config.is_terminal_valid():
            return

        pos_y, pos_x = self.config.get_pos()
        win_size_y, win_size_x = self.config.get_size()

        self._move_pad()
        self._check_borders()
        self.pad.refresh(self.state.pad_y, self.state.pad_x,
                         pos_y + 1, pos_x + 1,
                         pos_y + win_size_y - 2,
                         pos_x + win_size_x - 2)

    def _cursor_up(self, *args):
        segment = args[0]
        if self.state.cur_y > 0:
            self.pad.move(self.state.cur_y - 1,
                          min(self.state.cur_x,
                              len(segment[self.state.cur_y - 1])))

    def _cursor_down(self, *args):
        # pad properties
        pad_y_max, unused_pad_x_max = self.pad.getmaxyx()

        segment = args[0]
        if self.state.cur_y < pad_y_max and \
           self.state.cur_y < len(segment) - 1:
            self.pad.move(self.state.cur_y + 1,
                          min(self.state.cur_x,
                              len(segment[self.state.cur_y + 1])))

    def _cursor_left(self, *args):
        if self.state.cur_x > 0:
            self.pad.move(self.state.cur_y, self.state.cur_x - 1)

    def _cursor_right(self, *args):
        # pad properties
        unused_pad_y_max, pad_x_max = self.pad.getmaxyx()

        segment = args[0]
        if self.state.cur_x < pad_x_max and \
           self.state.cur_x < len(segment[self.state.cur_y]):
            self.pad.move(self.state.cur_y, self.state.cur_x + 1)

    def _cursor_line_start(self, *args):
        if self.state.cur_x > 0:
            self.pad.move(self.state.cur_y, 0)

    def _cursor_line_end(self, *args):
        # pad properties
        unused_pad_y_max, pad_x_max = self.pad.getmaxyx()

        segment = args[0]
        if self.state.cur_x < pad_x_max and \
           self.state.cur_x < len(segment[self.state.cur_y]):
            self.pad.move(self.state.cur_y, len(segment[self.state.cur_y]))

    def _cursor_msg_start(self, *args):
        if self.state.cur_y > 0 or self.state.cur_x > 0:
            self.pad.move(0, 0)

    def _cursor_msg_end(self, *args):
        segment = args[0]
        if self.state.cur_y < len(segment) - 1 or \
           self.state.cur_x < len(segment[-1]):
            self.pad.move(len(segment) - 1, len(segment[-1]))

    def _send_msg(self, *args):
        # do not send empty messages
        if self.msg == "":
            return

        # let conversation actually send the message
        self.conversation.send_msg(self.msg)

        # reset input
        self.msg = ""
        self.pad.clear()

        # reset pad size
        win_size_y, win_size_x = self.win.getmaxyx()
        self.pad.resize(win_size_y - 2, win_size_x - 2)

    def _delete_char(self, *args):
        segment = args[0]
        if self.state.cur_x > 0:
            # delete charater within a line
            segment[self.state.cur_y] = \
                segment[self.state.cur_y][:self.state.cur_x - 1] +\
                segment[self.state.cur_y][self.state.cur_x:]
        elif self.state.cur_y > 0:
            # delete newline
            old_prev_len = len(segment[self.state.cur_y - 1])
            segment[self.state.cur_y - 1] = segment[self.state.cur_y - 1] +\
                segment[self.state.cur_y]
            segment = segment[:self.state.cur_y] + \
                segment[self.state.cur_y + 1:]
        # reconstruct and display message
        self.msg = "\n".join(segment)
        self.pad.erase()
        self.pad.addstr(self.msg)
        # move cursor to new position
        if self.state.cur_x > 0:
            self.pad.move(self.state.cur_y, self.state.cur_x - 1)
        elif self.state.cur_y > 0:
            self.pad.move(self.state.cur_y - 1, old_prev_len)

    def _delete_line_end(self, *args):
        segment = args[0]

        # delete from cursor to end of line
        segment[self.state.cur_y] = \
            segment[self.state.cur_y][:self.state.cur_x]

        # reconstruct message
        self.msg = "\n".join(segment)
        self.pad.erase()
        self.pad.addstr(self.msg)

    def _delete_line(self, *args):
        segment = args[0]

        # delete the current line
        del segment[self.state.cur_y]

        # reconstruct message
        self.msg = "\n".join(segment)
        self.pad.erase()
        self.pad.addstr(self.msg)

        # move cursor to new position
        if len(segment) <= self.state.cur_y:
            self.state.cur_y = max(0, len(segment) - 1)
        if not segment:
            self.state.cur_x = 0
        elif len(segment[self.state.cur_y]) < self.state.cur_x:
            self.state.cur_x = len(segment[self.state.cur_y])
        self.pad.move(self.state.cur_y, self.state.cur_x)

    def _go_back(self, *args):
        self.state.active = False
        self.conversation.wins.log_win.state.active = False

        # assume user read all messages and set lastread to last message
        self.conversation.set_lastread()

    def _go_log(self):
        """
        Jump to log
        """

        self.state.active = False
        self.conversation.wins.log_win.state.active = True

    def process_input(self, char):
        """
        Process user input (character)
        """

        segments = self.msg.split("\n")
        self.state.cur_y, self.state.cur_x = self.pad.getyx()
        pad_size_y, pad_size_x = self.pad.getmaxyx()

        # look for special key mappings in keymap or process as text
        if char in self.config.keymap:
            func = self.keyfunc[self.config.keybinds[self.config.keymap[char]]]
            func(segments)
        elif char == curses.ascii.ctrl("o"):
            self._go_log()
        else:
            # insert new character into segments
            if not isinstance(char, str):
                return
            # make sure new char fits in the pad
            if len(segments) == pad_size_y - 1 and char == "\n":
                pad_size_y += 1
                self.pad.resize(pad_size_y, pad_size_x)
            if len(segments[self.state.cur_y]) == pad_size_x - 2 and \
               char != "\n":
                pad_size_x += 1
                self.pad.resize(pad_size_y, pad_size_x)

            segments[self.state.cur_y] = \
                segments[self.state.cur_y][:self.state.cur_x] + char +\
                segments[self.state.cur_y][self.state.cur_x:]
            # reconstruct orginal message for output in pad
            self.msg = "\n".join(segments)
            # reconstruct segments in case newline character was entered
            segments = self.msg.split("\n")
            # output new message in pad
            self.pad.erase()
            self.pad.addstr(self.msg)
            # move cursor to new position
            if char == "\n":
                self.pad.move(self.state.cur_y + 1, 0)
            else:
                self.pad.move(self.state.cur_y, self.state.cur_x + 1)
        # display changes in the pad
        self.redraw_pad()
