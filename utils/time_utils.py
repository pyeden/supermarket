import time


def time_stamp_to_str(time_stamp):
    """
    时间戳转datetime类型字符串
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_stamp))


def str_to_time_stamp(time_str):
    """
    字符串时间类型转timestamp
    """
    if not time_str:
        return time_str
    return time.mktime(time.strptime(time_str, "%Y-%m-%d %H:%M:%S"))
