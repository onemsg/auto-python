"""
采集豆瓣短评

示例网页 - https://movie.douban.com/subject/26634250/comments?status=P

@Author kvimsg@live.com
@Since 2023-06
"""

import requests
import logging
import json
from typing import List, Dict
import csv
import os
from bs4 import BeautifulSoup

LOGGER_FORMAT = '%(asctime)s %(levelname)s - %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, level='INFO')


COMMON_HEADERS = {
    "Host": "movie.douban.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.43",
    "Cookie": "",
}

def get_all_comments(id: int) -> List[str]:
    comments = []
    for i in range(0, 1000, 20):
        sub_comments = get_comments(id, i)
        if not sub_comments: break
        comments.extend(sub_comments)
        logging.info("已采集电影 %s 短评 %s-%s", id, i, i+20)
    logging.info("采集电影 %s 短评完成, 总计 %s", id, len(comments))
    return comments


def get_comments(id: int, start: int=0, limit: int=20) -> List[str]:
    url = f"https://movie.douban.com/subject/{id}/comments"
    params = {
        "start": start,
        "limit": limit,
        "status": "P",
        "sort": "new_score"
    }
    res = requests.get(url, params=params, headers=COMMON_HEADERS)
    if res.status_code == 404:
        return []
    res.raise_for_status()
    bs = BeautifulSoup(res.content)
    doms = bs.select("#comments > .comment-item")
    texts = []
    for dom in doms:
        text = dom.select_one("div.comment > p > span").text
        texts.append(text)
    return texts

def build_path(filename):
    return os.path.join(os.path.dirname(__file__), filename)

def load_cookie(file="cookie") -> str:
    with open(build_path(file), "r") as f:
        return f.read()
    

if __name__ == "__main__":

    movie_id = 26634250
    COMMON_HEADERS["Cookie"] = load_cookie("douban_cookie")
    filename = "变形金刚_超能勇士崛起_豆瓣短评.txt"

    comments = get_all_comments(movie_id)

    with open(build_path(filename), "w", encoding="UTF-8") as f:
        f.writelines(comments)
        logging.info("写入文件 %s", filename)

