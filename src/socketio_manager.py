import socketio
import eventlet

from src.room import Room
from src.user import User

from flask import Flask


class SocketIOManager:
    """Класс отвечает за управление розеткой"""
    app_flask = Flask(__name__)
    rooms_dict = {}
    users_dict = {}

    def __init__(self):
        self.sio = socketio.Server()
        self.room = None
        self.register_events()

    @staticmethod
    @app_flask.route("/api/room")
    def handle_request():
        dict_rooms = {}
        for room in SocketIOManager.rooms_dict.values():
            dict_rooms[room.name] = room.host

        return f"<p>Комнаты {dict_rooms}</p>" \
               f"<p>Количество подключенных пользователей - {len(SocketIOManager.users_dict)}</p>"

    def register_events(self):

        @self.sio.event
        def connect(sid, data):
            """После подключения юзера, создаем экземпляр юзера,
            добавляем его в словарь юзеров,
            получаем информацию о юзере методом класса юзера,
            отправляем сообщение юзеру о нем"""
            user = User(sid)
            self.users_dict[sid] = user
            user_info = f"{user.get_info()}"  # добавил в f-строку, чтобы не выходила ошибка сериализации в json
            self.sio.emit("message", user_info, to=sid)

        @self.sio.event
        def disconnect(sid):
            """После отключения юзера получаем экземпляр юзера из словаря юзеров,
            меняем статус юзера в его экземпляре,
            вызываем метод выхода юзера из комнаты,
            удаляем юзера из словаря присутствующих в комнате,
            """
            user = self.users_dict.get(sid)
            if user:
                user.is_online = False
                if user.room:
                    # SocketIOManager.register_events(leave_room(sid))
                    self.sio.leave_room(sid, user.room)
                    room = user.room
                    del room.members[user.session_id]
            del self.users_dict[sid]

            self.sio.emit("disconnect", user.id)

        @self.sio.on("room/host")
        def create_room(sid, data):
            """При получении от клиента события room/host создание на сервере экземпляра “комнаты”
            с добавлением туда клиента-host, клиенту при этом вернутся данные комнаты:
            id, room_name, host, members в формате json.

            От себя решил добавить настройку при создании комнаты:
            Это указывать максимальное количество участников
            Полезная фича ИМХО"""

            user = self.users_dict.get(sid)

            # в будущем кнч необходимо прописать обработку приема ТОЛЬКО целых чисел или что-нибудь подобное
            quantity_users = int(data.get("max_quantity"))

            if not user.is_host:

                user.is_host = True
                self.room = Room(quantity_users)  # создаем новую комнату
                self.room.host = user.session_id  # назначаем хост комнате
                self.rooms_dict[self.room.id] = self.room  # добавляем комнату в словарь комнат
                user.room = self.room.host  # сохраняем хост комнаты у пользователя

                # Когда подключается юзер к серверу, для него автоматически создается комната
                # поэтому sid-создателя-комнаты и host комнаты будут одинаковыми.
                # Значит комнату без юзеров не создать ИМХО
                self.sio.enter_room(sid, self.room.host)

                self.room.increase_id_counter()  # счетчик комнат увеличиваем на 1 после создания очередной комнаты

                self.sio.emit("message", {"room_id": self.room.id,
                                          "room_name": self.room.name,
                                          "host": self.room.host,
                                          "max_quantity_users": self.room.max_quantity,
                                          # в будущем можно добавить фичу, при которой,
                                          # хост сможет сам добавлять юзеров в комнату
                                          "members": self.room.members}, to=sid)

            else:
                self.sio.emit("message", "One user - one create room!", to=sid)

        @self.sio.on("room/join")
        def join_room(sid, data):
            """При получении от клиента события room/join {room_id: … } присоединение к комнате,
            клиенту при этом вернутся данные комнаты: id, name, host, members в формате json"""
            for key in self.rooms_dict.keys():

                if data.get("room_id") == str(key):
                    """полученный id присутствует в словаре комнат?"""

                    user_join = self.users_dict.get(sid)
                    room_join = self.rooms_dict.get(key)

                    if room_join.max_quantity == len(room_join.members):
                        self.sio.emit("message", data={"content": "В комнате нет свободных мест!"})
                        return None

                    user_join.room = room_join
                    room_join.members[user_join.session_id] = user_join.name

                    self.sio.enter_room(sid, room_join.host)

                    self.sio.emit("message", data={"room_id": room_join.id,
                                                   "room_name": room_join.name,
                                                   "host": room_join.host,
                                                   "members": room_join.members}, to=sid)
                    return None

                else:
                    self.sio.emit("message", data={"content": "Не указан ID комнаты!"
                                                              "Обратитесь в тех. поддержку!"})
                    return None
            self.sio.emit("message", data={"content": "Комната не найдена!"
                                                      "Обратитесь в тех. поддержку!"})

        @self.sio.on("room/leave")
        def leave_room(sid, data):
            """ При получении от клиента события room/leave юзер покидает комнату"""
            user_leave = self.users_dict.get(sid)

            if user_leave and user_leave.room:
                # юзер существует? юзер в комнате?
                room = user_leave.room

                if user_leave.is_host:
                    # юзер, который выходит, host?
                    self.sio.emit("message", "host не может покинуть комнату", to=sid)
                    return None

                user_leave.room = None

                del room.members[user_leave.session_id]

                self.sio.leave_room(sid, self.room.host)

                self.sio.emit("message", {"room_id": room.id, "user_id_left": user_leave.id}, to=room.host)
            else:
                self.sio.emit("message", "Вы не в комнате!"
                                         "Без паники, мы не на Титанике!", to=sid)

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

        @self.sio.event(namespace="/api/room")
        def connect(sid, data):
            self.app_flask.run("localhost", 5000)

            for room in self.rooms_dict.values():
                self.sio.emit("message", {"name_room": room.name,
                                          "host_room": room.host}, namespace="/api/rooms")

                self.sio.emit("message", {"count_members": len(room.members)}, namespace="/api/rooms")

    def run(self, host, port):
        app = socketio.Middleware(self.sio, self.app_flask)
        eventlet.wsgi.server(eventlet.listen((host, port)), app)
