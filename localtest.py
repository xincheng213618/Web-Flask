
from main import *
from applications import create_app
if __name__ == '__main__':
    create_app(app)
    app.run(debug=True, port=18888, host='0.0.0.0');
