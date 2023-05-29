"""
生成小美人鱼影评词云图
"""
from os import path
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import os
import jieba

from collections import Counter

from wordcloud import WordCloud, STOPWORDS

def build_path(filename: str) -> str:
    return os.path.join(path.dirname(__file__), filename)


def process_text(text: str) -> dict:
    """
    中文分词、去停用词、统计词频
    """
    # 中文分词
    words = jieba.cut(text, cut_all=False)
    stopwords = set()
    with open(build_path("stop_words.txt"), encoding="utf-8") as f:
        stopwords = set(f.read().splitlines())

    print(list(stopwords)[:15])

    words = [word for word in words if word not in stopwords and not word.isspace()]
    return dict(Counter(words))


# 读取文本
text = ""
with open(build_path("小美人鱼_豆瓣影评.txt") , "r", encoding="utf-8") as f:
    text = f.read()

# 统计词频
word_counter = process_text(text)

alice_mask = np.array(Image.open(build_path("alice_mask.png")))

wc = WordCloud(font_path=build_path("fonts/SourceHanSerifK-Light.otf"), background_color="white", max_words=2000, mask=alice_mask,
    contour_width=3, contour_color='steelblue')

# 生成词云图
wc.generate_from_frequencies(word_counter)

# 保存图片
wc.to_file(build_path("小美人鱼_豆瓣影评_词云图.png"))