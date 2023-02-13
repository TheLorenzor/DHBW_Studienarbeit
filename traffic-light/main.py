import os
import multiprocessing
from flask import Flask, render_template
from dotenv import load_dotenv

from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer
from frontend import routes
load_dotenv()

template_folder_path = os.path.join('..', 'data', 'frontend_websites','templates')
static_path = os.path.join(template_folder_path,'..','static_files')
app = Flask(__name__, template_folder=template_folder_path,static_folder=static_path)


@app.route('/')
def root():
    return render_template('index.html')

authorizer = DummyAuthorizer()
curr_dir = os.path.dirname(__file__)
base_data_dir = os.path.join(curr_dir,'..','data','train')
authorizer.add_user('user', '12345', base_data_dir, perm='elradfmwMT')
authorizer.add_anonymous(os.getcwd())

handler = FTPHandler
handler.authorizer = authorizer
handler.banner = "FTP Server ready"

server = FTPServer(('127.0.0.1',os.getenv('FTP-PORT')),handler)
server.max_cons = 2
server.max_cons_per_ip = 5


if __name__ == '__main__':
    ftpserver = multiprocessing.Process(server.serve_forever())
    ftpserver.start()
    app.run(debug=os.getenv('DEBUG'))
