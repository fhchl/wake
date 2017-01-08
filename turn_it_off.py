import subprocess as sp
import shlex
import re

def get_ids(command, regex):
    out = sp.check_output(shlex.split(command)).split('\n')
    out.remove('')
    ids = []
    for o in out:
        val = re.search(regex, o)
        if val:
            vals = val.groupdict()
            ids.append(vals['id'])

    return ids

def remove_jobs(q_command, rm_command, regex, i_const=None):
    # get all ids from pmset
    ids = get_ids(q_command, regex)

    # remove them
    for i in ids:
        if i_const:
            i = i_const
        command = rm_command + " " + i
        print command
        sp.check_call(shlex.split(command))

def let_me_sleep():
    remove_jobs("atq", "atrm", r"(?P<id>\d+)\s.*")
    remove_jobs("pmset -g sched",
        "sudo pmset schedule cancel",
        r"\s*\[(?P<id>\d+)\]\s.*", i_const='0')

if __name__ == '__main__':
    let_me_sleep()