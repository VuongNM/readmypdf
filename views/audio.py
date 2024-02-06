
import flask
from flask import Flask, render_template, request, redirect, current_app as app, send_file, g
from app import db, reader
import os
from data.database import Book
from scipy.io.wavfile import write
from subprocess import Popen
import json


blueprint = flask.Blueprint('read', __name__, template_folder='templates')

def read_if_not_exists(to_file, text):
    with app.app_context():
        sound = reader.read(text)
        write(to_file, 24000, sound)


@blueprint.get('/player')
def player():
    _id = request.args['id']
    page = request.args['page']
    book = Book.query.filter(Book.id== _id).first()

    if not book: return render_template('404.html'), 404
    book = book.to_dict()


    audio_dir = f'static/audio/{_id}/{page}/'
    os.makedirs(audio_dir, exist_ok=True)

    audio_filename = 'audio.wav'


    file_exists  = os.path.isfile(audio_dir + audio_filename)

    if file_exists:
        return render_template('book/player.html', audio=True, id=_id, page=page)
    else:
        content  =  json.loads(book['content'])
        text = content.get(str(page), {}).get('text', 'Content not found')
        print(text)
        read_if_not_exists(audio_dir+audio_filename, text)
        return render_template('book/player.html', audio=True, id=_id, page=page)

        # return render_template('book/player.html', book=book, message="Parsing audio, please wait...")



@blueprint.get('/audio')
def audio():

    _id = request.args['id']
    page = request.args['page']
    audio_path = f'static/audio/{_id}/{page}/audio.wav'

    return send_file(
        audio_path, 
        mimetype="audio/wav", 
        as_attachment=True
        )
