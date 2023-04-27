from flask_login import current_user,login_required

from main import *
from applications import create_app
from webinterface import *
from flask import redirect
@app.route('/', methods=['get'])
def root():
    return redirect("/admin", code=302)

if __name__ == '__main__':
    app.config['MAX_CONTENT_LENGTH'] = 160 * 1000 * 1000
    app.config['UPLOAD_FOLDER'] ="UPLOAD"
    create_app(app)
    app.run(debug=True, port=18888, host='0.0.0.0');


