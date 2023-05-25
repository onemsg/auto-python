"""
采集美团上北京-星巴克店铺数据

代码具有通用性, 更换 q 参数即可采集其他的店铺数据,比如 q="奶茶"

@Author kvimsg@live.com
@Since 2023-02
"""

import requests
import logging
import json
from typing import List, Dict
import csv
import os

LOGGER_FORMAT = '%(asctime)s %(levelname)s - %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, level='INFO')

def load_cookie() -> str:
    cookie_file = os.path.join(os.path.dirname(__file__), "cookie")
    with open(cookie_file, "r") as f:
        return f.read()

SEARCH_API = "https://apimobile.meituan.com/group/v4/poi/pcsearch/1"
SEARCH_PARAMS = {
    "limit": 32,
    "offset": 0,
    "cateId": -1,
    "q": "星巴克",
    "sort": "default"
}

# TODO: 使用您自己浏览器里的 Cookies
COOKIES = load_cookie()

HEADERS = {
    "Host": "apimobile.meituan.com",
    "Origin": "https://bj.meituan.com",
    "Referer": "https://bj.meituan.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Cookie": COOKIES,
}

def build_params(offset=0, limit=50, q="星巴克") -> Dict:
    """
    构建请求参数
    """
    params = SEARCH_PARAMS.copy()
    params.update(offset=offset, limit=limit, q=q)
    return params

def get_count(q="星巴克") -> int:
    """
    获取店铺数量
    """
    params = build_params(0, 5, q=q)
    res = requests.get(SEARCH_API, params, headers=HEADERS)
    try:
        res.raise_for_status()
    except requests.HTTPError as e:
        logging.warning("Get %s failed", res.url, exc_info=e)
        return 0
    return res.json()['data']['totalCount']

def get_data(offset, limit, q="星巴克") -> List[Dict]:
    """
    获取店铺列表
    """
    params = build_params(offset, limit, q=q)
    res = requests.get(SEARCH_API, params, headers=HEADERS)
    try:
        res.raise_for_status()
    except requests.HTTPError as e:
        logging.warn("Get %s failed", res.url, exc_info=e)
        return []
    search_result = res.json()['data']['searchResult']
    result = []
    for item in search_result:
        result.append({
            "id": item["id"],
            "title": item["title"],
            "avgscore": item["avgscore"],
            "backCateName": item["backCateName"],
            "areaname": item["areaname"]
        })
    return result


if __name__ == "__main__":
    
    q = "星巴克"    # 查询店铺名称
    filename = "beijing-starbucks"  # 存储文件名

    count = get_count(q=q)
    logging.info("查询到%s门店 %s", q, count)
    limit = 50
    data = []
    for offset in range(0, count, limit):
        _data = get_data(offset, limit,q=q)
        data.extend(_data)
        logging.info("%s门店 %s - %s 采集完成, 成功 %s", q, offset, offset + limit, len(_data))
    logging.info("%s门店采集完成, 总数 %s", q, len(data))

    # 存储为 json 格式
    json_filename = filename + ".json"
    with open(json_filename, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info("数据已写入 %s", json_filename)

    # 存储为 csv 格式
    csv_filename = filename + ".csv"
    with open(csv_filename, "w", encoding="utf-8", newline="") as f:
        header = "id title avgscore areaname backCateName".split()
        writer = csv.DictWriter(f, fieldnames=header, delimiter=",")
        writer.writeheader()
        for _ in data:
            writer.writerow(_)
        logging.info("数据已写入 %s", csv_filename)