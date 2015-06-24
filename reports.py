#!/usr/bin/python
"""
Usage:
    reports.py (<file>)

"""

import sys
import os
import tty
import termios
import subprocess

REPORT_FILE = 'reports.txt'
TEMP_SCRIPT_FILE = '/tmp/.ledgerscript.sh'
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
COLOR_BLUE = '\\e[36m'
COLOR_RESET = '\\e[0m'
CMD_EXPL_COLOR = COLOR_BLUE


def getchar():
    """
    Get a single character from stdin.
    """
    # from http://code.activestate.com/recipes/134892/
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def makescript(expl, cmds):
    """
    Make a helper script which eases usage of the ecosystem.
    """
    out = ""
    out += '#!/bin/bash\n'
    out += 'shopt -s expand_aliases\n'
    out += '. {}/alias\n'.format(THIS_DIR)
    out += 'echo -e "{}{}{}"\n'.format(CMD_EXPL_COLOR, expl, COLOR_RESET)
    out += 'echo ""\n'
    for cmd in cmds:
        s = cmd.replace('"', '\\"').replace('`', '\\`').replace('$', '\\$')
        out += 'echo -e "{}\$ {}{}"\n'.format(CMD_EXPL_COLOR, s, COLOR_RESET)
        out += '{}\n'.format(cmd)
    with open(TEMP_SCRIPT_FILE, 'w') as fh:
        fh.write(out)
    os.chmod(TEMP_SCRIPT_FILE, 0777)


def show((expl, cmds)):
    """
    Show one report from the report file.
    """
    makescript(expl, cmds)
    os.system('clear')
    subprocess.call(TEMP_SCRIPT_FILE, shell=True)


def main(argv=None):
    if (argv is not None and len(argv) > 1):
        filename = argv[1]
    else:
        filename = REPORT_FILE

    reports = []
    with open(filename, 'r') as fh:
        expl = ''
        cmds = []
        lines = fh.readlines()[2:]  # skip header lines
        for i, line in enumerate(lines):
            if (line.startswith('#')):
                expl += line
            elif (not line.startswith('\n')):
                # consider everything else till a blank line as commands
                cmds.append(line.strip())

            if (cmds and lines[i + 1].startswith('\n')):
                reports.append((expl.strip(), cmds))
                cmds = []
                expl = ''

    i = 0
    while True:
        show(reports[i])
        print('')
        print('[#{}] h = previous report, l = next report, q = quit [h/l/q] ?'.
              format(i + 1))
        action = getchar()
        # TODO: get char of cursor left/up/right/down
        if (action == 'h'):
            i = i - 1 if i > 0 else len(reports) - 1
        elif (action == 'l'):
            i = i + 1 if i < len(reports) - 1 else 0
        elif (action == 'q'):
            break

if __name__ == '__main__':
    main(sys.argv)
