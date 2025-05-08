import re


def is_valid_url(url):
    # URL 的正则表达式模式
    url_pattern = re.compile(r'^(https?|ftp)://[^\s/$.?#].\S*$')
    return url and url_pattern.match(url)
