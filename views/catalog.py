import flask
from flask import Flask, render_template, request, redirect, current_app as app
from app import db

from data.database import Book
from werkzeug.utils import secure_filename
from utils import get_book_link

import re
import os
import json

blueprint = flask.Blueprint('catalog', __name__, template_folder='templates')

@blueprint.get('/about')
def about():
    return render_template('/about.html')


@blueprint.get('/catalog')
@blueprint.get('/')
def catalog():
    books = [x.to_dict() for x in Book.query.all()]

    return render_template('/catalog.html', books=books)

