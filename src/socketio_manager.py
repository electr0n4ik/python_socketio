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

        self.rooms_dict = {}
        self.room = None
        self.users_dict = {}

        self.register_events()

    def register_events(self):

        @self.sio.event
        def connect(sid, environ):

            user = User(sid)
            self.users_dict[sid] = user

            self.sio.emit("connect", user.id, to=sid)

        @self.sio.event
        def disconnect(sid):
            user = self.users_dict.get(sid)
            print(1)
            if user:
                user.is_online = False
                print(2)
                if user.room:
                    # self.sio.leave_room(sid)
                    print(3)

            del self.users_dict[sid]

            self.sio.emit("disconnect", user.id)

        @self.sio.on("create_room")
        def create_room(sid, environ):

            user = self.users_dict.get(sid)

            self.room = Room()  # создаем новую комнату
            self.room.host = user.session_id  # назначаем хост комнате
            self.rooms_dict[self.room.id] = self.room  # добавляем комнату в словарь комнат
            user.room = self.room.host  # сохраняем хост комнаты у пользователя

            self.room.increase_id_counter()  # счетчик класса комнат увеличиваем на 1 после создания очередной комнаты

            self.sio.emit("create_room", {"room_id": self.room.id, "room_name": self.room.name}, to=sid)

        @self.sio.on("join_room")
        def join_room(sid, data):

            for key in self.rooms_dict.keys():

                if data.get("room_id") == str(key):

                    user_join = self.users_dict.get(sid)

                    room_join = self.rooms_dict.get(key)
                    user_join.room = room_join
                    room_join.members[user_join.session_id] = user_join

                    self.sio.emit("join_room",
                                  {"room_id": room_join.host, "user_id": sid},
                                  room=room_join.host)
                    self.sio.emit("join_room",
                                  "Hello!",  # приветствие пользователя при его подключении к комнате
                                  to=sid)

                else:
                    self.sio.emit("message", data={"content": "Не указан ID комнаты или комната не существует!"})

        @self.sio.on("leave_room")
        def leave_room(sid, environ):
            user_leave = self.users_dict.get(sid)

            if user_leave and user_leave.room:
                room = user_leave.room

                if user_leave.room == room:
                    self.sio.emit("message", "host не может покинуть комнату", room=room)
                    return None

                user_leave.room = None
                del room.members[user_leave]
                self.sio.emit("user_left", {"room_id": room.id, "user_id": user_leave.id}, room=room.id)
            else:

                self.sio.emit("message", "Вы не в комнате!", to=sid)

    def get_user_data(self, sid):

        if self.users_dict.get(sid):
            user = self.users_dict.get(sid)
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
