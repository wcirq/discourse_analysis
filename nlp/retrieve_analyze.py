# -*- coding: utf-8 -*- 
# @Time 2020/6/29 12:17
# @Author wcy
import os
import pickle
import re
from _tkinter import _flatten
from collections import Counter
from pprint import pprint

import chardet
import jieba
from tqdm import tqdm

from common.logger_config import logger
from config import INDEX_ROOT_PATH, PHRASES_PATH
from nlp import correct
from nlp.word_frequency import analyze_phrase

root = "E:\\DATA\\领域数据"


class DocumentSearch():

    def __init__(self, root=root):
        self.root = root
        self.index = {}  # 倒排索引
        self.participles = []  # 加入jieba用于分词的短语
        self.init_index()

    def read_file(self, document_path):
        try:
            bytes = min(2048, os.path.getsize(document_path))
            raw = open(document_path, 'rb').read(bytes)
            result = chardet.detect(raw)
            encoding = result['encoding']

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
            document_texts = "。".join(document_texts)
        # 将\n\r去掉
        document_texts = re.sub("[\n|\r]", "", document_texts)
        # 按符号切分文章
        sentences = re.split('[,。.，！!?？；;]', document_texts)
        # 去掉空字符串和去掉首尾空格
        sentences = [sentence.strip() for sentence in sentences if sentence != ""]
        return sentences

    def cut_word(self, sentences):
        words = []
        if isinstance(sentences, list):
            [words.extend(jieba.cut(sentence, cut_all=False)) for sentence in sentences]
        else:
            words = jieba.lcut(sentences, cut_all=False)
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

    def init_index(self, version=2):
        index_path = os.path.join(INDEX_ROOT_PATH, f"{version}.dict")
        if os.path.exists(index_path):
            with open(index_path, 'rb')as f:
                self.index = pickle.load(f)
            with open(PHRASES_PATH, 'r', encoding="utf-8")as f:
                lines = f.readlines()
                lines = [line.strip() for line in lines]
                self.participles = lines
            jieba.load_userdict(PHRASES_PATH)
        else:
            field_names = os.listdir(self.root)
            for field_name in tqdm(field_names[:5], desc="field"):
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
            with open(index_path, 'wb') as fi, open(PHRASES_PATH, "w", encoding="utf-8") as fw:
                pickle.dump(self.index, fi)
                fw.write("\n".join(self.participles))
            # 向jieba中加入短语
            [jieba.add_word(phrase) for phrase in self.participles]

    def auto_correct_sentence(self, query):
        """
        拼写检查
        :param query:
        :return: [有没有错, 修改后的字符串]
        """
        co_query = correct.auto_correct_sentence(query, words=self.participles)
        return co_query != query, co_query

    def search(self, query):
        words = jieba.lcut(query)
        words = set(words)
        results = {}
        for word in words:
            if word in self.index:
                results[word] = self.index[word]
        return results

    def get_sentence(self, datas):
        result = {}
        for word, docs in datas.items():
            result[word] = []
            for info in docs[:10]:
                file_path = os.path.join(self.root, info[0], info[1])
                document_texts = self.read_file(file_path)
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
