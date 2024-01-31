

import flask
from flask import Flask, render_template, request, redirect, current_app as app
from app import db

from data.database import Book
from werkzeug.utils import secure_filename
from datetime import datetime
import fitz
import json
from pdf2image import convert_from_path

import re
import os

from utils import render_text, allowed_file

blueprint = flask.Blueprint('book', __name__, template_folder='templates')




@blueprint.route('/book', methods=['GET', 'POST', 'DELETE', 'PUT'])
def book():
    if request.method == 'GET':
        _id = request.args.get('id', '')

        book = Book.query.filter(Book.id== _id).first().to_dict()
        book['content'] =  json.loads(book['content'])

        if book is not None:
            return render_template('book/book.html', book=book, render_text=render_text)
        else:
            return render_template('404.html'), 404

    elif request.method == 'POST':
        name = request.form.get('name', None)
        file = request.files.get('file', None)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath  = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            #extract a thumbnail 
            thumbnail = convert_from_path(filepath, first_page=0, last_page=1, size=(200,))[0]
            thumbnail_path =  os.path.join(app.config['IMAGE_FOLDER'], filename+'.jpg')

            thumbnail.save(thumbnail_path, "JPEG")



            # parse the pdf into text
            pdf =  fitz.open(filepath)

            author = pdf.metadata.get('author', '')
            title = pdf.metadata.get('title', '')
            
            if len(name) == 0:
                if len(title) > 0:
                    name = title
                else:
                    name = file.filename


            text = [{'text': render_text(page.get_text())} for page in pdf]
            text = dict(zip(list(
                            range(len(text))), 
                            text))
            text = json.dumps(text)

            Book.create(name=name, 
                        path=filepath, 
                        author = author,
                        title = title,
                        content = text, 
                        thumbnail=thumbnail_path,
                        timestamp=datetime.now())
        
            return redirect('/catalog', 303)

    elif request.method == 'PUT':
        _id = request.args.get('id', '')
        book = Book.query.filter(Book.id == _id).first()
        
        _book = book.to_dict()
        print(_book)
        print (request.form.get('name'))
        print (request.args.get('id'))

        book.update(name=request.form.get('name'), 
                    path=_book['path'], 
                    author = _book['author'],
                    title = _book['title'],
                    content = _book['content'], 
                    thumbnail=_book['thumbnail'],
                    timestamp=datetime.now())

        return render_template('/book/booktitle.html', book=book)


@blueprint.route('/bookedit', methods=['GET'])
def bookedit():
    _id = request.args.get('id', '')
    book = Book.query.filter(Book.id== _id).first().to_dict()
    return render_template('book/bookedit.html', book=book)