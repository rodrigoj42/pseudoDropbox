# Servidor do Clone do Dropbox
from flask import Flask, send_file, request
from datetime import datetime
import cPickle as pickle
import os
import urllib
app = Flask(__name__)

@app.route('/<user>/<psswd>/auth')
def auth(user, psswd):
    try: users = pickle.load(open('./myDropboxServer/users.p','rb'))
    except: users = {} 
    if user not in users:
        users[user] = {'password':psswd, 'lastlogin':False, 'thislogin':datetime.now()}
        try: os.makedirs('./myDropboxServer/'+user+'/')
        except: return 'False'
        pickle.dump(users, open('./myDropboxServer/users.p','wb'))
        return 'True'
    if users[user]['password'] != psswd: return 'False'
    pickle.dump(users, open('./myDropboxServer/users.p','wb'))
    return 'True'

@app.route('/<user>/<psswd>/lastlogin')
def lastlogin(user, psswd):
    if auth(user, psswd) != 'True': return 'Falha na autenticacao.'
    users = pickle.load(open('./myDropboxServer/users.p','rb'))
    l = users[user]['lastlogin']
    if l:
        lastlogin = 'Ultimo acesso em %02d/%02d/%04d as %02d:%02d:%02d' % (l.day, l.month, l.year, l.hour, l.minute, l.second)
    else:
        lastlogin = 'Este e seu primeiro acesso.'
    users[user]['lastlogin'] = users[user]['thislogin']
    users[user]['thislogin'] = datetime.now()
    pickle.dump(users, open('./myDropboxServer/users.p','wb'))
    return lastlogin

def listFiles(dirname):
    fileList = []
    dirList = []
    for (rootdir, dirnames, filenames) in os.walk(dirname):
        for item in filenames: fileList.append(rootdir+'/'+item)
        if rootdir != dirname: dirList.append(rootdir)
    return (fileList, dirList)

@app.route('/<user>/<psswd>/list')
def get_list(user, psswd):
    '''Funcao que lida com requests de listagem de arquivos'''
    if auth(user,psswd) != 'True': return 'Falha na autenticacao.'
    files = {}
    userpath = './myDropboxServer/'+user
    (fileList, dirList) = listFiles(userpath)
    for f in fileList:
        f = f[len(userpath)+1:]
        try: files[f] = {'time':os.stat(userpath+'/'+f).st_mtime,'type':'file'}
        except: files[f] = {'time':0,'type':None}
    for f in dirList:
        f = f[len(userpath)+1]
        try: files[f] = {'time':os.stat(userpath+'/'+f).st_mtime, 'type':'folder'}
        except: files[f] = {'time':0,'type':None}
    pickle.dump(files, open(userpath+'/files.p','wb'))
    return send_file(userpath+'/files.p')

@app.route('/<user>/<psswd>/download/<item>')
def download(user, psswd, item):
    '''Funcao que lida com requests de download'''
    if auth(user,psswd) != 'True': return 'Falha na autenticacao.'
    userpath = './myDropboxServer/'+user+'/'
    return send_file(userpath+item)

@app.route('/<user>/<psswd>/upload/<f_type>', methods=['POST'])
def upload(user, psswd, item, f_type):
    '''Funcao que lida com requests de upload'''
    if auth(user,psswd) != 'True': return 'Falha na autenticacao.'
    userpath = './myDropboxServer/'+user+'/'
    if not os.path.exists(userpath): os.makedirs(userpath)
    print request
    if f_type == "file":
        file = request.files['file']
        item = req
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
