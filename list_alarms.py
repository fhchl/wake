import subprocess as sp
import shlex
import re

def list_it(q_command, regex):
    out = sp.check_output(shlex.split(q_command)).split('\n')
    out.remove('')
    dts = []
    for o in out:
        val = re.search(regex, o)
        if val:
            vals = val.groupdict()
            dts.append(vals['dt'])

    return dts

def list_all(mode='p', list_wakeups=False):
    alarms = list_it("atq", r"\d+\s*(?P<dt>.*)")
    wakeups = list_it("pmset -g sched", r".*wakeorpoweron at (?P<dt>.*)")

    if mode=='p':
        for a in alarms:
            print "Alarm at", a
        if list_wakeups:
            for w in wakeups:
                print "Wakeup at", w
        return None
    else:
        s = ""
        for a in alarms:
            s = s + "Alarm at " + a + "\n"
        if list_wakeups:
            for w in wakeups:
                s = s + "Wakeup at " + w + "\n"
        return s[:-1]

if __name__ == '__main__':
    list_all(list_wakeups=True)