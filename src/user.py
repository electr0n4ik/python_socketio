class User:
    """У пользователя есть id, имя, идентификатор его сессии, комната в которой он состоит,
    флаг is_online (по умолчанию True).
    Экземпляр класса создается при подключении пользователя к серверу.
    При подключении пользователю возвращаются его данные, содержащие все поля кроме sid"""

    def __init__(self, sid, name):
        self.id = f"id_{sid}"
        self.name = name
        self.session_id = sid
        self.room = None
        self.is_online = True
