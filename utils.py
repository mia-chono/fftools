import re
import time


def clean_args(args: list[str]) -> list[str]:
    new_args = []
    for arg in args:
        if " " in arg:
            arg = '"' + arg + '"'
        new_args.append(arg.replace("\\", "/").replace("__COLON__", ":"))

    return new_args


def convert_str_time_to_sec(str_time: str) -> int:
    h, m, s = str_time.split(":")
    return int(h) * 3600 + int(m) * 60 + int(s)


def get_str_time_from_text(key: str, string: str, default: str) -> str:
    str_time = re.search(r'(?<={})\w+:\w+:\w+'.format(key), string)
    return convert_str_time_to_sec(str_time.group(0)) if time else default


def seconds_elapsed(start_time: float, current_time: float, total: float) -> float:
    if current_time != 0:
        time_elapsed = time.time() - start_time
        return total * time_elapsed / current_time - time_elapsed
    return 0
