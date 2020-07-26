# -*- coding: utf-8 -*- 
# @Time 2020/6/28 15:09
# @Author wcy
import hashlib
import json
import os
import re
import shutil
import time
from random import shuffle

from flask import render_template, request, redirect, url_for, jsonify
from wtforms.validators import DataRequired, Length
import threading

from common.logger_config import logger
from config import STATIC_PATH, PHRASES_PATH
from nlp.match_analysis import MatchAnalysis
from nlp.retrieve_analyze import DocumentSearch
from nlp.subject_analyze import read_corpus_file, analyze_word_likelihood, analyze_phrase_likelihood
from nlp.util import read_txt, pretreatment_texts
from nlp.word_frequency import analyze_word, analyze_phrase
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, StringField, SelectField
from view import app, photos, match_analy, doc_search


class UploadForm(FlaskForm):
    photo = FileField(validators=[
        FileAllowed(photos, u'只能选择文本文件'), FileRequired(u'选择一个文件!')
    ])
    # field_name = StringField('name',
    #                    validators=[DataRequired(message=u"领域名不能为空"), Length(1, 10, message=u'长度位于1~10之间')],
    #                    render_kw={'placeholder': u'输入领域名'})
    field_name = SelectField(
        label='类别',
        validators=[DataRequired('请选择标签')],
        render_kw={
            'class': 'form-control'
        },
        choices=[(0, '未选择无法上传'), (1, '领域一'), (2, '领域二')],
        default=3,
        coerce=int

    )
    submit = SubmitField(u'上传')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        field_name = form.field_name.choices[form.field_name.data][1]
        field_path = os.path.join(STATIC_PATH, field_name)
        if not os.path.exists(field_path):
            os.mkdir(field_path)
        for file_info in request.files.getlist('photo'):
            seed = ('admin' + str(time.time())).encode('UTF-8')
            suffix = hashlib.md5(seed).hexdigest()[:3]
            file_name, _ = os.path.splitext(file_info.filename)
            file_name_path = os.path.join(field_path, f"{file_name}_{suffix}.txt")
            file_info.save(file_name_path)
            # photos.save(file_info, name=name + '.', folder=field_path)
        success = True
    else:
        success = False
    return render_template('index.html', form=form, success=success)


@app.route('/word_counts/<field_name>/<filename>')
def word_counts(field_name, filename):
    file_path = os.path.join(field_name, filename)
    path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], file_path)
    datas = read_txt(path)
    datas = " ".join(datas)
    word_counts = analyze_word(datas)
    word_counts = {k:v for k, v in word_counts.items() if len(k)>1}
    word_counts = sorted(word_counts.items(), key=lambda d: d[1], reverse=True)
    return render_template('word_count.html', field_name=field_name, filename=filename, word_counts=word_counts)


@app.route('/phrase_counts/<field_name>/<filename>')
def phrase_counts(field_name, filename):
    file_path = os.path.join(field_name, filename)
    path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], file_path)
    datas = read_txt(path)
    phrase_counts = analyze_phrase(datas)
    phrase_counts = sorted(phrase_counts.items(), key=lambda d: d[1], reverse=True)
    return render_template('word_count.html', field_name=field_name, filename=filename, word_counts=phrase_counts)


@app.route('/match_word/<field_name>/<filename>/<word>')
def match_word(field_name, filename, word):
    path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], field_name, filename)
    lines = read_txt(path)
    lines = pretreatment_texts(lines)
    results = [len(re.findall(word, line)) for line in lines]
    return render_template('position.html', filename=filename, lines=lines, results=results, lenght=len(lines),
                           word=word)


@app.route('/manage_file/<field_name>')
def manage_file(field_name):
    file_path = os.path.join(STATIC_PATH, field_name)
    files_list = os.listdir(file_path)
    return render_template('manage_file.html', files_list=files_list, field_name=field_name)


@app.route('/manage_dir')
def manage_dir():
    dir_list = os.listdir(STATIC_PATH)
    return render_template('manage_dir.html', dir_list=dir_list)


@app.route('/open/<field_name>/<filename>')
def open_file(filename, field_name):
    file_url = photos.url(filename)
    file_path = os.path.join(field_name, filename)
    path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], file_path)
    lines = read_txt(path)
    return render_template('browser.html', filename=filename, texts=lines)


@app.route('/delete_dir/<field_name>')
def delete_dir(field_name):
    dir_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], field_name)
    if not os.path.exists(dir_path):
        return redirect(url_for('manage_dir'))
    shutil.rmtree(dir_path)
    return redirect(url_for('manage_dir'))


@app.route('/delete_file/<field_name>/<filename>')
def delete_file(field_name, filename):
    file_path = os.path.join(field_name, filename)
    # file_path = photos.path(file_path)
    file_path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], file_path)
    if not os.path.exists(file_path):
        return redirect(url_for('manage_dir'))
    os.remove(file_path)
    return redirect(url_for('manage_file', field_name=field_name))


@app.route('/subject_analyze')
def subject_analyze():
    field1_path = os.path.join(STATIC_PATH, "领域一")
    field2_path = os.path.join(STATIC_PATH, "领域二")
    corpus1 = read_corpus_file(field1_path)
    corpus2 = read_corpus_file(field2_path)
    word_likelihood_sort = analyze_word_likelihood(corpus1, corpus2)
    phrase_likelihood_sort = analyze_phrase_likelihood(corpus1, corpus2)
    field1_word = word_likelihood_sort[:20]
    field2_word = word_likelihood_sort[::-1][:20]
    field1_phrase = phrase_likelihood_sort[:20]
    field2_phrase = phrase_likelihood_sort[::-1][:20]
    datas = [[f"{w1[0]} - {round(w1[1], 2)}",
              f"{p1[0]} - {round(p1[1], 2)}",
              f"{w2[0]} - {round(-w2[1], 2)}",
              f"{p2[0]} - {round(-p2[1], 2)}"]
             for w1, p1, w2, p2 in zip(field1_word, field1_phrase, field2_word, field2_phrase)]
    return render_template('subject_analyze.html', datas=datas)


@app.route('/manage_search')
def manage_search():
    lines = []
    try:
        with open(PHRASES_PATH, 'r', encoding="utf-8")as f:
            lines = f.readlines()
            shuffle(lines)
            lines = [line.strip() for line in lines[:300]]
    except:
        logger.error("读取PHRASES_PATH出错！")
    return render_template('search.html', lines=lines)


@app.route('/search', methods=['POST'])
def search():
    try:
        texts = request.values["texts"]
        reslut = doc_search.search(texts)
        reslut = doc_search.get_sentence(reslut)
        return jsonify(code=1, msg=f"ok", data=reslut)
    except Exception as e:
        return jsonify(code=0, msg=f"no")


@app.route('/reset_index/<intention>', methods=['POST'])
def reset_index(intention):
    """

    :param intention: [submit, confirm] [提交任务建立索引， 确认是否存在任务]
    :return:
    """
    t_name = [t.name for t in threading.enumerate() if t.name == "reset_index"]
    if intention=="confirm":
        if len(t_name) > 0:
            # 返回no 表示有任务在进行
            return jsonify(code=0, msg="no")
        else:
            # 返回ok 表示没有任务在进行
            return jsonify(code=1, msg=f"ok")
    elif intention=="submit":
        if len(t_name) > 0:
            # 返回 no 表示有任务在进行
            return jsonify(code=0, msg="no")
        else:
            # 返回ok 表示启动一个任务
            threading.Thread(target=DocumentSearch, args=(True,), name="reset_index").start()
            return jsonify(code=1, msg=f"ok")
    else:
        return jsonify(code=2, msg=f"unknow")


@app.route('/match_analysis', methods=['POST'])
def match_analysis():
    values = request.values
    word = values.get("word", "")
    num = values.get("num", 5)
    if isinstance(num, str):
        num = int(num)
    sentences = values.get("sentences", [])
    if isinstance(sentences, str):
        sentences = json.loads(sentences)
    try:
        pattern = doc_search.pattern
        result = match_analy.match(word, sentences=sentences, document_search=doc_search, num=num, pattern=pattern)
        return jsonify(code=1, msg=f"ok", data=result)
    except Exception as e:
        logger.error(f"{e}")
        return jsonify(code=0, msg="no")
