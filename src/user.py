class User:
    """У пользователя имеются id, имя, идентификатор его сессии, комната в которой он состоит,
    статус is_online (по умолчанию True).
    Экземпляр класса создается при подключении пользователя к серверу.
    При подключении пользователю возвращаются его данные, содержащие все поля кроме sid"""
    number = 1

    def __init__(self, sid):
        self.id = f"id_{sid}"
        self.name = f"nickname_{self.number}"
        self.session_id = sid
        self.room = None
        self.is_online = True
        self.is_host = False

        User.number_up()

    def get_info(self):
        return {"User": {"id": {self.id}, "name": {self.name}}}

    @classmethod
    def number_up(cls):
        cls.number += 1
        return cls.number
