"""
Nuqql Conversations
"""

import datetime

from types import SimpleNamespace
from pathlib import Path

import nuqql.history
import nuqql.win


# list of active conversations
CONVERSATIONS = []


class Conversation:
    """
    Class for conversations
    """

    def __init__(self, backend, account, name):
        # general
        self.name = name
        self.notification = 0

        # backend info
        self.backend = backend
        self.account = account

        # windows of the conversation
        self.wins = SimpleNamespace()
        self.wins.log_win = None
        self.wins.input_win = None
        self.wins.list_win = None

        # history and logging
        self.history = SimpleNamespace()
        self.history.log = []
        self.history.logger = None
        self.history.log_file = None

    def activate(self):
        """
        Activate windows of conversation
        """

        # check log_win to determine, if windows are already created
        if self.wins.log_win is not None:
            self.wins.input_win.state.active = True
            self.wins.input_win.redraw()
            self.wins.log_win.state.active = False
            self.wins.log_win.redraw()
            self.clear_notifications()
            return

    def activate_log(self):
        """
        Activate windows of conversation and go to history
        """

        # check log_win to determine, if windows are already created
        if self.wins.log_win is not None:
            self.wins.input_win.state.active = False
            self.wins.input_win.redraw()
            self.wins.log_win.state.active = True
            self.wins.log_win.redraw()
            self.clear_notifications()
            return

    def has_windows(self):
        """
        Check if conversation has already created its windows
        """

        if self.wins.log_win:
            return True

        return False

    def create_windows(self):
        """
        Create windows for this conversation
        """

        # implemented in sub classes

    def get_name(self):
        """
        Get the name of the conversation, depending on type
        """

        # implemented in sub classes

    def log(self, sender, msg, tstamp=None):
        """
        Log message to conversation's history/log window
        """

        # create a log message and put it into conversation's history
        if tstamp is None:
            tstamp = datetime.datetime.now()
        log_msg = nuqql.history.LogMessage(tstamp, sender, msg)
        self.history.log.append(log_msg)

        # if conversation is already active, redraw the log window
        if self.is_active():
            self.wins.log_win.redraw()

        return log_msg

    def notify(self):
        """
        Notify this conversation about new messages
        """

        self.notification = 1

        if self.wins.list_win:
            self.wins.list_win.redraw_pad()

    def clear_notifications(self):
        """
        Clear notifications of buddy
        """

        self.notification = 0
        if self.wins.list_win:
            self.wins.list_win.redraw_pad()

    def __lt__(self, other):
        # sort based on get_key output
        return self.get_key() < other.get_key()

    # status to sorting key mapping
    status_key = {
        "on": 0,
        "afk": 1,
        "off": 2,
    }

    def get_key(self):
        """
        Get a key for sorting this conversation
        """

        # implemented in sub classes

    def is_active(self):
        """
        Check if this conversation is currently active, and return True if it
        is the case; otherwise, return False.
        """

        # check if input win is active
        if self.wins.input_win and self.wins.input_win.state.active:
            return True

        # check if log win is active
        if self.wins.log_win and self.wins.log_win.state.active:
            return True

        return False

    def is_any_active(self):
        """
        Check if any conversation is currently active
        """

        if self.is_active():
            return True

        for conv in CONVERSATIONS:
            if conv.is_active():
                return True

        return False

    def process_input(self, char):
        """
        Process user input in active window
        """

        # try to give control to the input win first...
        if self.wins.input_win and self.wins.input_win.state.active:
            self.wins.input_win.process_input(char)
            return

        # then, try to give control to the log win
        if self.wins.log_win and self.wins.log_win.state.active:
            self.wins.log_win.process_input(char)
            return

    def send_msg(self, msg):
        """
        Send message coming from the UI/input window
        """

        # implemented in sub classes

    def set_lastread(self):
        """
        Helper that sets lastread to the last message in the conversation,
        thus, marking all messages as read.
        """

        # only relevant for BuddyConversation. Implemented there.


class BuddyConversation(Conversation):
    """
    Class for conversations with buddies
    """

    def __init__(self, backend, account, name):
        Conversation.__init__(self, backend, account, name)

        self.peers = []
        self.wins.list_win = nuqql.win.MAIN_WINS["list"]
        self.history.logger, self.history.log_file = nuqql.history.init_logger(
            self)

    def create_windows(self):
        """
        Create windows for this conversation
        """

        # create standard chat windows
        log_title = "Chat log with {0}".format(self.name)
        input_title = "Message to {0}".format(self.name)

        log_config = nuqql.config.get("log_win")
        self.wins.log_win = nuqql.win.LogWin(log_config, self, log_title)
        self.wins.log_win.list = self.history.log
        input_config = nuqql.config.get("input_win")
        self.wins.input_win = nuqql.win.InputWin(input_config, self,
                                                 input_title)

        # try to read old messages from message history
        nuqql.history.init_log_from_file(self)

    def get_name(self):
        """
        Get the name of the conversation, depending on type
        """

        # check if there are pending notifications
        if self.notification > 0:
            notify = "# "
        else:
            notify = ""

        peer = self.peers[0]
        return "{0}[{1}] {2}".format(notify, peer.status, peer.alias)

    def get_key(self):
        """
        Get a key for sorting this conversation
        """

        # defaults
        sort_notify = 0 - self.notification
        sort_type = 0
        sort_status = 0
        sort_name = self.name

        peer = self.peers[0]
        try:
            sort_status = self.status_key[peer.status]
        except KeyError:
            sort_status = len(self.status_key) + 1
        sort_name = peer.alias

        # return tuple of sort keys
        return sort_notify, sort_type, sort_status, sort_name

    def send_msg(self, msg):
        """
        Send message coming from the UI/input window
        """

        # TODO: unify the logging in a method of Conversation?
        # log message
        tstamp = datetime.datetime.now()
        log_msg = nuqql.history.LogMessage(tstamp, "you", msg, own=True)
        self.wins.log_win.add(log_msg)

        # send message and log it in the history file
        self.backend.client.send_msg(self.account.aid, self.name, msg)
        nuqql.history.log(self, log_msg)

    def set_lastread(self):
        """
        Helper that sets lastread to the last message in the conversation,
        thus, marking all messages as read.
        """

        log_msg = None
        if self.wins.log_win.list:
            log_msg = self.wins.log_win.list[-1]
            # do not put new conversation event in last_read
            if log_msg.sender == "<event>" and \
               log_msg.msg == "<Started new conversation.>":
                log_msg = None
                if len(self.wins.log_win.list) > 1:
                    log_msg = self.wins.log_win.list[-2]

        # if there is a log message, write it to lastread
        if log_msg:
            nuqql.history.set_lastread(self, log_msg)


class BackendConversation(Conversation):
    """
    Class for backend conversations
    """

    def create_windows(self):
        """
        Create windows for this conversation
        """

        # create windows command windows for backends
        log_title = "Command log of {0}".format(self.name)
        input_title = "Command to {0}".format(self.name)

        log_config = nuqql.config.get("log_win")
        self.wins.log_win = nuqql.win.LogWin(log_config, self, log_title)
        self.wins.log_win.list = self.history.log
        input_config = nuqql.config.get("input_win")
        self.wins.input_win = nuqql.win.InputWin(input_config, self,
                                                 input_title)

    def get_name(self):
        """
        Get the name of the conversation, depending on type
        """

        # check if there are pending notifications
        if self.notification > 0:
            notify = "# "
        else:
            notify = ""

        return "{0}{{backend}} {1}".format(notify, self.name)

    def get_key(self):
        """
        Get a key for sorting this conversation
        """

        # defaults
        sort_notify = 0 - self.notification
        sort_type = 0
        sort_status = 0
        sort_name = self.name
        sort_type = 1

        # return tuple of sort keys
        return sort_notify, sort_type, sort_status, sort_name

    def send_msg(self, msg):
        """
        Send message coming from the UI/input window
        """

        # TODO: unify the logging in a method of Conversation?
        # log message
        tstamp = datetime.datetime.now()
        log_msg = nuqql.history.LogMessage(tstamp, "you", msg, own=True)
        self.wins.log_win.add(log_msg)

        # send command message to backend
        if self.backend is not None:
            self.backend.client.send_command(msg)


class NuqqlConversation(Conversation):
    """
    Class for the nuqql conversation
    """

    def create_windows(self):
        """
        Create windows for this conversation
        """

        # create command windows for nuqql
        log_title = "Command log of {0}".format(self.name)
        input_title = "Command to {0}".format(self.name)

        log_config = nuqql.config.get("log_win")
        self.wins.log_win = nuqql.win.LogWin(log_config, self, log_title)
        self.wins.log_win.list = self.history.log
        input_config = nuqql.config.get("input_win")
        self.wins.input_win = nuqql.win.InputWin(input_config, self,
                                                 input_title)

        # nuqql itself needs a list window for buddy list
        list_config = nuqql.config.get("list_win")
        self.wins.list_win = nuqql.win.ListWin(list_config, self,
                                               "Conversation list")
        # set list to conversations
        self.wins.list_win.list = CONVERSATIONS
        # mark nuqql's list window as active, so main loop does not quit
        self.wins.list_win.state.active = True

    def get_name(self):
        """
        Get the name of the conversation, depending on type
        """

        # check if there are pending notifications
        if self.notification > 0:
            notify = "# "
        else:
            notify = ""

        return "{0}{{nuqql}}".format(notify)

    def get_key(self):
        """
        Get a key for sorting this conversation
        """

        # defaults
        sort_notify = 0 - self.notification
        sort_type = 0
        sort_status = 0
        sort_name = self.name
        sort_type = 2

        # return tuple of sort keys
        return sort_notify, sort_type, sort_status, sort_name

    def send_msg(self, msg):
        """
        Send message coming from the UI/input window
        """

        # TODO: unify the logging in a method of Conversation?
        # log message
        tstamp = datetime.datetime.now()
        log_msg = nuqql.history.LogMessage(tstamp, "you", msg, own=True)
        self.wins.log_win.add(log_msg)

        # handle nuqql command
        handle_nuqql_command(self, msg)


def handle_nuqql_global_status(conv, parts):
    """
    Handle nuqql command: global-status
    Call getter and setter funcions
    """

    if not parts:
        return
    sub_command = parts[0]
    if sub_command == "set":
        if len(parts) < 2:
            return
        handle_nuqql_global_status_set(conv, parts[1:])
    elif sub_command == "get":
        handle_nuqql_global_status_get(conv)


def handle_nuqql_global_status_set(conv, status):
    """
    Handle nuqql command: global-status set
    Set status and store it in global_status file
    """

    # only use the first word as status
    if not status or status[0] == "":
        return
    status = status[0]

    # write status
    write_global_status(status)

    # set status in all backends and their accounts
    for conversation in CONVERSATIONS:
        if isinstance(conversation, BackendConversation):
            for acc in conversation.backend.accounts.values():
                conversation.backend.client.send_status_set(acc.aid, status)

    # log message
    tstamp = datetime.datetime.now()
    msg = "global-status: " + status
    log_msg = nuqql.history.LogMessage(tstamp, "nuqql", msg)
    conv.wins.log_win.add(log_msg)


def handle_nuqql_global_status_get(conv):
    """
    Handle nuqql command: global-status get
    Read status from global_status file
    """

    # read status
    status = read_global_status()
    if status == "":
        return

    # log message
    tstamp = datetime.datetime.now()
    msg = "global-status: " + status
    log_msg = nuqql.history.LogMessage(tstamp, "nuqql", msg)
    conv.wins.log_win.add(log_msg)


def write_global_status(status):
    """
    Write global status to global_status file
    """

    # write status to file
    global_status_dir = str(Path.home()) + "/.config/nuqql"
    Path(global_status_dir).mkdir(parents=True, exist_ok=True)
    global_status_file = global_status_dir + "/global_status"
    line = status + "\n"
    lines = []
    lines.append(line)
    with open(global_status_file, "w+") as status_file:
        status_file.writelines(lines)


def read_global_status():
    """
    Read global status from global_status file
    """

    # if there is a global_status file, read it
    global_status_dir = str(Path.home()) + "/.config/nuqql"
    Path(global_status_dir).mkdir(parents=True, exist_ok=True)
    global_status_file = global_status_dir + "/global_status"
    try:
        with open(global_status_file) as status_file:
            line = status_file.readline()
            status = line.split()
            if not status:
                return ""
            return status[0]
    except FileNotFoundError:
        return ""


def handle_nuqql_command(conv, msg):
    """
    Handle a nuqql command (from the nuqql conversation)
    """

    # parse message
    parts = msg.split()
    if not parts:
        return

    # check command and call helper functions
    command = parts[0]
    if command == "global-status":
        handle_nuqql_global_status(conv, parts[1:])


def log_main_window(msg):
    """
    Log message to main windows
    """

    now = datetime.datetime.now()
    log_msg = nuqql.history.LogMessage(now, "nuqql", msg)
    nuqql.win.MAIN_WINS["log"].add(log_msg)


def resize_main_window():
    """
    Resize main window
    """

    # get main win
    screen = nuqql.win.MAIN_WINS["screen"]

    # get new maxima
    max_y, max_x = screen.getmaxyx()

    # redraw main windows
    screen.clear()
    screen.refresh()

    # redraw conversation windows
    found_active = False
    for conv in CONVERSATIONS:
        # resize and move conversation windows
        if conv.wins.list_win:
            size_y, size_x = conv.wins.list_win.config.get_size()
            conv.wins.list_win.resize_win(size_y, size_x)
        if conv.wins.log_win:
            # TODO: move zoom/resizing to win.py?
            if conv.wins.log_win.zoomed:
                size_y, size_x = max_y, max_x
                pos_y, pos_x = 0, 0
                conv.wins.log_win.state.pad_y = 0  # reset pad position
            else:
                size_y, size_x = conv.wins.log_win.config.get_size()
                pos_y, pos_x = conv.wins.log_win.config.get_pos()
            conv.wins.log_win.resize_win(size_y, size_x)
            conv.wins.log_win.move_win(pos_y, pos_x)
        if conv.wins.input_win:
            size_y, size_x = conv.wins.input_win.config.get_size()
            conv.wins.input_win.resize_win(size_y, size_x)
            pos_y, pos_x = conv.wins.input_win.config.get_pos()
            conv.wins.input_win.move_win(pos_y, pos_x)
        # redraw active conversation windows
        if conv.is_active():
            found_active = True
            conv.wins.list_win.redraw()
            conv.wins.input_win.redraw()
            conv.wins.log_win.redraw()

    # if there are no active conversations, redraw nuqql main windows
    if not found_active:
        nuqql.win.MAIN_WINS["list"].redraw()
        nuqql.win.MAIN_WINS["log"].redraw()
        nuqql.win.MAIN_WINS["input"].redraw()


def create_main_windows():
    """
    Create main UI windows
    """

    # main screen
    # dummy conversation for main windows, creates log_win and input_win
    nuqql_conv = NuqqlConversation(None, None, "nuqql")
    nuqql_conv.create_windows()
    CONVERSATIONS.append(nuqql_conv)

    # draw list
    nuqql_conv.wins.list_win.redraw()
    nuqql_conv.wins.log_win.redraw()
    nuqql_conv.wins.input_win.redraw()

    # save windows
    nuqql.win.MAIN_WINS["list"] = nuqql_conv.wins.list_win
    nuqql.win.MAIN_WINS["log"] = nuqql_conv.wins.log_win
    nuqql.win.MAIN_WINS["input"] = nuqql_conv.wins.input_win
