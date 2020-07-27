# -*- coding: utf-8 -*- 
# @Time 2020/6/29 12:17
# @Author wcy
import os
import pickle
import re
from _tkinter import _flatten
from collections import Counter
from copy import deepcopy
from pprint import pprint

import chardet
import jieba
from tqdm import tqdm

from common.logger_config import logger
from config import INDEX_ROOT_PATH, PHRASES_PATH, STATIC_PATH
from nlp import correct
from nlp.util import pretreatment_texts, get_chinese_ratio
from nlp.word_frequency import analyze_phrase

tokenizer = jieba.Tokenizer(dictionary=jieba.DEFAULT_DICT)


class DocumentSearch():

    def __init__(self, reset_index=False):
        self.version = 1  # 索引版本
        self.reset_index = reset_index  # 是否重置索引
        self.index_path = os.path.join(INDEX_ROOT_PATH, f"{self.version}.dict")
        self.index_time = 0
        self.root = STATIC_PATH
        self.index = {}  # 倒排索引
        self.participles = []  # 加入jieba用于分词的短语
        self.init_index()

    def read_file(self, document_path):
        try:
            bytes = min(2048, os.path.getsize(document_path))
            raw = open(document_path, 'rb').read(bytes)
            result = chardet.detect(raw)
            encoding = result['encoding']
            ncoding = "gbk" if encoding=='GB2312' else encoding
            with open(document_path, "rb") as infile:
                datas = infile.readlines()
                datas = [data.decode(encoding) for data in datas]
        except Exception as e:
            logger.error(document_path)
            return None
        return datas

    def cut_sentence(self, document_texts):
        """
        把文章按句子拆分为list
        :param document_texts:
        :return: list ["句子1", "句子2"]
        """
        sentences = []
        if isinstance(document_texts, list):
            document_texts = "".join(document_texts)
        # 将\n\r去掉
        document_texts = re.sub("[\n|\r]", "", document_texts)
        # 按符号切分文章
        sentences = re.split('[。.,，！!?？；;]', document_texts)
        # 去掉空字符串和去掉首尾空格
        sentences = [sentence.strip() for sentence in sentences if sentence != ""]
        return sentences

    def cut_word(self, sentences):
        words = []
        if isinstance(sentences, list):
            if get_chinese_ratio(sentences) > 0.5:
                [words.extend(jieba.Tokenizer.lcut(tokenizer, sentence, cut_all=False)) for sentence in sentences]
            else:
                [words.extend(re.split(" ", sentence)) for sentence in sentences]
        else:
            if get_chinese_ratio(sentences) > 0.5:
                words = jieba.Tokenizer.lcut(tokenizer, sentences, cut_all=False)
            else:
                words = re.split(" ", sentences)
        pattern = "[ |&|　|、]"
        words = [re.sub(pattern, "", word) for word in words if re.sub(pattern, "", word) != ""]
        return words

    def cut_phrase(self, sentences):
        """
        获取句子短语
        :param sentences:
        :return: ["短语1"， "短语2"], ["短语1"，"短语1", "短语2"]
        """
        phrases = analyze_phrase(sentences, show=False)
        result = list(_flatten([[phrase] * count for phrase, count in phrases.items()]))
        return list(phrases.keys()), result

    def create_inverted_index(self, words, field_name, document_name, sentences):
        """
        创建倒排索引
        :param texts:
        :param field_name: 所属领域
        :param document_name: 所属文档
        :param sentences: list 文档所有句子
        :return:
        """
        dic_word_count = Counter(words)
        # 保存在index
        for word, count in dic_word_count.items():
            # [领域, 文档, 句子序号， 词出现次数]
            # sentence_id = [[i, s] for i, s in enumerate(sentences) if word in s]
            dic_word_count[word] = [field_name, document_name, count]
            if word in self.index.keys():
                self.index[word].append(dic_word_count[word])
            else:
                self.index[word] = [dic_word_count[word]]

    def compile_pattern(self):
        # 按字符串长度从大到小排序，匹配短语时会有限匹配较长的短语
        participles = sorted(self.participles, key=lambda x:len(x), reverse=True)
        self.pattern = re.compile("[ ](" + '|'.join(participles) + ")[ ]")

    def read_index(self):
        with open(self.index_path, 'rb')as f:
            self.index = pickle.load(f)
        self.index_time = os.path.getmtime(self.index_path)
        if not os.path.exists(PHRASES_PATH):
            self.participles = []
            self.compile_pattern()
            return
        with open(PHRASES_PATH, 'r', encoding="utf-8")as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines]
            self.participles = lines
            self.compile_pattern()

    def build_index(self):
        field_names = os.listdir(self.root)
        for field_name in tqdm(field_names[:2], desc="field"):
            field_path = os.path.join(self.root, field_name)
            if os.path.isfile(field_path):
                continue
            document_names = os.listdir(field_path)
            for document_name in tqdm(document_names[:], desc="document"):
                # if document_name != "C11-Space0004.txt" and document_name != "C11-Space1197.txt":
                #     continue
                document_path = os.path.join(field_path, document_name)
                document_texts = self.read_file(document_path)
                if document_texts is None:
                    continue
                sentences = self.cut_sentence(document_texts)
                words = self.cut_word(sentences)
                uniq_phrases, repeat_phrases = self.cut_phrase(sentences)
                # # 向jieba中加入短语
                # [jieba.add_word(phrase) for phrase in uniq_phrases]
                self.participles.extend(uniq_phrases)
                words.extend(repeat_phrases)
                self.create_inverted_index(words, field_name, document_name, sentences)
        with open(self.index_path, 'wb') as fi, open(PHRASES_PATH, "w", encoding="utf-8") as fw:
            pickle.dump(self.index, fi)
            fw.write("\n".join(self.participles))
            self.compile_pattern()
        self.index_time = os.path.getmtime(self.index_path)

    def init_index(self):
        if self.reset_index or not os.path.exists(self.index_path):
            self.build_index()
            # 向jieba中加入短语
            [jieba.Tokenizer.add_word(tokenizer, phrase) for phrase in self.participles]
        else:
            self.read_index()
            if os.path.exists(PHRASES_PATH):
                jieba.Tokenizer.load_userdict(tokenizer, PHRASES_PATH)

    def auto_correct_sentence(self, query):
        """
        拼写检查
        :param query:
        :return: [有没有错, 修改后的字符串]
        """
        co_query = correct.auto_correct_sentence(query, words=self.participles)
        return co_query != query, co_query

    def search(self, query):
        now_index_time = os.path.getmtime(self.index_path)
        if now_index_time != self.index_time:
            # 若索引文件被修改，则重新读取索引
            self.read_index()
        if get_chinese_ratio(query) > 0.5:
            words = jieba.Tokenizer.lcut(tokenizer, query)
        else:
            words = []
            phrase_iterator = self.pattern.finditer(f" {query} ")
            last_end = 0
            for phrase in phrase_iterator:
                start = phrase.start()
                end = phrase.end()
                texts_prefix = query[last_end:start]
                words_prefix = [w for w in texts_prefix.split(" ") if w.strip()!=""]
                words.extend(words_prefix)
                word = phrase.group()
                word = word.strip()
                words.append(word)
                last_end = end
            texts_suffix = query[last_end:]
            words_suffix = [w for w in texts_suffix.split(" ") if w.strip() != ""]
            words.extend(words_suffix)
        words = set(words)
        results = {}
        for word in words:
            if word in self.index:
                results[word] = self.index[word]
            # else:
            #     results[word] = []
        return results

    def get_sentence(self, datas, num=10):
        """
        获取词
        :param datas:
        :param num: 显示的文档结果个数，默认为10， 传入None则是所有
        :return: 
        """
        result = {}
        for word, docs in datas.items():
            result[word] = []
            # 默认只显示10个文档的结果
            for info in docs[:num]:
                file_path = os.path.join(self.root, info[0], info[1])
                document_texts = self.read_file(file_path)
                document_texts = pretreatment_texts(document_texts)
                if document_texts is None:
                    continue
                sentences = self.cut_sentence(document_texts)
                target_sentences = [s for i, s in enumerate(sentences) if word in s]
                result[word].append(info[:2] + [len(target_sentences)] + target_sentences)
        return result


if __name__ == '__main__':
    text = "工人在巴黎哪裏"
    doc = DocumentSearch()
    state, co_text = doc.auto_correct_sentence(text)
    result = doc.search(co_text)
    pprint(result)
    sentences = doc.get_sentence(result)
    pprint(sentences)
