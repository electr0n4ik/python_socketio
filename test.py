# [ ] Данные хранятся в словаре
# [ ] Пользователь может получить свои данные
# [ ] Пользователь может поменять свои данные
# [ ] Пользователь может отключиться, переподключиться и иметь доступ к своим данным
#
# Бонус
#
# [ ] При подлючении и отключении статус пользователя обновляется (online / offline)

import eventlet
import socketio

sio = socketio.Server()
app = socketio.WSGIApp(sio)

user_storage = {}  # ключ - pk пользователя , значение - словарь c ключами user_pk, name, status, sid


def get_next_pk(storage):
    return len(storage.keys()) + 1


@sio.event
def connect(sid, data):
    pass


@sio.on("user/join")
def user_join(sid, data): # {name: , status:}

    user_pk = get_next_pk(user_storage)
    name = data.get("name")
    status = data.get("status")
    sid = sid

    user_storage[user_pk] = {"user_pk": user_pk, "name": name, "status": status, "sid": sid}

    sio.emit("message", to=sid, data={"user_pk": user_pk})


@sio.on("profile/get")
def get_profile(sid, data):
    user_pk = data.get("user_pk")

    if not user_pk:
        sio.emit("message", to=sid, data={"message": "не передан id для получения"})
        return

    if user_pk not in user_storage:
        sio.emit("message", to=sid, data={"message": "нет такого id"})
        return

    user_data = user_storage[user_pk]
    sio.emit("message", to=sid, data=user_data)


@sio.on("user/reconnect")
def get_profile(sid, data):

    user_pk = data.get("user_pk")

    if user_pk in user_storage:
        user_storage[user_pk]["sid"] = sid

    sio.emit("message", to=sid, data={"message": "you are reconnected"})


eventlet.wsgi.server(
    eventlet.listen(('', 5000)), app
)

# @sio.on("rooms/join")
# def join_room(sid, data):
#     room_name = data.get("room_name")
#     if room_name:
#         sio.enter_room(sid, room_name)
#         sio.save_session(sid, {"room_name": room_name})
#         sio.emit("message", to=sid, data={"content": "you joined the room"})
#         print(sid, "joined room", room_name)
#     else:
#         sio.emit("message", to=sid, data={"content": "select a room to join"})
#
#
# @sio.on("rooms/send")
# def sent_to_room(sid, data):
#     message = data["message"]
#     room_name = sio.get_session(sid).get("room_name")
#     if room_name:
#         sio.emit("message", room=room_name, data={"content": message})
#         print(sid, "send message to room", room_name)
#     else:
#         sio.emit("message", to=sid, data={"content": "no room is selected"})
#
#
# @sio.on("rooms/get_rooms")
# def get_rooms(sid, data):
#     my_rooms = sio.rooms(sid=sid)
#     sio.emit("message", to=sid, data={"my_rooms": my_rooms, "sid": sid})
#
#
# eventlet.wsgi.server(
#     eventlet.listen(('', 5000)), app
# )
