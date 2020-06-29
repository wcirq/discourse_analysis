# -*- coding: utf-8 -*- 
# @Time 2020/6/28 15:33
# @Author wcy


"""python提取文本的tfidf特征"""

import math
from collections import Counter

# 1.语料库
corpus = [
    'this is the first document',
    'this is the second second document',
    'and the third one',
    'is this the first document'
]

# 2.对语料进行分词
word_list = []
for i in range(len(corpus)):
    word_list.append(corpus[i].split(' '))
print('2-->', word_list)

# 3.统计词频
countlist = []
for i in range(len(word_list)):
    count = Counter(word_list[i])
    countlist.append(count)
print('3词频-->', countlist)


# 4.定义计算tfidf公式的函数
# count[word]可以得到每个单词的词频， sum(count.values())得到整个句子的单词总数
def tf(word, count):
    return count[word] / sum(count.values())


# 统计的是含有该单词的句子数
def n_containing(word, count_list):
    return sum(1 for count in count_list if word in count)


# len(count_list)是指句子的总数，n_containing(word, count_list)是指含有该单词的句子的总数，加1是为了防止分母为0
def idf(word, count_list):
    return math.log(len(count_list) / (1 + n_containing(word, count_list)))


# 将tf和idf相乘
def tfidf(word, count, count_list):
    return tf(word, count) * idf(word, count_list)


all_dict = {}
for counte in countlist:
    counter = dict(counte)
    for k, v in counter.items():
        try:
            all_dict[k] += v
        except:
            all_dict[k] = v
print('merge-->', all_dict)

with open('tf.txt', 'w+') as tfin, open('idf.txt', 'w+') as idfin:
    for k in all_dict.keys():
        # k_tf = tf(k, all_dict)
        tfin.write(k + ' ' + str(all_dict[k]) + '\n')
        k_idf = idf(k, countlist)
        idfin.write(k + ' ' + str(k_idf) + '\n')