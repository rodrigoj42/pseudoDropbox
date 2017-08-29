# Cliente do Clone do Dropbox
import os, hashlib, urllib, pickle, requests
from time import sleep
from getpass import getpass
from flask import send_file

# configs
url = 'http://127.0.0.1:5000' # servidor
path = '.' # pasta atual
t = 5 # segundos de espera

#functions
def auth(user, psswd):
    '''Envia usuario e hash para o servidor a fim de descobrir se o usuario esta ou nao autenticado'''
    authorized = False
    try:
        authorized = eval(urllib.urlopen(url+"/"+user+"/"+psswd+"/auth").read())
    except:
        authorized = False
        print '\'except:'+str(authorized)+'\''
    if not authorized: print "Falha na autenticacao. \n"
    return authorized

def server_changes(user, psswd):
    try:
        new = urllib.urlopen(url+"/"+user+"/"+psswd+"/list")
        new = new.read()
        userpath = './myDropbox/'+user+'/'
        with open(userpath+'new.p','wb') as new_file:
            new_file.write(new)
        new = pickle.load(open(userpath+'new.p','rb'))
        os.remove(userpath+'new.p')
    except:
        new = old_server
    return new

def download(user, psswd, item, isfolder):
    if item == 'files.p':
        return
    print 'Baixando novo arquivo,', item
    try:
        userpath = './myDropbox/'+user+'/'
        if not os.path.exists(userpath):
            os.makedirs(userpath)
        if isfolder:
            os.makedirs(userpath+item)
        else:
            urllib.urlretrieve(url+"/"+user+"/"+psswd+"/download/"+item, filename=userpath+item)
    except:
        return 'Nao foi possivel baixar o arquivo'
    return


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
def local_changes(user):
    '''Checa se existe alguma mudanca no diretorio sendo observado'''
    files = {}
    userpath = './myDropbox/'+user+'/'
    if not os.path.exists(userpath):
        os.makedirs(userpath)
    lista = listFiles(userpath)
    for f in lista:
        try: files[f] = {'time':os.stat(userpath+f).st_mtime,'type':os.path.isdir(userpath+f)}
        except: 
            try: files[f] = old_local[f]
            except: files[f] = {'time':0,'type':None}
    return files


def upload(user, psswd, item, isfolder): 
    print 'Fazendo upload de novo item: ', item
    userpath = './myDropbox/'+user+'/'
    if not os.path.exists(userpath):
        os.makedirs(userpath)
    if not isfolder:
        files = {'file': open(userpath+item, 'rb')}
        requests.post(url+"/"+user+"/"+psswd+"/upload/"+item+"/file", files=files)
    else:
        requests.post(url+"/"+user+"/"+psswd+"/upload/"+item+"/folder")
    return

def update(user, psswd, server, local):
    global old_server, old_local

    changes = {}
    files = server.keys() + local.keys()
    vals = server.values() + local.values()
    for index in xrange(len(files)):
        item = files[index]
        changes[item] = {'status':None,'type':None}
        changes[item]['type'] = vals[index]['type']
        if (item in local) and (item not in server):
            changes[item]['status'] = 'Upload'
        if (item in server) and (item not in local):
            changes[item]['status'] = 'Download'
        if (item in server) and (item in local):
            if (server[item]['time'] - local[item]['time']) > 60.0: 
                print 'Conflito: "%s". Tratando arquivo mais recente como correto' % item 
                changes[item]['status'] = 'Download'
            if (local[item]['time'] - server[item]['time']) > 60.0:
                print 'Conflito: "%s". Tratando arquivo mais recente como correto' % item 
                changes[item]['status'] = 'Upload'
        if (item not in server) and (item in old_server):
            changes[item]['status'] = 'Delete local'
        if (item not in local) and (item in old_local):
            changes[item]['status'] = 'Delete server'
    
    for key in changes:
        if key == 'new.p':
            continue
        f_type = changes[key]['type']
        if changes[key]['status'] == 'Delete server': delete_server(user, psswd, key)
        if changes[key]['status'] == 'Delete local': delete_local(user, key)
        if changes[key]['status'] == 'Download': download(user, psswd, key, f_type)
        if changes[key]['status'] == 'Upload': upload(user, psswd, key, f_type)

    old_server = server
    old_local = local 
    return

def delete_server(user, psswd, item):
    urllib.urlopen(url+'/'+user+'/'+psswd+'/delete/'+item)
    print 'Removendo "%s" do servidor' % item
    return

def delete_local(user, item):
    userpath = './myDropbox/'+user+'/'
    try: os.rmdir(userpath+item)
    except: 
        try: os.remove(userpath+item)
        except: print 'Erro ao deletar arquivo'
    print 'Removendo', item
    return

def main():
    # auth
    logged = False
    while not logged:
        user = raw_input("Usuario: ")
        psswd = hashlib.sha512(getpass("Senha: ")).hexdigest()
        logged = auth(user, psswd)
    numfiles = urllib.urlopen(url+'/'+user+'/'+psswd+'/numfiles').read()
    print numfiles
    # main loop
    while True:
        update(user, psswd, server_changes(user, psswd), local_changes(user))
        sleep(t)

if __name__ == "__main__": 
    old_local = {}
    old_server = {}
    main()
