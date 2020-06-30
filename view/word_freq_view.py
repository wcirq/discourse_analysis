# -*- coding: utf-8 -*- 
# @Time 2020/6/28 15:09
# @Author wcy
import hashlib
import os
import re
import shutil
import time

from flask import render_template, request, redirect, url_for
from wtforms.validators import DataRequired, Length

from config import STATIC_PATH
from nlp.subject_analyze import read_corpus_file, analyze_word_likelihood, analyze_phrase_likelihood
from nlp.util import read_txt
from nlp.word_frequency import analyze_word, analyze_phrase
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, StringField, SelectField
from view import app, photos


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


@app.route('/word_counts/<filename>')
def word_counts(filename):
    path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
    datas = read_txt(path)
    datas = "".join(datas)
    word_counts = analyze_word(datas)
    word_counts = sorted(word_counts.items(), key=lambda d: d[1], reverse=True)
    return render_template('word_count.html', filename=filename, word_counts=word_counts)


@app.route('/phrase_counts/<filename>')
def phrase_counts(filename):
    path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
    datas = read_txt(path)
    phrase_counts = analyze_phrase(datas)
    phrase_counts = sorted(phrase_counts.items(), key=lambda d: d[1], reverse=True)
    return render_template('word_count.html', filename=filename, word_counts=phrase_counts)


@app.route('/mach_word/<filename>/<word>')
def mach_word(filename, word):
    path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
    lines = read_txt(path)
    results = [len(re.findall(word, line)) for line in lines]
    return render_template('position.html', filename=filename, lines=lines, results=results, lenght=len(lines), word=word)


@app.route('/manage_file/<field_name>')
def manage_file(field_name):
    file_path = os.path.join(STATIC_PATH, field_name)
    files_list = os.listdir(file_path)
    files_list = [os.path.join(field_name, file) for file in files_list]
    return render_template('manage_file.html', files_list=files_list)


@app.route('/manage_dir')
def manage_dir():
    dir_list = os.listdir(STATIC_PATH)
    return render_template('manage_dir.html', dir_list=dir_list)


@app.route('/open/<filename>')
def open_file(filename):
    file_url = photos.url(filename)
    path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
    lines = read_txt(path)
    return render_template('browser.html', filename=filename, texts=lines)


@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = photos.path(filename)
    if not os.path.exists(file_path):
        return redirect(url_for('manage_dir'))
    if os.path.isfile(file_path):
        os.remove(file_path)
        return redirect(url_for('manage_file', field_name=os.path.dirname(filename)))
    else:
        shutil.rmtree(file_path)
        return redirect(url_for('manage_dir'))


@app.route('/subject_analyze')
def subject_analyze():
    field1_path = os.path.join(STATIC_PATH, "领域一")
    field2_path =  os.path.join(STATIC_PATH, "领域二")
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