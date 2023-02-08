import os

from flask import Flask
from dotenv import load_dotenv

from frontend import routes

load_dotenv()
app = Flask(__name__)

@app.route('/')
def root():
    return '<p>TEst</p>'

if __name__ == '__main__':
    print(os.getenv('DEBUG'))
    app.run(debug=True)