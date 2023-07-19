import socketio
import eventlet

from src.room import Room
from src.user import User


class SocketIOManager:
    """Класс отвечает за управление розеткой"""

    def __init__(self):
        self.sio = socketio.Server()
        self.app = socketio.WSGIApp(self.sio, static_files={
            "/": "./public/"
        })

        self.clients_count = 1
        self.rooms_dict = {}
        self.room = None
        self.users_dict = {}

        self.register_events()

    def register_events(self):

        @self.sio.event
        def connect(sid, environ):

            user = User(sid)
            self.users_dict[sid] = user
            self.clients_count += 1

            self.sio.emit("connect", user.id, to=sid)

        @self.sio.event
        def disconnect(sid):
            user = self.users_dict.get(sid)
            if user:
                user.is_online = False
                if user.room:
                    self.leave_room(sid)
                del self.users_dict[sid]

                self.clients_count -= 1

        @self.sio.on("create_room")
        def create_room(sid, environ):

            user = self.users_dict.get(sid)

            self.room = Room()  # создаем новую комнату
            self.room.host = user.session_id  # назначаем хост комнате
            self.rooms_dict[self.room.id] = self.room.host  # добавляем комнату в словарь комнат
            user.room = self.room.host  # сохраняем хост комнаты у пользователя

            self.room.increase_id_counter()  # счетчик класса комнат увеличиваем на 1 после создания очередной комнаты

            self.sio.emit("create_room", {"room_id": self.room.id, "room_name": self.room.name}, to=sid)

        @self.sio.on("join_room")
        def join_room(sid, data):

            for key in self.rooms_dict.keys():

                if data.get("room_id") == str(key):

                    user = self.users_dict.get(sid)

                    room = self.rooms_dict.get(key)
                    user.room = room

                    # room.members[user.session_id] = user  # TODO исправить
                    self.sio.emit("message", {"room_id": room, "user_id": user.id}, room=room)

                else:
                    self.sio.emit("message", data={"content": "Не указан ID комнаты или комната не существует!"})

        @self.sio.on("leave_room")
        def leave_room(sid):
            user = self.users_dict.get(sid)
            if user and user.room:
                room = user.room
                user.room = None
                room.members.remove(user)
                self.sio.emit("user_left", {"room_id": room.id, "user_id": user.id}, room=room.id)

        @self.sio.event(namespace='/chat')
        def my_custom_event():
            print("Ку")

        # @self.sio.on('connect', namespace='/chat')
        # def on_connect():
        #     print("I'm connected to the /chat namespace!")

    def get_user_data(self, sid):
        user = self.users.get(sid)
        if user:
            return {
                "id": user.id,
                "name": user.name,
                "room": user.room.id if user.room else None,
                "is_online": user.is_online
            }
        return None

    def run(self, host, port):
        eventlet.wsgi.server(eventlet.listen((host, port)), self.app)

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


# асинхронная функция
# @sio.event
# async def message(data):
# print("I received a message!")
