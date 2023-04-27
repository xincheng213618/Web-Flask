from main import *

from flask import redirect
@app.route('/', methods=['get'])
def root():
    return redirect("http://www.njust-sci.com/", code=302)

if __name__ == '__main__':
    app.config['MAX_CONTENT_LENGTH'] = 160 * 1000 * 1000
    app.config['UPLOAD_FOLDER'] ="UPLOAD"
    app.run(debug=True, port=18888, host='0.0.0.0', ssl_context=('v3.xincheng213618.com_bundle.crt', 'v3.xincheng213618.com.key'));


