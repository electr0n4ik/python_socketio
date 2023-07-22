
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
def reconnect_profile(sid, data):

    user_pk = data.get("user_pk")

    if user_pk in user_storage:
        user_storage[user_pk]["sid"] = sid

    sio.emit("message", to=sid, data={"message": "you are reconnected"})


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
