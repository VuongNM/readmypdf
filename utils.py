import fitz
import statistics

from config import ALLOWED_EXTENSIONS
def clear_files():
    # todo: clear uploaded files
    pass

def get_book_link(book_id):
    return f'/book?id={bookid}'


def parse_text(text):

    lines = text.split('\n')
    # avg_len = sum([len(x) for x in lines]) / len(lines)
    avg_len = statistics.median([len(l) for l in lines])
    rendered = []
    for l in lines:
        if len(l) < 0.9 * avg_len and l.endswith('.'):
           l += '\n\n'
        rendered += l,


    text = '\n'.join(rendered)
    # return the text with original line breaking
    # return text
    paragraph = text.split('\n\n')
    paragraph = [p.replace('\n', '') for p in paragraph]

    return '\n\n'.join(paragraph)

ALLOWED_EXTENSIONS = {'pdf', 'PDF'}



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

