
import flask
from flask import Flask, render_template, request, redirect, current_app as app, send_file
from app import db
import os
from data.database import Book

blueprint = flask.Blueprint('read', __name__, template_folder='templates')


@blueprint.get('/player')
def player():
    _id = request.args['id']
    page = request.args['page'] 

    file_exists  = True
    if file_exists:
        return render_template('book/player.html', audio=True, id=_id, page=page)
    else:
        book = Book.query.filter(Book.id== _id).first().to_dict()
        return render_template('book/player.html', book=book, message="Parsing audio, please wait...")



@blueprint.get('/audio')
def audio():

    _id = request.args['id']
    page = request.args['page']

    path_to_file =  os.path.join(app.config['AUDIO_FOLDER'], 'test.mp3')
    print( path_to_file)

    return send_file(
        path_to_file, 
        mimetype="audio/wav", 
        as_attachment=True
        )
