# coding: utf-8
#
# for CUI scripts.

import os
import re
import time
import math
import random
import inspect
import requests
import datetime
from enum import Enum

from natsort import natsorted

VERSION = 1.1

_OK = "\x1b[96m"
_WA = "\x1b[31m"
_IM = "\x1b[92m"
_TE = "\x1b[95m"
_RS = "\x1b[39m"

EMPHASIZE = [
    r"\(.*?\)",
    r"\[.*?\]",
    r"\s\d+%?\s",
    r"\s\d+%?$",
    r"^\d+%?\s",
    r"\s[<|>]\s",
    r"https?://\S+",
    r"\s[0-9]+(?:\.[0-9]+){4}",
    r"\s\d+[/|\.]\d+?\s",
    r"\s\d+[/|\.]\d+?$",
]


class Args(Enum):
    FORCE = 1
    TIMEPUT = 2
    PRINTOUT = 3
    ADDMARK = 4
    FULLCOLOR = 5
    REWRITE = 6
    ENDL = 7
    FUNCNAME = 8
    EMPHASIZE = 9
    DELAY = 10


FORCE = Args.FORCE


class CUI_MOD:
    def __init__(self):
        self.color_list = (_IM, _OK, _TE, _WA, _RS)
        self.file_path = None
        self.file_put = False
        self.default_timeput = True
        self.default_printout = True
        self.default_addmark = True
        self.default_fullcolor = True
        self.default_rewrite = False
        self.default_endl = True
        self.default_funcname = False
        self.default_emphasize = False
        self.default_delay = False

    def cli(
        self,
        text,
        number,
        *,
        timeput=False,
        printout=False,
        addmark=False,
        fullcolor=False,
        rewrite=False,
        endl=False,
        emphasize=False,
        funcname=False,
        delay=False
    ):
        """Color Text output/print.

        :param text: output text.\n
        :param number: 1=[+]@Green, 2=[x]@Cyan, 3=[o]@Magenta, 4=[!]@Red\n
        :flag timeput: add time print. default=True\n
        :flag printout: print in cli. default=True\n
        :flag addmark: add [+] this like marks. default=True\n
        :flag fullcolor: full color output of text. default=True\n
        :flag rewrite: add \\r overwrite. default=False\n
        :flag endl: add \\n to last of line. default=True\n
        :flag emphasize: highlight syntax. number to set limit. default=False\n
        :flag funcname: src called function name add to text. default=False\n
        :param delay: add random delay to end function.\n
        """
        args = {
            Args.TIMEPUT: (self.default_timeput, timeput),
            Args.PRINTOUT: (self.default_printout, printout),
            Args.ADDMARK: (self.default_addmark, addmark),
            Args.FULLCOLOR: (self.default_fullcolor, fullcolor),
            Args.REWRITE: (self.default_rewrite, rewrite),
            Args.ENDL: (self.default_endl, endl),
            Args.FUNCNAME: (self.default_funcname, funcname),
            Args.EMPHASIZE: (self.default_emphasize, emphasize),
            Args.DELAY: (self.default_delay, delay),
        }
        opt = {}
        for key_, val_ in args.items():
            selfv, argsv = val_
            if key_ == Args.EMPHASIZE and emphasize in [1, 2, 3]:
                chk = int(emphasize)
                opt.update({key_: chk})
                continue
            if (selfv or argsv) and argsv != Args.FORCE:
                chk = True
            else:
                chk = False
            opt.update({key_: chk})
        ret = False
        if opt[Args.TIMEPUT]:
            now = now_time()
        else:
            now = ""
        if opt[Args.ADDMARK]:
            m_im = "[{}+{}] {} {}:{} ".format(_IM, _RS, now, _IM, _RS)
            m_ok = "[{}o{}] {} {}:{} ".format(_OK, _RS, now, _OK, _RS)
            m_te = "[{}*{}] {} {}:{} ".format(_TE, _RS, now, _TE, _RS)
            m_wa = "[{}!{}] {} {}:{} ".format(_WA, _RS, now, _WA, _RS)
        else:
            m_im = m_ok = m_te = m_wa = ""
        num_set = {1: (_IM, m_im), 2: (_OK, m_ok), 3: (_TE, m_te), 4: (_WA, m_wa)}
        if number in num_set.keys():
            markindex = num_set.get(number)
            colorname = markindex[0]
            markname = markindex[1]
            if opt[Args.EMPHASIZE]:
                if opt[Args.FULLCOLOR] == False:
                    em = []
                    for re_em in EMPHASIZE:
                        comp = re.compile(re_em)
                        em += comp.findall(text)
                    if type(opt[Args.EMPHASIZE]) == int:
                        new_em = []
                        nat_em = {}
                        for e in em:
                            textfind = text.find(e)
                            if textfind > -1:
                                nat_em.update({textfind: e})
                        new_em = natsorted(nat_em)
                        new_em = [nat_em[ne] for ne in new_em]
                        em = new_em[: opt[Args.EMPHASIZE]]
                    if em:
                        for rpl_em in em:
                            text = text.replace(rpl_em, colorname + rpl_em + _RS)
            if text[0:1] == "\n":
                text = text.replace("\n", "", 1)
                ret = True
            else:
                ret = False
            if opt[Args.FUNCNAME]:
                fn = self.get_funcname(inspect.stack())
            else:
                fn = ""
            if opt[Args.FULLCOLOR]:
                checkrs = markname.replace(_RS, "")
                colortext = colorname + checkrs + fn + text + _RS
            else:
                colortext = markname + fn + text
        else:
            colortext = ""
        if self.file_put:
            filetext = colortext
            for c in self.color_list:
                if colortext.find(c) > -1:
                    filetext = filetext.replace(c, "")
            if self.file_path:
                self.file_out(self.file_path, filetext)
            else:
                self.file_out("stdout.log", filetext)
        if opt[Args.PRINTOUT]:
            if opt[Args.REWRITE]:
                print("\r{}".format(colortext), end="")
            else:
                if ret:
                    colortext = "\n" + colortext
                if opt[Args.ENDL]:
                    print(colortext)
                else:
                    if colortext[-2:] == "\n":
                        colortext = colortext[:-2]
                    print(colortext, end="")
        if opt[Args.DELAY]:
            delays = [0.01, 0.05, 0.10, 0.13, 0.16, 0.20]
            time.sleep(random.choice(delays))
        return colortext

    def file_init(self, path):
        self.file_path = os.path.abspath(path)
        self.file_put = True
        return [self.file_path, self.file_put]

    def file_out(self, fname, text):
        if os.path.isfile(fname):
            with open(fname, "a+") as f:
                f.write(text + "\n")
        else:
            with open(fname, "w") as f:
                f.write(text + "\n")

    # ? return or print random color multiple text lines.
    def rainbow_lines(self, lines, printout=False):
        colors = self.color_list[0:3]
        reset = _RS
        new_lines = ""
        for line in lines.split("\n"):
            pick = random.choice(colors)
            new_lines += (pick + line + reset) + "\n"
        if printout:
            print(new_lines)
        else:
            return new_lines

    # ? return random color text line.
    def random_oneline(self, line):
        colors = self.color_list[0:3]
        reset = _RS
        return random.choice(colors) + line + reset

    def get_funcname(self, stack1):
        func = stack1[-1].code_context[0].strip()
        func = func.replace("\n", "") + func + " "
        return func


# ? return colors.
def get_color():
    return _OK, _WA, _IM, _TE, _RS


# ? return string datetime like this: 00:00:00
def now_time():
    n = datetime.datetime.now()
    n = str(n).split(".")[0].split()[1]
    return n


# ? fixed text width in argpase help message.
def argparse_wide(formatter, w=120, h=40):
    try:
        kwargs = {"width": w, "max_help_position": h}
        formatter(None, **kwargs)
        return lambda prog: formatter(prog, **kwargs)
    except TypeError:
        return formatter


# ? convert bytes to general syntax.
def calculate_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB")
    calc = int(math.floor(math.log(size_bytes, 1024)))
    calc_pow = math.pow(1024, calc)
    calc_round = round(size_bytes / calc_pow, 2)
    return "{} {}".format(calc_round, size_name[calc])


# ? update cuimod from github.
def update_cuimod():
    cli = CUI_MOD().cli

    def GET(u):
        try:
            req = requests.get(u)
            response = req.status_code
            if response == 200:
                return req.content
            else:
                cli(
                    "cuimod.py: status code: {} error: {}".format(response, req.reason),
                    4,
                )
                return None
        except Exception as err:
            cli("cuimod.py: https request error. {}".format(err), 4)
            return None

    url = "https://raw.githubusercontent.com/ar0f/cuimod/master/cuimod.py"
    ver = "https://raw.githubusercontent.com/ar0f/cuimod/master/version"
    resp = GET(ver)
    answer = False
    get_ver = None
    if resp:
        get_ver = float(resp)
        if VERSION < get_ver:
            cli(
                "cuimod.py: new version available. ver.{} -> ver.{}".format(
                    VERSION, get_ver
                ),
                1,
            )
            cli("cuimod.py: do you want update? (y, n)", 1)
            ans = input("> ")
            if ans in ["Y", "y", "YES", "Yes", "yes"]:
                answer = True
    if answer:
        resp = GET(url)
        if resp:
            with open(__file__, "wb") as w:
                w.write(resp)
            size = calculate_size(len(resp))
            cli("cuimod.py: updated to ver.{} size: {}\n".format(get_ver, size), 2)
