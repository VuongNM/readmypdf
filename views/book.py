

import flask
from flask import Flask, render_template, request, redirect, current_app as app, send_file
from app import db

from data.database import Book, BookContent
from werkzeug.utils import secure_filename
from datetime import datetime
import fitz
import json
from pdf2image import convert_from_path
import io
from PyPDF2 import PdfReader
from PyPDF2 import PdfWriter
import nltk
import re
import os

from utils import parse_text, allowed_file

blueprint = flask.Blueprint('book', __name__, template_folder='templates')


def render_text_as_html(sentences):
    # sentences is a list of strings
    text = ' '.join(sentences)
    paragraphs = text.split('\n')

    # return text
    def _wrap(para):
        return f"<p> {para} </p>"

    return " <br> ".join([_wrap(p) for p in paragraphs])


@blueprint.route('/book', methods=['GET', 'POST', 'DELETE', 'PUT'])
def book():
    if request.method == 'GET':
        _id = request.args.get('id', '')
        from_page = int(request.args.get('from', 0))
        limit = int(request.args.get('limit', 10))

        book = Book.query.filter(Book.id== _id).first()

        if book is not None:
            book = book.to_dict()

            book_content = BookContent.query.filter(BookContent.book_id==_id, 
                                        BookContent.page_num >= from_page,
                                        BookContent.page_num < from_page+limit
                                        ).order_by(BookContent.page_num, BookContent.sentence_num).all()

            
            pages = [
                ["sentence11", "sentence12"],
                ["sentence21", "sentence22"],

            ]
            pages = {}
            book_content = [sent.to_dict() for sent in book_content]
            for sent in book_content:
                if sent['page_num'] not in pages:
                    pages[sent['page_num']] = [ sent['text'] ]
                else:
                    pages[sent['page_num']] += sent['text'],

            pages = dict(sorted(pages.items())) #python 3.7+


            next_chunk = from_page + limit if len(pages) else None

            if 'HX-Request' in request.headers:
                return render_template('book/bookpage.html',
                                book_id=_id,
                                pages=pages,
                                book=book,
                                next_chunk = next_chunk,
                                render_text_as_html=render_text_as_html
                                )
            else:
                return render_template('book/book.html',
                                book_id=_id,
                                pages=pages,
                                book=book,
                                sentences=book_content,
                                next_chunk=next_chunk,
                                render_text_as_html=render_text_as_html
                                )
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
            thumbnail_path =  os.path.join(app.config['IMAGE_FOLDER'], 'upload', filename+'.jpg')

            thumbnail.save(thumbnail_path, "JPEG")



            # parse the pdf into text
            # pdf is now a list of PDF page
            pdf =  fitz.open(filepath)

            author = pdf.metadata.get('author', '')
            title = pdf.metadata.get('title', '')

            if len(name) == 0:
                if len(title) > 0:
                    name = title
                else:
                    name = file.filename


            text = [{'text': parse_text(page.get_text())} for page in pdf]

            text = dict(zip(list(
                            range(len(text))),
                            text))

            # text = {
            #     page '1': {'text': "asdfadsf"},
            #     page '2': {'text': "asdfadsf"},
            #     ...
            # }

            text_json = json.dumps(text)

            book = Book.create(name=name,
                        path=filepath,
                        author=author,
                        title=title,
                        content=text_json,
                        thumbnail=thumbnail_path,
                        timestamp=datetime.now())

            book_content = []
            for page_num, page_content in text.items():
                paragraphs = page_content['text'].split('\n\n')
                
                sentences = []
                for p in paragraphs:
                    sentences += nltk.sent_tokenize(p)
                    sentences += '\n\n',

                for sentence_num, sentence in enumerate(sentences):
                    book_content += BookContent(
                        book_id=book.id,
                        page_num=page_num,
                        sentence_num=sentence_num,
                        text=sentence if len(sentence) else None,
                        audio=None),
                


            db.session.bulk_save_objects(book_content)
            db.session.commit()

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







@blueprint.route('/pdf', methods=['GET'])
def page():
    _id = request.args.get('id')
    page = int(request.args.get('page'))
    filepath = request.args.get('filepath')


    page = PdfReader(filepath).pages[page]
    page.scale_to(868,1216)
    pdf = PdfWriter()
    pdf.add_page(page)

    outfile = io.BytesIO()
    pdf.write(outfile)
    pdf.close()
    outfile.seek(0)

    return send_file(outfile, mimetype='application/pdf')





@blueprint.route('/player2', methods=['GET'])
def player():
    return render_template('book/audio_player.html')


