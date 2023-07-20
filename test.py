import eventlet
import socketio
from flask import Flask, send_file

app = Flask(__name__)
sio = socketio.Server()


@app.route('/open_file')
def open_file():
    # Открываем файл и возвращаем его клиенту
    file_path = 'path_to_your_file'
    return send_file(file_path)


@app.route('/')
def index():
    # Обработка других запросов
    return 'Hello, World!'


@sio.event
def connect(sid, environ):
    print('Подключено:', sid)


@sio.event
def disconnect(sid):
    print('Отключено:', sid)


if __name__ == '__main__':
    app = socketio.Middleware(sio, app)
    eventlet.wsgi.server(eventlet.listen(('localhost', 8080)), app)
