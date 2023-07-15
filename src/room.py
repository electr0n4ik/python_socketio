import random
import string


class Room:
    """У класса комнаты название, которое генерируется случайно
    и id выдаются комнатам по возрастанию,
    хост (пользователь который комнату создал) и
    мемберы (клиенты которые к ней подключились).
    """
    id_counter = 1
    members = {"default": "anonim"}

    def __init__(self, host):
        self.id = self.id_counter
        self.id_counter += 1
        self.name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        self.host = host
        self.members = self.members
