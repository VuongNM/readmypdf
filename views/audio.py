blueprint = flask.Blueprint('read', __name__, template_folder='templates')

@blueprint.get('/read')
def read():
    return "Hello world"
