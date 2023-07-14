# demo_socket
import eventlet
import socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio)

socket_data = {"online": 0, "message": 0}


@sio.event
def connect(sid, environ):
    socket_data["online"] += 1
    socket_data["message"] += 1
    sio.emit("message", data=socket_data)
    sio.emit("message", to=sid, data={"content": "С подключением"})


@sio.event
def disconnect(sid):
    socket_data["online"] -= 1
    socket_data["message"] += 1
    sio.emit("message", data=socket_data)


@sio.on("message")
def in_com(sid, data):
    print(data)


eventlet.wsgi.server(
    eventlet.listen(('', 5000)), app
)
