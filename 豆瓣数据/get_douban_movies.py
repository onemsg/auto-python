"""
获取豆瓣电影数据

网页: https://movie.douban.com/explore

@Author: kvimsg@livve.com
@Since: 2023-06
"""

import os
import logging

LOGGER_FORMAT = '%(asctime)s %(levelname)s - %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, level='INFO')


def load_cookie() -> str:
    cookie_file = os.path.join(os.path.dirname(__file__), "cookie")
    with open(cookie_file, "r") as f:
        return f.read()

MOVIES_API = "https://m.douban.com/rexxar/api/v2/movie/recommend"
COOKIES = load_cookie()

def build_params():
    return {
        
    }

