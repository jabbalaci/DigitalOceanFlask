#!/usr/bin/env python3
# encoding: utf-8

import os
from multiprocessing import cpu_count


def max_workers():
    return cpu_count() * 2 + 1


def main():
    cmd = "gunicorn -w {workers} -b {host}:{port} main:app --pid=gunicorn_manual.pid".format(
        workers=max_workers(), host='0.0.0.0', port=9000
    )
    print("#", cmd)
    os.system(cmd)

##############################################################################

if __name__ == "__main__":
    main()
