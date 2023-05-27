"""
采集美团-北京店铺数据

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

HEADERS = {
    "Host": "apimobile.meituan.com",
    "Origin": "https://bj.meituan.com",
    "Referer": "https://bj.meituan.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Cookie": load_cookie(), # 使用您自己浏览器里的 Cookies
}

def build_params(q, offset=0, limit=32) -> Dict:
    """
    构建请求参数
    """
    return {
        "offset": offset,
        "limit": limit,
        "q": q,
        "cateId": -1,
        "sort": "rating"
    }

def get_data(q, offset, limit) -> List[Dict]:
    """
    获取指定数量的店铺列表
    """
    params = build_params(q, offset, limit)
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
            "id": item["id"], # id
            "title": item["title"], # 店铺名
            "avgscore": item["avgscore"], # 评分评分
            "backCateName": item["backCateName"], # 店铺类型
            "areaname": item["areaname"], # 商圈
            "avgprice": item["avgprice"], # 平均价格
            "comments": item["comments"], # 评论数量
        })
    return result


def get_all_data(q) -> List[Dict]:
    """
    获取所有店铺列表
    """
    data = []
    offset = 0
    limit = 34
    while True:
        _data = get_data(q, offset, limit)
        if not _data: break
        data.extend(_data)
        logging.info("%s门店 %s - %s 采集完成, 成功 %s", q, offset, offset + limit, len(_data))
        offset += limit
    logging.info("%s门店采集完成, 总数 %s", q, len(data))
    return data


def save_to_json(data, filename):
    """
    存储到 json 文件
    """
    json_filename = os.path.join(os.path.dirname(__file__), filename + ".json")
    with open(json_filename, 'w', encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info("数据已写入 %s", json_filename)


def save_to_csv(data, filename):
    """
    存储到 csv 文件
    """ 
    if not data: return
    csv_filename = os.path.join(os.path.dirname(__file__), filename + ".csv")
    with open(csv_filename, "w", encoding="utf-8", newline="") as f:
        header = data[0].keys()
        writer = csv.DictWriter(f, fieldnames=header, delimiter=",")
        writer.writeheader()
        for _ in data:
            writer.writerow(_)
        logging.info("数据已写入 %s", csv_filename)


if __name__ == "__main__":
    
    q = "火锅"    # 查询店铺名称
    filename = "北京-火锅"  # 存储文件名
    data = get_all_data(q)
    save_to_csv(data, filename)