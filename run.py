
import eventlet

from src.socketio_manager import SocketioManager


if __name__ == "__main__":

    socketio = SocketioManager
    app = socketio.app

    eventlet.wsgi.server(
        eventlet.listen(('', 5000)), app
    )
