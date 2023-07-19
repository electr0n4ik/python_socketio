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
            return "OK"

        @self.sio.event
        def disconnect(sid):
            user = self.users_dict.get(sid)
            if user:
                user.is_online = False
                if user.room:
                    self.sio.leave_room(sid)
                    room = user.room
                    del room.members[user.session_id]
            del self.users_dict[sid]

            self.sio.emit("disconnect", user.id)

        @self.sio.event
        def create_room(sid, environ):
            """При получении от клиента события create_room создание на сервере экземпляра “комнаты”
            с добавлением туда клиента-host.
            Клиенту при этом вернутся данные комнаты: id, название, хост, мемберы в формате json."""

            user = self.users_dict.get(sid)
            user.is_host = True
            self.room = Room()  # создаем новую комнату
            self.room.host = user.session_id  # назначаем хост комнате
            self.rooms_dict[self.room.id] = self.room  # добавляем комнату в словарь комнат
            user.room = self.room.host  # сохраняем хост комнаты у пользователя

            self.room.increase_id_counter()  # счетчик класса комнат увеличиваем на 1 после создания очередной комнаты

            self.sio.emit("create_room", {"room_id": self.room.id,
                                          "room_name": self.room.name,
                                          "host": self.room.host,
                                          "members": self.room.members}, to=sid)

        @self.sio.event
        def join_room(sid, data):
            """При получении от клиента события join_room присоединение к комнате.
            Клиенту при этом вернутся данные комнаты: id, название, хост, мемберы в формате json. """
            for key in self.rooms_dict.keys():

                if data.get("room_id") == str(key):

                    user_join = self.users_dict.get(sid)
                    room_join = self.rooms_dict.get(key)
                    user_join.room = room_join
                    room_join.members[user_join.session_id] = user_join.name

                    self.sio.emit("join_room", {"room_id": room_join.id,
                                                "room_name": room_join.name,
                                                "host": room_join.host,
                                                "members": room_join.members}, to=sid)

                    self.sio.emit("join_room", {"room_id": room_join.id,
                                                "room_name": room_join.name,
                                                "host": room_join.host,
                                                "members": room_join.members}, to=room_join.host)

                else:
                    self.sio.emit("message", data={"content": "Не указан ID комнаты или комната не существует!"})

        @self.sio.event
        def leave_room(sid, environ):
            """ При получении от клиента события leave_room покидание комнаты.
            При этом хост не может покинуть комнату. Такая вот у него грустная жизнь."""
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

        @self.sio.event
        def message_room(sid, data):

            """ При получении от хоста события message_room происходит рассылка сообщения всем мемберам в комнате.
            data = {"message_room": "message"}"""
            user_host = self.users_dict[sid]
            message_host = data.get("message")
            room_id = data.get("room_id")

            if user_host.is_host:
                for key in self.rooms_dict.keys():
                    if room_id == str(key):
                        self.room_message = self.rooms_dict.get(key)

                        for user in self.room_message.members.keys():
                            # self.sio.emit("message", {"message": message_host}, room=self.room_message.host)
                            self.sio.emit("message", {"message": message_host}, to=user)
            else:
                self.sio.emit("message", "Только host может рассылать сообщения.", to=sid)

        @self.sio.event(namespace="/api/rooms")
        def get_list_rooms(sid, data):
            # self.sio.connect("https://localhost:8000/api/rooms")

            for room in self.rooms_dict.values():
                self.sio.emit("message", {"name_room": room.name,
                                          "host_room": room.host}, namespace="/api/rooms")

                self.sio.emit("message", {"count_members": len(room.members)}, namespace="/api/rooms")

    def run(self, host, port):
        eventlet.wsgi.server(eventlet.listen((host, port)), self.app)
