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

        self.rooms = {}
        self.users = {}

        self.register_events()

    def register_events(self):

        @self.sio.event
        def connect(sid, environ):

            user = User(sid)
            self.users[sid] = user
            self.clients_count += 1

            self.sio.emit("message", user.id, to=sid)

        @self.sio.event
        def disconnect(sid):
            user = self.users.get(sid)
            if user:
                user.is_online = False
                if user.room:
                    self.leave_room(sid)
                del self.users[sid]

                self.clients_count -= 1

        @self.sio.on("create_room")
        def create_room(sid, environ):
            print("Ok")
            user = self.users.get(sid)
            if user:
                room = Room(user)  # host
                self.rooms[room.id] = room
                user.room = room
                self.sio.emit("create_room", {"room_id": room.id, "room_name": room.name}, to=sid)
                print(sid, user.id, room.id, room.name)

        @self.sio.on("join_room")
        def join_room(sid, data):
            room_id = data.get("room_id")
            print("Ok_join", sid, room_id)
            # user = self.users.get(sid)
            # if user:
            #     room = self.rooms.get(room_id)
            #     if room:
            #         user.room = room
            #         room.members["user"] = user
            #         self.sio.emit("user_joined", {"room_id": room.id, "user_id": user.id}, room=room.id)

        @self.sio.on("leave_room")
        def leave_room(sid):
            user = self.users.get(sid)
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
