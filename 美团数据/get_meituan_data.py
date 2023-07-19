"""
采集美团-北京店铺数据

采集的店铺数据包括:
  - id 店铺id
  - title 店铺名
  - avgscore 平均评分
  - backCateName 店铺类型
  - areaname 商圈
  - avgprice 平均价格
  - comments 评论数量

同目录其他文件:
  - cookie - 保存你的 cookie 值
  - citys.json - 城市列表
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


class MeituanDataCollector:
    """
    美团店铺数据采集器
    """

    def __init__(self, city_id, cookie):
        self.search_api = "https://apimobile.meituan.com/group/v4/poi/pcsearch/" + str(city_id)
        self.headers = {
            "Host": "apimobile.meituan.com",
            "Origin": "https://sh.meituan.com",
            "Referer": "https://sh.meituan.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            "Cookie": cookie
        }

    def get_data(self, q, offset, limit) -> List[Dict]:
        """
        获取指定数量的店铺列表
        """
        params = self.__build_params(q, offset, limit)
        res = requests.get(self.search_api, params, headers=self.headers)
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
                "avgscore": item["avgscore"], # 平均评分
                "backCateName": item["backCateName"], # 店铺类型
                "areaname": item["areaname"], # 商圈
                "avgprice": item["avgprice"], # 平均价格
                "comments": item["comments"], # 评论数量
            })
        return result

    def get_all_data(self, q) -> List[Dict]:
        """
        获取所有店铺列表
        """
        data = []
        offset = 0
        limit = 34
        while True:
            _data = self.get_data(q, offset, limit)
            if not _data: break
            data.extend(_data)
            logging.info("%s门店 %s - %s 采集完成, 成功 %s", q, offset, offset + limit, len(_data))
            offset += limit
        logging.info("%s门店采集完成, 总数 %s", q, len(data))
        return data

    def chagne_city(self, city_id):
        self.search_api = "https://apimobile.meituan.com/group/v4/poi/pcsearch/" + str(city_id)

    def __build_params(self, q, offset=0, limit=32) -> Dict:
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

def load_cookie() -> str:
    cookie_file = os.path.join(os.path.dirname(__file__), "cookie")
    with open(cookie_file, "r") as f:
        return f.read()

def find_city_by_name(name: str) -> Dict:
    cookie_file = os.path.join(os.path.dirname(__file__), "citys.json")
    citys = []
    with open(cookie_file, "r", encoding="utf-8") as f:
        citys = json.load(f)
    for city in citys:
        if city["name"] == name:
            return city
    return {}

def load_city_id(cityname):
    city_info = find_city_by_name(cityname)
    if not city_info:
        logging.error("城市 %s 无效", cityname)
        quit()
    return city_info["id"]

if __name__ == "__main__":
    
    """
    更改 q 和 city 参数即可执行
    """

    q = "川菜"    # 查询店铺名称
    city = "北京" # 城市

    filename = f"{city}-{q}"
    city_id = load_city_id(city)
    cookie = load_cookie()

    collector = MeituanDataCollector(city_id, cookie)
    data = collector.get_all_data(q)

    save_to_csv(data, filename)