# Servidor do Clone do Dropbox
from flask import Flask, send_file, request
import cPickle as pickle
import os
app = Flask(__name__)
users ={'usuario':'hash'}

@app.route('/<user>/<psswd>/auth')
def auth(user, psswd):
    try: users = pickle.load(open('./myDropboxServer/users.p','rb'))
    except: users = {} 
    if user not in users:
        users[user] = psswd
        try: os.makedirs('./myDropboxServer/'+user+'/')
        except: return 'False'
        pickle.dump(users, open('./myDropboxServer/users.p','wb'))
        return 'True'
    if users[user] != psswd: return 'False'
    return 'True'

@app.route('/<user>/<psswd>/list')
def get_list(user, psswd):
    '''Funcao que lida com requests de listagem de arquivos'''
    if auth(user,psswd) != 'True': return 'Falha na autenticacao.'
    files = {}
    userpath = './myDropboxServer/'+user+'/'
    file_list = os.listdir(userpath)
    for f in file_list:
        try: files[f] = {'time':os.stat(userpath+f).st_mtime,'type':os.path.isdir(userpath+f)}
        except: files[f] = 0
    pickle.dump(files, open(userpath+'files.p','wb'))
    return send_file(userpath+'files.p')

@app.route('/<user>/<psswd>/download/<item>')
def download(user, psswd, item):
    '''Funcao que lida com requests de download'''
    if auth(user,psswd) != 'True': return 'Falha na autenticacao.'
    userpath = './myDropboxServer/'+user+'/'
    return send_file(userpath+item)

@app.route('/<user>/<psswd>/upload/<item>/<f_type>', methods=['POST'])
def upload(user, psswd, item, f_type):
    '''Funcao que lida com requests de upload'''
    if auth(user,psswd) != 'True': return 'Falha na autenticacao.'
    userpath = './myDropboxServer/'+user+'/'
    if not os.path.exists(userpath): os.makedirs(userpath)
    if f_type == "file":
        file = request.files['file']
        file.save(userpath+item)
    elif f_type == "folder":
        os.makedirs(userpath+item)
    return

@app.route('/<user>/<psswd>/delete/<item>')
def delete(user, psswd, item):
    '''Funcao que lida com requests de delete'''
    if auth(user,psswd) != 'True': return 'Falha na autenticacao.'
    userpath = './myDropboxServer/'+user+'/'
    try: os.rmdir(userpath+item)
    except: 
        try: os.remove(userpath+item)
        except: print 'Erro ao deletar arquivo'
    return

if __name__ == '__main__':
    app.run(host='127.0.0.1')
