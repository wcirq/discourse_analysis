# -*- coding: utf-8 -*- 
# @Time 2020/6/28 15:10
# @Author wcy
import os

from flask import Flask
from flask_uploads import UploadSet, TEXT, configure_uploads, patch_request_class

from nlp.match_analysis import MatchAnalysis
from nlp.retrieve_analyze import DocumentSearch

app = Flask(__name__, template_folder="../templates", static_folder="../templates")
app.config['SECRET_KEY'] = 'I have a dream'
app.config['UPLOADED_PHOTOS_DEST'] = os.getcwd() + '/static'

photos = UploadSet('photos', TEXT)
configure_uploads(app, photos)
patch_request_class(app)  # set maximum file size, default is 16MB
doc_search = DocumentSearch()
match_analy = MatchAnalysis()

from view import word_freq_view


