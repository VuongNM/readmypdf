import sys


# from data.database import get_db, query_db, close_connection, insert

from flask_sqlalchemy import SQLAlchemy
from config import DB_LOCAITON, UPLOAD_FOLDER, IMAGE_FOLDER, AUDIO_FOLDER
from utils import *

import flask

app = flask.Flask('app')


app.config['SQLALCHEMY_DATABASE_URI'] = DB_LOCAITON
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER

db = SQLAlchemy(app)




def register_blueprint():
    from views import catalog, book, audio
    app.register_blueprint(catalog.blueprint)
    app.register_blueprint(book.blueprint)
    app.register_blueprint(audio.blueprint)


def configure():

    # setting up the database
    from data.database import Book

    with app.app_context():
        db.create_all()

        # _ = Book.create(name='zen and the art of motorcycle maintenance', path='data/storage/file1')
        # _ = Book.create(name='zen', path='data/storage/file1')
        # _ = Book.create(name='road to serfdom', path='data/storage/file2')
        print ("here")
        db.session.commit()


    print ("register_blueprint...")

    register_blueprint()


if __name__ == '__main__':
    configure()
    being_debugged = sys.gettrace() is not None
    app.run(debug=being_debugged)
else:
    configure()