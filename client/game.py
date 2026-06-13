import threading
import queue
import pygame
from websockets import ClientConnection
from client.states.state import State
from common import messages

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pong")
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = None
        self.connection: ClientConnection | None = None
        self.player_id = 1
        self.is_connected = False
        self.local_test = False
        self.net_queue = queue.Queue()
        self.send_queue = queue.Queue()
        self._net_thread = None
        self._net_stop = threading.Event()

    def change_state(self, state: State):
        self.state = state

    def close_connection(self):
        # Stop network receiver first, which will also close the socket
        try:
            self.stop_network_receiver()
        except Exception:
            pass
        if self.connection is not None:
            try:
                conn = self.connection.close()
            except Exception:
                pass
            finally:
                self.connection = None
                self.is_connected = False

    def start_network_receiver(self):
        if self._net_thread and self._net_thread.is_alive():
            return
        self._net_stop.clear()
        self._net_thread = threading.Thread(target=self._network_loop, daemon=True)
        self._net_thread.start()

    def stop_network_receiver(self):
        self._net_stop.set()
        # close connection to interrupt blocking recv
        try:
            if self.connection is not None:
                conn = self.connection.close()
        except Exception:
            pass
        if self._net_thread:
            self._net_thread.join(timeout=1)
            self._net_thread = None

    def _network_loop(self):
        try:
            while not self._net_stop.is_set() and self.connection is not None:
                try:
                    raw = self.connection.recv()
                except Exception as e:
                    # signal network error to main thread
                    self.net_queue.put(e)
                    break

                try:
                    msg = messages.decode(raw)
                except Exception as e:
                    # decoding error
                    self.net_queue.put(e)
                    continue

                self.net_queue.put(msg)
        finally:
            self._net_stop.set()

    def send_messages(self):
        if self.connection is None:
                print("No connection found. Failed to send messages")
                self.send_queue = queue.Queue()
                return

        while not self.send_queue.empty():
            msg = self.send_queue.get_nowait()
            result = self.connection.send(msg)
            

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            # Process all pending network messages first
            try:
                while True and self.state is not None:
                    self.state.handle_message(self.net_queue.get_nowait())
            except queue.Empty:
                pass

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                if self.state is not None:
                    self.state.handle_event(event) # Handles inputs

            if self.state is not None:
                self.state.update(dt) # Handles internal data changes
                self.state.draw(self.screen) # Render based on internal data
            
            self.send_messages()
            pygame.display.flip()

        self.close_connection()
        pygame.quit()
