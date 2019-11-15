from usfpes import app
import socket

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

if __name__ == '__main__':
    app.run(debug=True,host=IPAddr,port='8000')
