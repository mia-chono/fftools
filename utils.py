import datetime
import re
import sys
import time


def clean_args(args: list[str]) -> list[str]:
    """
    replace invalid characters in the arguments
    :param args:
    :return:
    """
    new_args = []
    for arg in args:
        if " " in arg:
            arg = '"' + arg + '"'
        new_args.append(arg.replace("\\", "/").replace("__COLON__", ":"))

    return new_args


def convert_str_time_to_sec(str_time: str) -> float:
    """
    convert a string time `00:00:01` to seconds `1`
    :param str_time:
    :return: total of seconds
    """
    h, m, s = str_time.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def get_str_time_from_text(key: str, string: str, default: float) -> float:
    """
    retrieves the time string from contains `00:00:00` and returns the total of the seconds
    :param key: key to search in the string
    :param string: text to find the time
    :param default: default value if the key is not found
    :return: total of seconds
    """
    str_time = re.search(r'(?<={})\w+:\w+:\w+'.format(key), string)
    return convert_str_time_to_sec(str_time.group(0)) if str_time else default


def seconds_elapsed(start_time: float, current_time: float, total: float) -> float:
    """
    calculate the seconds elapsed since the start_time
    :param start_time:
    :param current_time:
    :param total:
    :return: elapsed seconds
    """
    if current_time != 0:
        time_elapsed = time.time() - start_time
        return total * time_elapsed / current_time - time_elapsed
    return 0


def basic_monitor(process_cmd_line, duration, downloaded_time, remaining_time, process):
    """
    example of the visual: `[0:23:03](5%) 0:01:24 left [#####-----------------------------------------------------------------------------------------------]`
    :param process_cmd_line: process command line
    :param duration: duration of the video
    :param downloaded_time: current time of transcoded video
    :param remaining_time: seconds left to finish the video process
    :param process: subprocess object
    :return: None
    """
    percent = round(downloaded_time / duration * 100)
    sys.stdout.write(
        "\r[{}]({}%) {} left [{}{}]".format(
            datetime.timedelta(seconds=int(duration)),
            percent,
            datetime.timedelta(seconds=int(remaining_time)),
            '#' * percent,
            '-' * (100 - percent)
        )
    )
    sys.stdout.flush()
