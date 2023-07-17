
import eventlet

from src.socketio_manager import SocketIOManager


if __name__ == '__main__':
    server = SocketIOManager()
    server.run('localhost', 5000)


