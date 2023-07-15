import socketio


class SocketioManager:
    """Класс отвечает за управление розеткой"""

    def __int__(self):
        pass

    @staticmethod
    def app():
        sio = socketio.Server()
        return socketio.WSGIApp(sio)

# socket_data = {"online": 0, "message": 0}
#
#
# # событие подключения
# @sio.event
# def connect(sid, environ):
#     socket_data["online"] += 1
#     socket_data["message"] += 1
#     sio.emit("message", data=socket_data)
#     sio.emit("message", to=sid, data={"content": "С подключением"})
#
#
# # событие отключения
# @sio.event
# def disconnect(sid):
#     socket_data["online"] -= 1
#     socket_data["message"] += 1
#     sio.emit("message", data=socket_data)
#
#
# # событие отправки сообщения
# @sio.on("message")
# def in_com(sid, data):
#     print(data)

# асинхронная функция
# @sio.event
# async def message(data):
# print('I received a message!')
