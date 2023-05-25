"""
下载微博用户相册

示例页面 https://weibo.com/u/5372556014?tabtype=album

@Author kvimsg@live.com
@Since 2023-05
"""
import requests
import logging
import os
LOGGER_FORMAT = '%(asctime)s %(levelname)s - %(message)s'
logging.basicConfig(format=LOGGER_FORMAT, level='INFO')
from typing import Dict, List

headers = {
    "Cookie": ""
}

def fetch_picture_urls(uid: int, sinceid: str="0") -> Dict:
    """
    获取微博用户的相册 url 列表
    """
    # 构建用户相册 api
    url = f"https://weibo.com/ajax/profile/getImageWall?uid={uid}&sinceid={sinceid}"
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    data = res.json()
    # 图片url列表
    picture_urls = []
    # 遍历响应数据，构造图片 url
    for item in data["data"]["list"]:
        # 如果是图片而不是视频或gif动图
        if item["type"] == "pic":
            pic_url = f"https://wx4.sinaimg.cn/mw2000/{item['pid']}.jpg"
            picture_urls.append(pic_url)
    return {
        "picture_urls": picture_urls,
        "sinceid": data["data"]["since_id"]
    }


def save_pictures(picture_urls: List[str], path: str):
    """
    下载图片
    """

    # 1. 构建文件夹
    if not os.path.exists(path):
        os.mkdir(path)
    # 2. 遍历图片url列表并保存
    for i, pic_url in enumerate(picture_urls):
        res = requests.get(pic_url)
        filename = f"{i}.jpg"
        filepath = os.path.join(path, filename)
        with open(filepath, "wb") as f:
            f.write(res.content)
        logging.info("%s 已下载保存", filepath)
    logging.info("图片下载完成，总数量：%s", len(picture_urls))

if __name__ == "__main__":
    
    # 微博用户id
    uid = 1640016932
    name = "张雨绮"

    picture_urls = []
    sinceid = "0"
    # 获取 10 批相册 urls
    # 当然可以自由更改批次
    for i in range(10):
        data = fetch_picture_urls(uid, sinceid)
        picture_urls.extend(data["picture_urls"])
        sinceid = data["sinceid"]
    
    # 下载保存图片
    save_pictures(picture_urls, name)