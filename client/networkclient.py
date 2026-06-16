import queue
import threading
from common import messages
from common.messages import Message
from websockets.sync.client import connect

class NetworkClient:
    def __init__(self, url):
        self.url = url
        self.incoming_queue = queue.Queue()
        self.outgoing_queue = queue.Queue()
        self.running = False
        self._thread = None

    def start_network_receiver(self):
        if self.running or (self._thread and self._thread.is_alive()):
            return
        self.running = True
        self._thread = threading.Thread(target=self._network_loop, daemon=True)
        self._thread.start()

    def stop_network_receiver(self):
        self.running = False

    def send(self, message: Message):
        self.outgoing_queue.put(messages.encode(message))

    def poll(self):
        while not self.incoming_queue.empty():
            yield self.incoming_queue.get()

    def _network_loop(self):
        try:
            with connect(self.url) as ws:
                while self.running:
                    try:
                        # Timeout is needed here because otherwise this can wait forever
                        raw = ws.recv(timeout=0.05)
                        msg = messages.decode(raw)
                        self.incoming_queue.put(msg)
                    except TimeoutError:
                        pass
                    except messages.DecodeError as e:
                        self.incoming_queue.put(f"Decode Error: {e}")

                    while not self.outgoing_queue.empty():
                        ws.send(self.outgoing_queue.get())
        except Exception as e:
            # connect() failed or the socket died mid-send/recv;
            # signal the error to the main thread
            self.incoming_queue.put(e)
        finally:
            # always clear the flag so the start guard can restart later
            self.running = False
