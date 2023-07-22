import random
import string


class Room:
    """У класса комнаты имеются название, которое генерируется случайно,
    id выдаются комнатам по возрастанию,
    host (пользователь, который комнату создал) и
    members (клиенты, которые к ней подключились).
    """
    id_counter = 1
    host = None
    members = {}

    def __init__(self):
        self.id = self.id_counter
        self.id_counter += 1
        self.name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    @classmethod
    def increase_id_counter(cls):
        cls.id_counter += 1
        return cls.id_counter
