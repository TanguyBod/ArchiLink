import asyncio
from abc import ABC, abstractmethod
import uuid
import json
import logging
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosedOK

class ArchipelagoClient(ABC) :
    version : dict[str, any] = {"major": 0, "minor": 6, "build": 7, "class": "Version"}
    items_handling: int = 0b000 # Does not receive any items
    
    def __init__(self, config: dict[str, any], logger: logging.Logger) :
        self.client_url : str = str(config["ArchipelagoConfig"]["client_url"])
        self.client_port : str = str(config["ArchipelagoConfig"]["client_port"])
        self.self_hosted : bool = bool(config["ArchipelagoConfig"]["self_hosted"])
        self.password : str = str(config["ArchipelagoConfig"]["password"])
        self.password = self.password if self.password else ""
        self.uuid : int = uuid.getnode()
        self.ap_connection = None
        self.message_queue = asyncio.Queue(maxsize=2000)
        self.slot_name : str = ""
        self.tags : set[str] = set()
        self.running = True
        self.nb_workers = 6
        self.workers_started = False
        self.game = ''
        self.worker_tasks = []
        self.logger = logger
        self.failed_connection_attempts = 0
    
    async def connect(self) :
        if self.self_hosted :
            self.ap_connection = await connect(
            f"ws://{self.client_url}:{self.client_port}",
            max_size=None
            )
        else :
            self.ap_connection = await connect(
                f"wss://{self.client_url}:{self.client_port}",
                max_size=None
            )
        
    async def send_message(self, message: dict) -> None :
        try :
            await self.ap_connection.send(json.dumps([message]))
        except Exception as e :
            print(f"Error sending message: {e}")
    
    async def send_connect(self) -> None:
        self.logger.info("-- Sending `Connect` packet to log in to server.")
        payload = {
            'cmd': 'Connect',
            'game': self.game,
            'password': self.password,
            'name': self.slot_name,
            'version': ArchipelagoClient.version,
            'tags': list(self.tags),
            'items_handling': ArchipelagoClient.items_handling,
            'uuid': self.uuid,
        }
        await self.send_message(payload)
        
    async def run(self):
        while self.running:
            try:
                self.logger.info("Connecting to Archipelago server at " + self.client_url + ":" + self.client_port)
                await self.connect()
                if not self.workers_started:
                    for _ in range(self.nb_workers):
                        task = asyncio.create_task(self.process_messages())
                        self.worker_tasks.append(task)
                    self.workers_started = True

                while self.running:
                    raw = await self.ap_connection.recv()
                    messages = json.loads(raw)
                    for message in messages:
                        self.logger.debug(f"Received message from server :\n{message}")
                        await self.message_queue.put(message)
            except ConnectionClosedOK:
                self.logger.info("Connection closed gracefully.")
                self.running = False
                break
            except asyncio.CancelledError:
                self.logger.info("Archipelago client shutting down...")
                self.running = False
                # nettoyage éventuel
                if self.ap_connection:
                    await self.ap_connection.close()
                raise
            except Exception as e:
                self.logger.error(f"Connection error: {e}")
                await asyncio.sleep(60)  # Wait before trying to reconnect
                self.failed_connection_attempts += 1
                # If more than 5 failed connection attempts and not self-hosted, stop trying to reconnect
                # This is to prevent infinite reconnection attempts if the server is down or the URL is incorrect
                if self.failed_connection_attempts >= 5:
                    if not self.self_hosted:
                        self.logger.error("Too many failed connection attempts. Stopping reconnection attempts.")
                        await self.stop()
        self.logger.info("Archipelago tracker stopped on endpoint " + self.client_url + ":" + self.client_port)

    async def stop(self) :
        self.logger.info("Stopping Archipelago tracking on endpoint " + self.client_url + ":" + self.client_port)
        self.running = False
        for task in getattr(self, "worker_tasks", []):
            task.cancel()
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        if self.ap_connection:
            await self.ap_connection.close()
            
    async def start(self) :
        self.logger.info("Starting Archipelago tracking on endpoint " + self.client_url + ":" + self.client_port)
        self.running = True
        await self.run()
    
    @abstractmethod
    async def process_messages(self) :
        pass
