from flask import Flask
from flask import url_for, redirect, render_template

from database import init_db
from database import db_session
from models import *

from tasks import *

import re
import os
from glob import glob

PREFIX = "carpedm20"
BASE_URL = "http://pail.unist.ac.kr/"

app = Flask(__name__, static_url_path="/%s/critic/static" % PREFIX,)

@app.route('/')
@app.route('/%s/' % PREFIX)
def root():
    return redirect(url_for('index'))

@app.route('/%s/critic/' % PREFIX)
def index():
    years = glob("./static/*.json")

    return render_template('index.html')

if __name__ == '__main__':
    path = os.path.join(os.path.dirname(__file__), 'login.long.js')
    app.logger.debug(path)

    app.run(host='0.0.0.0', debug=True, port=5003)
