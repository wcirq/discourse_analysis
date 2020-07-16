# -*- coding: utf-8 -*- 
# @Time 2020/6/28 15:41
# @Author wcy
import os

import chardet

from nlp.util import log_likelihood
from nlp.word_frequency import analyze_word, analyze_phrase


def extract_word_frequency(corpus, min_char_num=2):
    if isinstance(corpus, list):
        corpus = " ".join(corpus)
    result = analyze_word(corpus)
    # 去掉length<2的词
    result = {k: v for k, v in result.items() if len(k) >= min_char_num}
    return result


def extract_phrase_frequency(corpus):
    # if isinstance(corpus, list):
    #     corpus = " ".join(corpus)
    result = analyze_phrase(corpus)
    return result


def get_log_likelihood_ratio(word_freq1, word_freq2):
    """计算对数似然率"""
    results = {}
    keys1 = list(word_freq1.keys())
    keys2 = list(word_freq2.keys())
    union = list(set(keys1).union(set(keys2)))  # 并集
    intersection = list(set(keys1).intersection(set(keys2)))  # 交集
    difference_set = list(set(keys2).difference(set(keys1)))  # 差集 keys2中有而keys1中没有的
    vocabularys = intersection
    for vocabulary in vocabularys:
        if not vocabulary in word_freq1.keys():
            word_freq1[vocabulary] = 0
        if not vocabulary in word_freq2.keys():
            word_freq2[vocabulary] = 0
        results[vocabulary] = log_likelihood(word_freq1[vocabulary], word_freq2[vocabulary])
    # 按从大到小排序
    results_sort = sorted(results.items(), key=lambda d: d[1], reverse=True)
    return results_sort


def analyze_word_likelihood(corpus1, corpus2):
    """
    分析两个文本库词语的对数似然率
    :param corpus1: 文本库1 ["文章1", "文章2", ...]
    :param corpus2: 文本库2 ["文章1", "文章2", ...]
    :return: 各词的对数似然率
    """
    corpus1_word_freq = extract_word_frequency(corpus1)
    corpus2_word_freq = extract_word_frequency(corpus2)
    # corpus1_word_freq = sorted(corpus1_word_freq.items(), key=lambda d: d[1], reverse=True)
    # corpus2_word_freq = sorted(corpus2_word_freq.items(), key=lambda d: d[1], reverse=True)
    word_likelihood_sort = get_log_likelihood_ratio(corpus1_word_freq, corpus2_word_freq)
    return word_likelihood_sort


def analyze_phrase_likelihood(corpus1, corpus2):
    """
    分析两个文本库短语的对数似然率
    :param corpus1: 文本库1 like ["文章1", "文章2", ...]
    :param corpus2: 文本库2 like ["文章1", "文章2", ...]
    :return: 各短语的对数似然率
    """
    corpus1_phrase_freq = extract_phrase_frequency(corpus1)
    corpus2_phrase_freq = extract_phrase_frequency(corpus2)
    # corpus1_phrase_freq = sorted(corpus1_phrase_freq.items(), key=lambda d: d[1], reverse=True)
    # corpus2_phrase_freq = sorted(corpus2_phrase_freq.items(), key=lambda d: d[1], reverse=True)
    phrase_likelihood_sort = get_log_likelihood_ratio(corpus1_phrase_freq, corpus2_phrase_freq)
    return phrase_likelihood_sort


def read_corpus_file(corpus_path, max_num=500):
    """
    根据文本库根目录读取该路径下所有文本
    :param corpus_path: 文本库根目录
    :param max_num: 最多读取多少篇文章
    :return: 文本库数据 like ["文章1", "文章2", ...]
    """
    file_list = os.listdir(corpus_path)
    results = []
    for file_name in file_list[:]:
        document_path = os.path.join(corpus_path, file_name)
        bytes = min(2048, os.path.getsize(document_path))
        raw = open(document_path, 'rb').read(bytes)
        result = chardet.detect(raw)
        encoding = result['encoding']
        with open(document_path, "r", encoding=encoding) as f:
            try:
                result = f.readlines()
            except Exception as e:
                print(document_path)
                continue
            result = [line.strip('\n') for line in result]
            result = "".join(result)
            results.append(result)
    return results


if __name__ == '__main__':
    # path1 = "../static/corpus1"
    path1 = "E:\\DATA\\领域数据\\C3-Art"
    # path2 = "../static/corpus2"
    path2 = "E:\\DATA\\领域数据\\C39-Sports"
    corpus1 = read_corpus_file(path1)
    corpus2 = read_corpus_file(path2)
    word_likelihood_sort = analyze_word_likelihood(corpus1, corpus2)
    phrase_likelihood_sort = analyze_phrase_likelihood(corpus1, corpus2)
    print()
