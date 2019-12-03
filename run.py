from usfpes import app,basedir
import socket
#before blueprinting
hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

if __name__ == '__main__':
    #print(basedir)
    app.run(debug=True,host='127.0.0.1',port='8000')
