# Servidor do Clone do Dropbox
from flask import Flask, send_file, request
from datetime import datetime
import cPickle as pickle
import os
app = Flask(__name__)

@app.route('/<user>/<psswd>/auth')
def auth(user, psswd):
    try: users = pickle.load(open('./myDropboxServer/users.p','rb'))
    except: users = {} 
    if user not in users:
        users[user] = {'password':psswd, 'lastlogin':False}
        try: os.makedirs('./myDropboxServer/'+user+'/')
        except: return 'False'
        pickle.dump(users, open('./myDropboxServer/users.p','wb'))
        return 'True'
    if users[user]['password'] != psswd: return 'False'
    pickle.dump(users, open('./myDropboxServer/users.p','wb'))
    return 'True'

@app.route('/<user>/<psswd>/numfiles')
def numfiles(user, psswd):
    if auth(user, psswd) != 'True': return 'Falha na autenticacao.'
    userpath = './myDropboxServer/'+user+'/'
    numfiles = sum([len(files) for r, d, files in os.walk(userpath)])
    return 'Numero de arquivos no diretorio: %s' % numfiles

def listFiles(dirname):
    fileList = []
    for (rootdir, dirnames, filenames) in os.walk(dirname):
        fileList.extend(filenames)
        for subdir in dirnames:
            subList = listFiles(rootdir+subdir)
            for item in subList:
                fileList.append(subdir+'/'+item)
            fileList.append(subdir)
    return fileList

@app.route('/<user>/<psswd>/list')
def get_list(user, psswd):
    '''Funcao que lida com requests de listagem de arquivos'''
    if auth(user,psswd) != 'True': return 'Falha na autenticacao.'
    files = {}
    userpath = './myDropboxServer/'+user+'/'
    file_list = listFiles(userpath)
    for f in file_list:
        try: files[f] = {'time':os.stat(userpath+f).st_mtime,'type':os.path.isdir(userpath+f)}
        except: files[f] = {'time':0,'type':None}
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
