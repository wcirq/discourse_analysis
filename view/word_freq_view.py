# -*- coding: utf-8 -*- 
# @Time 2020/6/28 15:09
# @Author wcy
import hashlib
import os
import re
import time

from flask import render_template, request, redirect, url_for

from nlp.util import read_txt
from nlp.word_frequency import analyze_word, analyze_phrase
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
from view import app, photos


class UploadForm(FlaskForm):
    photo = FileField(validators=[
        FileAllowed(photos, u'只能选择文本文件'), FileRequired(u'Choose a file!')
                                  ])
    submit = SubmitField(u'上传')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        for filename in request.files.getlist('photo'):
            f = ('admin' + str(time.time())).encode('UTF-8')
            name = hashlib.md5(f).hexdigest()[:15]
            photos.save(filename, name=name + '.')
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

@app.route('/manage')
def manage_file():
    files_list = os.listdir(app.config['UPLOADED_PHOTOS_DEST'])
    return render_template('manage.html', files_list=files_list)


@app.route('/open/<filename>')
def open_file(filename):
    file_url = photos.url(filename)
    path = os.path.join(app.config['UPLOADED_PHOTOS_DEST'], filename)
    lines = read_txt(path)
    return render_template('browser.html', filename=filename, texts=lines)


@app.route('/delete/<filename>')
def delete_file(filename):
    file_path = photos.path(filename)
    os.remove(file_path)
    return redirect(url_for('manage_file'))