import fitz
import statistics

from config import ALLOWED_EXTENSIONS
def clear_files():
    # todo: clear uploaded files
    pass

def get_book_link(book_id):
    return f'/book?id={bookid}'


def render_text(text):

    lines = text.split('\n')
    # avg_len = sum([len(x) for x in lines]) / len(lines)
    avg_len = statistics.median([len(l) for l in lines])
    rendered = []
    for l in lines:
        if len(l) < 0.8 * avg_len and l.endswith('.'):
           l += '\n\n'
        rendered += l,
    return '\n'.join(rendered)


ALLOWED_EXTENSIONS = {'pdf', 'PDF'}



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

