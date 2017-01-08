# -*- coding: utf-8 -*-
import subprocess
import sys
import shlex
import re
import time
import datetime
import os
import curses
import locale

from turn_it_off import *
from list_alarms import *

from curses import textpad

os.environ["TERMINFO"] = "/opt/local/share/terminfo"
os.environ["TERM"] = "xterm-256color"

# unicode was not displayed properly
locale.setlocale(locale.LC_ALL,"")

from subprocess import PIPE, STDOUT

# Inspirations:
# http://patorjk.com/software/taag/#p=display&f=Bloody&t=TERROR%0AWAKE%0AUP
# http://www.seevishal.com/?p=
# https://stackoverflow.com/questions/1726590/python-stdin-eof

# check if at run is aktivated:
# launchctl load -w /System/Library/LaunchDaemons/com.apple.atrun.plist
# https://developer.apple.com/library/mac/documentation/darwin/reference/manpages/man8/atrun.8.html

# USEFUL COMMANDS:
# pmset -g sched
# sudo pmset schedule cancel 0
# at -l or atq
# atrm NUMBER

# change working directory to dir where this file is stored
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# Pack files together to check if they are available
files = {'alarmscript': 'al.scpt'}

# start mac before alarm
START_BEFORE_ALARM = 3

# at specified alarm time do
DO_ON_ALARM = "osascript %s" % files['alarmscript']

day_date_form = "%a, %x"
day_date_time_form = "%a, %x at %X"
date_time_form = "%x %X"

def get_param(scr, promt_string):
    scr.clear()
    scr.border(0)
    scr.addstr(2, 2, prompt_string)
    scr.refresh()
    input = scr.getstr(10, 10, 60)
    return input

def curses_init():
    scr = curses.initscr()
    curses.noecho()
    scr.keypad(True)
    return scr

def curses_exit(scr, msg=None):
    curses.nocbreak()
    scr.keypad(False)
    curses.echo()
    curses.endwin()
    if msg:
        print msg
    sys.exit(0)

def logo_screen(scr):
    scr.clear()
    scr.border(0)

    # TODO: schöner machen
    scr.addstr(2,2, " ▄▄▄█████▓▓█████  ██▀███   ██▀███   ▒█████   ██▀███      ")
    scr.addstr(3,2, " ▓  ██▒ ▓▒▓█   ▀ ▓██ ▒ ██▒▓██ ▒ ██▒▒██▒  ██▒▓██ ▒ ██▒    ")
    scr.addstr(4,2, " ▒ ▓██░ ▒░▒███   ▓██ ░▄█ ▒▓██ ░▄█ ▒▒██░  ██▒▓██ ░▄█ ▒    ")
    scr.addstr(5,2, " ░ ▓██▓ ░ ▒▓█  ▄ ▒██▀▀█▄  ▒██▀▀█▄  ▒██   ██░▒██▀▀█▄      ")
    scr.addstr(6,2, "   ▒██▒ ░ ░▒████▒░██▓ ▒██▒░██▓ ▒██▒░ ████▓▒░░██▓ ▒██▒    ")
    scr.addstr(7,2, "   ▒ ░░   ░░ ▒░ ░░ ▒▓ ░▒▓░░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒▓ ░▒▓░    ")
    scr.addstr(8,2, "     ░     ░ ░  ░  ░▒ ░ ▒░  ░▒ ░ ▒░  ░ ▒ ▒░   ░▒ ░ ▒░    ")
    scr.addstr(9,2, "   ░         ░     ░░   ░   ░░   ░ ░ ░ ░ ▒    ░░   ░     ")
    scr.addstr(10,2, "             ░  ░   ░        ░         ░ ░     ░         ")
    scr.addstr(11,2, "                                                         ")
    scr.addstr(12,2, "  █     █░ ▄▄▄       ██ ▄█▀▓█████      █    ██  ██▓███   ")
    scr.addstr(13,2, " ▓█░ █ ░█░▒████▄     ██▄█▒ ▓█   ▀      ██  ▓██▒▓██░  ██▒ ")
    scr.addstr(14,2, " ▒█░ █ ░█ ▒██  ▀█▄  ▓███▄░ ▒███       ▓██  ▒██░▓██░ ██▓▒ ")
    scr.addstr(15,2, " ░█░ █ ░█ ░██▄▄▄▄██ ▓██ █▄ ▒▓█  ▄     ▓▓█  ░██░▒██▄█▓▒ ▒ ")
    scr.addstr(16,2, " ░░██▒██▓  ▓█   ▓██▒▒██▒ █▄░▒████▒    ▒▒█████▓ ▒██▒ ░  ░ ")
    scr.addstr(17,2, " ░ ▓░▒ ▒   ▒▒   ▓▒█░▒ ▒▒ ▓▒░░ ▒░ ░    ░▒▓▒ ▒ ▒ ▒▓▒░ ░  ░ ")
    scr.addstr(18,2, "   ▒ ░ ░    ▒   ▒▒ ░░ ░▒ ▒░ ░ ░  ░    ░░▒░ ░ ░ ░▒ ░      ")
    scr.addstr(19,2, "   ░   ░    ░   ▒   ░ ░░ ░    ░        ░░░ ░ ░ ░░        ")
    scr.addstr(20,2, "     ░          ░  ░░  ░      ░  ░       ░               ")
    scr.addstr(21,2, "                                                         ")

    scr.refresh()
    curses.cbreak()
    scr.getkey()


def date_screen(scr):
    today = datetime.date.today()
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    scr.clear()
    scr.border(0)

    scr.addstr(2, 2, "Was willst du? Drücke ...")
    scr.addstr(4, 4, "Enter - Wecker für heute (%s)" % today.strftime(day_date_form))
    scr.addstr(6, 4, "t - Wecker für morgen (%s) " % tomorrow.strftime(day_date_form))
    scr.addstr(8, 4, "d - Alle Wecker ausschalten")
    scr.addstr(10, 4, "x - Abbrechen")

    alarms = list_all(mode='string').split('\n')
    if alarms and alarms != ['']:
        scr.addstr(13, 2, "Aktive Wecker:")
        i = 0
        for a in alarms:
            scr.addstr(15 + i, 4, a)
            i = i + 1

    scr.refresh()
    curses.cbreak()
    curses.noecho()

    inp = None

    while True:
        inp = scr.getkey()

        if inp == '\n':
            d = today
            break
        elif inp == 't':
            d = tomorrow
            break
        elif inp == 'd':
            let_me_sleep()
            d = date_screen(scr)
            break
            # curses_exit(scr, msg="Alle Wecker wurden entfernt")
        elif inp == 'x':
            curses_exit(scr)

    return d

def time_screen(scr, d):
    scr.clear()
    scr.border(0)
    curses.nocbreak()
    curses.echo()

    wrong_format = False
    in_past = False
    while True:
        scr.addstr(2, 2, "Um welche Uhrzeit willst du am %s geweckt werden? Format: hh:mm" % \
            d.strftime(day_date_form))

        editwin = curses.newwin(1,6, 4,3)

        if wrong_format:
            scr.addstr(6, 2, "Im Format hh:mm angeben!")
            wrong_format = False
        if in_past:
            scr.addstr(7, 2, "Diese Weckzeit ist in der Vergangenheit!")
            in_past = False
        scr.refresh()

        box = curses.textpad.Textbox(editwin)

        # Let the user edit until Ctrl-G is struck.
        box.edit()

        inp = box.gather()
        try:
            pattern = r"(?P<h>\d\d):(?P<m>\d\d)"
            val = re.search(pattern, inp)
            if not val:
                raise ValueError
            vals = val.groupdict()
            hour = int(vals['h'])
            mins = int(vals['m'])
            t = datetime.time(hour=hour, minute=mins)
        except ValueError:
            wrong_format = True
            continue

        wakedatetime = datetime.datetime.combine(d, t)
        now = datetime.datetime.now()

        if wakedatetime <= now:
            in_past = True
            continue
        else:
            break

    return wakedatetime


def set_alarm(scr, dt):
    # wake some time before alarm
    startdatetime = dt - datetime.timedelta(minutes=START_BEFORE_ALARM)

    # power on
    command_text = 'sudo pmset schedule wakeorpoweron "%s"' % startdatetime.strftime(date_time_form)
    schedule_command = shlex.split(command_text)
    p = subprocess.Popen(schedule_command, shell=False, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    for line in iter(p.stdout.readline, ''):
        # sys.stdout.write(line)
        scr.addstr(3, 3, line)

    # job for starting music
    at_text = 'at %s' % dt.strftime("%H:%M %x")
    at_command = shlex.split(at_text)

    print at_command
    p = subprocess.Popen(at_command, shell=False, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    o = p.communicate(DO_ON_ALARM)
    p.stdin.close()


def main(scr):
    scr = curses_init()
    logo_screen(scr)
    d = date_screen(scr)
    dt = time_screen(scr, d)
    set_alarm(scr, dt)
    curses_exit(scr, msg="Wecker gestellt auf %s!!!" % dt.strftime(day_date_time_form))

    # ohne passwort
    # ohne itnues
    # launchd atrun aktivieren


if __name__ == '__main__':
    curses.wrapper(main)
