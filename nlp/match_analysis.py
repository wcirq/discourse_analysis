# -*- coding: utf-8 -*- 
# @Time 2020/7/5 21:21
# @Author wcy
import re
from collections import Counter
from copy import deepcopy
from pprint import pprint

import jieba

from nlp.retrieve_analyze import DocumentSearch
from nlp.util import get_chinese_ratio


class MatchAnalysis(object):

    def __init__(self, document_search: DocumentSearch = None):
        if document_search is None:
            document_search = DocumentSearch()
        self.document_search = document_search

    def analysis(self, sentences, word, num, pattern=None):
        if pattern is None:
            pattern = re.compile("[ ](" + '|'.join([word]) + ")[ ]")
        else:
            pattern = re.compile(f"{pattern.pattern[:4]}{word}|{pattern.pattern[4:]}")
        is_chinese = get_chinese_ratio(word) > 0.5
        all_words = []
        for sentence in sentences:
            sentence_list = sentence[3:]
            for sentence in sentence_list:
                if is_chinese:
                    # jieba.add_word(word)
                    # s_cut = jieba.lcut(sentence)
                    # jieba.del_word(word)
                    s_cut = []
                    start = sentence.index(word)
                    end = start + len(word)
                    prefix_s = sentence[:start]
                    suffix_s = sentence[end:]
                    s_cut.extend(jieba.lcut(prefix_s))
                    s_cut.append(word)
                    s_cut.extend(jieba.lcut(suffix_s))
                else:
                    s_cut = []
                    phrase_iterator = pattern.finditer(f" {sentence} ")
                    last_end = 0
                    for phrase_sre in phrase_iterator:
                        start = phrase_sre.start()
                        end = phrase_sre.end()
                        phrase_prefix_str = sentence[last_end:start]
                        phrase_prefix = [w for w in phrase_prefix_str.split(" ") if w.strip() != ""]
                        s_cut.extend(phrase_prefix)
                        phrase = phrase_sre.group()
                        phrase = phrase.strip()
                        s_cut.append(phrase)
                        last_end = end
                    phrase_suffix_str = sentence[last_end:]
                    phrase_suffix = [w for w in phrase_suffix_str.split(" ") if w.strip() != ""]
                    s_cut.extend(phrase_suffix)
                if not word in s_cut:
                    continue
                s_cut = [s for s in s_cut if s.strip() != ""]
                index = s_cut.index(word)
                s = max(index - num, 0)
                e = index + num
                words = s_cut[s:e]
                words.remove(word)
                all_words.extend(words)
        dict_word_count = Counter(all_words)
        dict_word_count = {k: v for k, v in dict_word_count.items() if k != ""}
        dic_word_count_sort = sorted(dict_word_count.items(), key=lambda d: d[1], reverse=False)
        return dic_word_count_sort

    def match(self, word, num=5, sentences=None, document_search=None, pattern=None):
        """
        word搭配的词
        :param word:
        :param num: 前后各num个词范围内的高频词词表, 默认为5
        :param sentences:
        :return:
        """
        if pattern is None:
            pattern = re.compile("[ ](" + '|'.join([]) + ")[ ]")
        if document_search is None:
            document_search = self.document_search
        if sentences is None:
            # state, word = document_search.auto_correct_sentence(word)
            sentences_index = document_search.search(word)
            sentences = document_search.get_sentence(sentences_index)
            sentences = sentences.get(word, [])
        result = self.analysis(sentences, word, num, pattern)
        return result


if __name__ == '__main__':
    word = "公司"
    match_analysis = MatchAnalysis()
    doc = DocumentSearch()
    result = doc.search(word)
    sentences = doc.get_sentence(result)
    result = match_analysis.match(word, sentences=sentences[word])
    pprint(result)
