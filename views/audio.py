
import flask
from flask import Flask, render_template, request, redirect, current_app as app, send_file, g
from app import db, reader
import os
from data.database import Book, BookContent
from scipy.io.wavfile import write
from subprocess import Popen
import json
import numpy as np

import base64 



blueprint = flask.Blueprint('read', __name__, template_folder='templates')

def read_if_not_exists(to_file, text):
    with app.app_context():
        sound = reader.read(text)
        write(to_file, 24000, sound)


@blueprint.get('/player')
def player():
    book_id = request.args['book_id']
    page_num = request.args['page_num']
    book = Book.query.filter(Book.id == book_id).first()
    
    if not book:
        return render_template('404.html'), 404

    book = book.to_dict()

    if not book: return ''

    book_page = BookContent.query.filter(BookContent.book_id == book_id, 
                        BookContent.page_num == page_num).all()

    sentences = sorted([b.sentence_num for b in book_page])


    return render_template('book/audio_player.html', book_id=book_id, page_num=page_num, sentences=sentences)




@blueprint.get('/audio')
def audio():
    book_id  = request.args['book_id']
    page_num = request.args['page_num']
    sentence_num = request.args['sentence_num']
    trigger_read_only = request.args.get('trigger_read_only', False)

    book_content = BookContent.query.filter(BookContent.book_id == book_id, 
                            BookContent.page_num == page_num,
                            BookContent.sentence_num == sentence_num
                            ).first().to_dict()


    audio_dir = f'static/audio/{book_id}/{page_num}/{sentence_num}/'
    file_name = audio_dir + 'audio.wav'

    file_exists  = os.path.isfile(file_name)
    text = book_content['text']

    if not file_exists:
        if len(text.strip()):
            sound = reader.read(text)
        else:
            sound = np.array([0.], dtype=np.float32)

        os.makedirs(audio_dir, exist_ok=True)
        write(file_name, 24000, sound)
    if trigger_read_only == True:
        return '', 200

    return send_file(file_name, mimetype='audio/wav')



@blueprint.get('/read_page')
def reads_page():
    book_id  = request.args['book_id']
    page_num = request.args['page_num']

    book_content = BookContent.query.filter(BookContent.book_id == book_id, 
                            BookContent.page_num == page_num
                            ).all()
    if not book_content:
        return render_template('404.html'), 404

    sentences = sorted([page.to_dict() for page in book_content], key=lambda x: x['sentence_num'])
    for s in sentences:
        sentence_num = s['sentence_num']
        audio_dir = f'static/audio/{book_id}/{page_num}/{sentence_num}/'

        os.makedirs(audio_dir, exist_ok=True)

        file_name = audio_dir + 'audio.wav'

        file_exists  = os.path.isfile(file_name)
        text = s['text']

        if not file_exists:
            print(f"reading {s}")

            if len(text.strip()):
                sound = reader.read(text)
            else:
                sound = np.array([0.], dtype=np.float32)

            write(file_name, 24000, sound)

    return ''


