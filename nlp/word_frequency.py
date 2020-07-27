# -*- coding: utf-8 -*- 
# @Time 2020/6/1 10:34
# @Author wcy
import re  # 正则表达式库
import collections  # 词频统计库
import numpy as np  # numpy数据处理库
import jieba  # 结巴分词
import wordcloud  # 词云展示库
from PIL import Image  # 图像处理库
import matplotlib.pyplot as plt  # 图像展示库

from nlp.new_words import NewWords
from nlp.util import pretreatment_texts, get_chinese_ratio


def test():
    # 读取文件
    fn = open('data.txt', encoding="utf-8")  # 打开文件
    string_data = fn.read()  # 读出整个文件
    fn.close()  # 关闭文件

    # 文本预处理
    pattern = re.compile(u'\t|\n|\.|-|:|;|\)|\(|\?|《|》|\[|\]|"')  # 定义正则表达式匹配模式
    string_data = re.sub(pattern, '', string_data)  # 将符合模式的字符去除

    # 文本分词
    seg_list_exact = jieba.cut(string_data, cut_all=False)  # 精确模式分词
    object_list = []
    remove_words = [u'的', u'，', u'和', u'是', u'随着', u'对于', u'对', u'等', u'能', u'都', u'。', u' ', u'、', u'中', u'在', u'了',
                    u'通常', u'如果', u'我们', u'需要']  # 自定义去除词库

    for word in seg_list_exact:  # 循环读出每个分词
        if word not in remove_words:  # 如果不在去除词库中
            object_list.append(word)  # 分词追加到列表

    # 词频统计
    word_counts = collections.Counter(object_list)  # 对分词做词频统计
    word_counts_top10 = word_counts.most_common(10)  # 获取前10最高频的词
    print(word_counts_top10)  # 输出检查

    # 词频展示
    mask = np.array(Image.open('wordcloud.jpg'))  # 定义词频背景
    wc = wordcloud.WordCloud(
        font_path='C:/Windows/Fonts/simhei.ttf',  # 设置字体格式
        mask=mask,  # 设置背景图
        max_words=400,  # 最多显示词数
        max_font_size=100  # 字体最大值
    )

    wc.generate_from_frequencies(word_counts)  # 从字典生成词云
    image_colors = wordcloud.ImageColorGenerator(mask)  # 从背景图建立颜色方案
    wc.recolor(color_func=image_colors)  # 将词云颜色设置为背景图方案
    plt.imshow(wc)  # 显示词云
    plt.axis('off')  # 关闭坐标轴
    plt.show()  # 显示图像


def analyze_word(texts):
    # 文本预处理
    # pattern = re.compile(u'―|、|\r|\t|\n|\.|-|:|;|\)|\(|\?|《|》|\[|\]|"|,|，| |。|？|；|#|“|”|％|…|．|【|】|：')  # 定义正则表达式匹配模式
    # string_data = re.sub(pattern, '', text)  # 将符合模式的字符去除
    string_data = pretreatment_texts(texts)

    # 文本分词
    if get_chinese_ratio(string_data) > 0.5:
        seg_list_exact = jieba.lcut(string_data, cut_all=False)  # 精确模式分词
    else:
        seg_list_exact = re.split(" ", string_data)

    # 词频统计
    word_counts = collections.Counter(seg_list_exact)  # 对分词做词频统计
    return dict(word_counts)


def analyze_phrase(texts, show=True):
    # 文本预处理
    # pattern = re.compile(u'―|、|\r|\t|\n|\.|-|:|;|\)|\(|\?|《|》|\[|\]|"|,|，| |。|？|；|#|“|”|％|…|．|【|】|：')  # 定义正则表达式匹配模式
    # texts = [re.sub(pattern, '', text) for text in texts]  # 将符合模式的字符去除
    # score = get_chinese_ratio(texts)
    texts = pretreatment_texts(texts)
    nw = NewWords(filter_cond=10, filter_free=2)
    nw.add_text3(texts, show)
    vocab = {k: v[0] for k, v in nw.vocab.items() if v[0] > 1}
    if len(vocab.keys()) < 1:
        vocab = {k: v[0] for k, v in nw.vocab.items()}
    return vocab


def analyze(text):
    word_counts = analyze_word(text)
    word_counts_sorted = sorted(word_counts.items(), key=lambda d: d[1], reverse=True)
    datas = re.split('[,。.，！!?？；;]', text)
    wphrase_counts = analyze_phrase(datas)
    wphrase_counts_sorted = sorted(wphrase_counts.items(), key=lambda d: d[1], reverse=True)
    return word_counts, wphrase_counts


if __name__ == '__main__':
    with open("data.txt", "r", encoding="utf-8") as f:
        datas = f.readlines()
    datas = "\n".join(datas)
    # test()
    analyze(datas)
