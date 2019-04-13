"""
History: (file) logging for nuqql conversations
"""

import datetime
import logging
import pathlib
import os


class LogMessage:
    """Class for log messages to be displayed in LogWins"""

    def __init__(self, tstamp, sender, msg, own=False):
        """
        Initialize log message with timestamp, sender of the message, and
        the message itself
        """

        # timestamp
        self.tstamp = tstamp

        # sender could be us or buddy/other user, as
        # indicated by self.own (helps with coloring etc. later)
        self.sender = sender
        self.own = own

        # the message itself
        self.msg = msg

        # has message been read?
        self.is_read = False

    def get_short_sender(self):
        """
        Convert name to a shorter version
        """

        # TODO: improve? Save short name in account and buddy instead?
        return self.sender.split("@")[0]

    def read(self):
        """
        Format and return log message; mark it as read
        """

        # format message
        msg = "{0} {1}: {2}\n".format(self.tstamp.strftime("%H:%M:%S"),
                                      self.get_short_sender(),
                                      self.msg)

        # message has now been read
        self.is_read = True

        return msg

    def is_equal(self, other):
        """
        Check if this message and the LogMessage "other" match
        """

        if self.tstamp != other.tstamp:
            return False
        if self.sender != other.sender:
            return False
        if self.msg != other.msg:
            return False

        return True


def get_logger(name, file_name):
    """
    Create a logger for a conversation
    """

    # create logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # create handler
    fileh = logging.FileHandler(file_name)
    fileh.setLevel(logging.DEBUG)
    fileh.terminator = "\r\n"

    # create formatter
    formatter = logging.Formatter(
        # fmt="%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s",
        fmt="%(message)s",
        datefmt="%s")

    # add formatter to handler
    fileh.setFormatter(formatter)

    # add handler to logger
    logger.addHandler(fileh)

    # return logger to caller
    return logger


def init_logger(backend, account, conv_name):
    """
    Init logger for a conversation
    """

    # make sure log directory exists
    log_dir = str(pathlib.Path.home()) + \
        "/.config/nuqql/conversation/{}/{}/{}".format(backend.name,
                                                      account.aid,
                                                      conv_name)
    pathlib.Path(log_dir).mkdir(parents=True, exist_ok=True)

    # create logger with log name and log file
    log_name = "{} {} {}".format(backend.name, account.aid, conv_name)
    log_file = log_dir + "/history"
    logger = get_logger(log_name, log_file)

    # return the ready logger and the log file to caller
    return logger, log_file


def parse_log_line(line):
    """
    Parse line from log file and return a LogMessage
    """

    # parse line
    parts = line.split(sep=" ", maxsplit=3)
    tstamp = parts[0]
    direction = parts[1]
    is_own = False
    if direction == "OUT":
        is_own = True
    sender = parts[2]
    msg = parts[3][:-2]
    tstamp = datetime.datetime.fromtimestamp(int(tstamp))

    # create and return LogMessage
    log_msg = LogMessage(tstamp, sender, msg, own=is_own)
    return log_msg


def create_log_line(tstamp, direction, sender, msg):
    """
    Create a line for the log files
    """
    # TODO: create from a LogMessage

    return "{} {} {} {}".format(tstamp, direction, sender, msg)


def get_lastread(backend, account, conv_name):
    """
    Get last read message from "lastread" file of the conversation
    """

    # make sure log directory exists
    lastread_dir = str(pathlib.Path.home()) + \
        "/.config/nuqql/conversation/{}/{}/{}".format(backend.name,
                                                      account.aid,
                                                      conv_name)
    pathlib.Path(lastread_dir).mkdir(parents=True, exist_ok=True)
    lastread_file = lastread_dir + "/lastread"

    try:
        with open(lastread_file, newline="\r\n") as in_file:
            lines = in_file.readlines()
            for line in lines:
                log_msg = parse_log_line(line)
                log_msg.is_read = True
                return log_msg
    except FileNotFoundError:
        return None


def set_lastread(backend, account, conv_name, tstamp, direction, sender, msg):
    """
    Set last read message in "lastread" file of the conversation
    """

    # make sure log directory exists
    lastread_dir = str(pathlib.Path.home()) + \
        "/.config/nuqql/conversation/{}/{}/{}".format(backend.name,
                                                      account.aid,
                                                      conv_name)
    pathlib.Path(lastread_dir).mkdir(parents=True, exist_ok=True)
    lastread_file = lastread_dir + "/lastread"

    line = create_log_line(tstamp, direction, sender, msg) + "\r\n"
    lines = []
    lines.append(line)
    with open(lastread_file, "w+") as in_file:
        lines = in_file.writelines(lines)


def get_last_log_line(conv):
    """
    Read last LogMessage from log file
    """

    # make sure log directory exists
    lastread_dir = str(pathlib.Path.home()) + \
        "/.config/nuqql/conversation/{}/{}/{}".format(conv.backend.name,
                                                      conv.account.aid,
                                                      conv.name)
    pathlib.Path(lastread_dir).mkdir(parents=True, exist_ok=True)
    lastread_file = lastread_dir + "/lastread"

    try:
        # negative seeking requires binary mode
        with open(lastread_file, "rb") as in_file:
            # check if file contains at least 2 bytes
            in_file.seek(0, os.SEEK_END)
            if in_file.tell() < 3:
                return None

            # try to find last line
            in_file.seek(-3, os.SEEK_END)
            while in_file.read(2) != b"\r\n":
                try:
                    in_file.seek(-3, os.SEEK_CUR)
                except IOError:
                    in_file.seek(-2, os.SEEK_CUR)
                    if in_file.tell() == 0:
                        break

            # read and return last line as LogMessage
            last_line = in_file.read()
            log_msg = parse_log_line(last_line.decode())
            return log_msg
    except FileNotFoundError:
        return None


def init_log_from_file(conv):
    """
    Initialize a conversation's log from the conversation's log file
    """

    # get last read log message
    last_read = get_lastread(conv.backend, conv.account, conv.name)
    is_read = True

    lines = []
    with open(conv.log_file, newline="\r\n") as in_file:
        lines = in_file.readlines()
        for line in lines:
            # add log message to the conversation's log
            log_msg = parse_log_line(line)
            log_msg.is_read = is_read
            conv.log_win.add(log_msg)

            # if this is the last read message, following message will be
            # marked as unread
            if last_read and last_read.is_equal(log_msg):
                is_read = False
    if lines:
        # if there were any log messages in the log file, put a marker in the
        # log where the new messages start
        tstamp = datetime.datetime.now()
        log_msg = LogMessage(tstamp, "<event>", "<Started new conversation.>",
                             own=True)
        log_msg.is_read = True
        conv.log_win.add(log_msg)