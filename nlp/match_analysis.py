# -*- coding: utf-8 -*- 
# @Time 2020/7/5 21:21
# @Author wcy
from collections import Counter
from pprint import pprint

import jieba

from nlp.retrieve_analyze import DocumentSearch


class MatchAnalysis(object):

    def __init__(self, document_search:DocumentSearch=None):
        if document_search is None:
            document_search = DocumentSearch()
        self.document_search = document_search

    def analysis(self, sentences, word, num):
        all_words = []
        for sentence in sentences:
            sentence_list = sentence[3:]
            for s in sentence_list:
                jieba.add_word(word)
                s_cut = jieba.lcut(s)
                jieba.del_word(word)
                if not word in s_cut:
                    continue
                index = s_cut.index(word)
                s = max(index-num, 0)
                e = index+num
                words = s_cut[s:e]
                words.remove(word)
                all_words.extend(words)
        dic_word_count = Counter(all_words)
        dic_word_count_sort = sorted(dic_word_count.items(), key=lambda d: d[1], reverse=False)
        return dic_word_count_sort

    def match(self, word, num=5, sentences=None, document_search=None):
        """
        word搭配的词
        :param word:
        :param num: 前后各num个词范围内的高频词词表, 默认为5
        :param sentences:
        :return:
        """
        if document_search is None:
            document_search = self.document_search
        if sentences is None:
            # state, word = document_search.auto_correct_sentence(word)
            sentences_index = document_search.search(word)
            sentences = document_search.get_sentence(sentences_index)
            sentences = sentences.get(word, [])
        result = self.analysis(sentences, word, num)
        return result


if __name__ == '__main__':
    word = "公司"
    match_analysis = MatchAnalysis()
    doc = DocumentSearch()
    result = doc.search(word)
    sentences = doc.get_sentence(result)
    result = match_analysis.match(word, sentences=sentences[word])
    pprint(result)