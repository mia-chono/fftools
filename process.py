"""
based on ffmpeg_streaming.process
"""

import subprocess
import threading
import logging
import time
from typing import Tuple

from utils import get_str_time_from_text, seconds_elapsed


class Process(object):
    out = None
    err = None

    def __init__(self, bin_path, commands: str, monitor: callable = None, **options) -> None:
        self.is_monitor = False
        self.timeout = options.pop('timeout', None)
        default_proc_opts = {
            'stdin': None,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.STDOUT,
            'universal_newlines': False
        }
        default_proc_opts.update(options)
        options.update(default_proc_opts)
        if callable(monitor):
            self.is_monitor = True
            options.update({
                'stdin': subprocess.PIPE,
                'universal_newlines': True
            })

        logging.info("[PROCESS] open process: {}".format(bin_path))
        self.bin_path = bin_path
        self.monitor = monitor
        self.process = subprocess.Popen("{} {}".format(bin_path, commands), **options)

    def __enter__(self) -> 'Process':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.process.kill()

    def _monitor(self) -> None:
        logging.info("[PROCESS][MONITOR] start monitor")
        duration = 1
        total_downloaded_time = 0
        log = []
        start_time = time.time()

        while True:
            line = self.process.stdout.readline().strip()
            if line == '' and self.process.poll() is not None:
                break

            logging.info("[PROCESS][MONITOR] {}".format(line))
            log += [line]

            if callable(self.monitor):
                duration = float(get_str_time_from_text('Duration: ', line, duration))
                total_downloaded_time = float(get_str_time_from_text('time=', line, total_downloaded_time))
                self.monitor(line, duration, total_downloaded_time, seconds_elapsed(start_time, total_downloaded_time, duration), self.process)

        Process.out = log

    def _thread_monitor(self) -> None:
        thread = threading.Thread(target=self._monitor)
        logging.info("[PROCESS][THREAD] start thread")
        thread.start()

        thread.join(self.timeout)
        if thread.is_alive():
            self.process.terminate()
            thread.join()
            error = 'Timeout! exceeded the timeout of {} seconds.'.format(str(self.timeout))
            logging.error(error)
            raise RuntimeError(error)

    def run(self) -> Tuple[str, str]:
        if self.is_monitor:
            self._thread_monitor()
        else:
            Process.out, Process.err = self.process.communicate(None, self.timeout)

        if self.process.poll():
            error = str(Process.err) if Process.err else str(Process.out)
            logging.error('[PROCESS] execution failed:\n{}'.format(error))
            raise RuntimeError('[PROCESS] execution failed: ', error)

        logging.info("[PROCESS] command successfully executed")

        return Process.out, Process.err
