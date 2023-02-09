import os

from flask import Flask, render_template
from dotenv import load_dotenv

from frontend import routes
load_dotenv()

template_folder_path = os.path.join('..', 'data', 'frontend_websites','templates')
static_path = os.path.join(template_folder_path,'..','static_files')
app = Flask(__name__, template_folder=template_folder_path,static_folder=static_path)


@app.route('/')
def root():
    return render_template('index.html')


if __name__ == '__main__':
    print(os.getenv('DEBUG'))
    app.run(debug=True)
