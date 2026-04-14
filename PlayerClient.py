import uuid
from websockets.asyncio.client import connect
import json
import asyncio
config = json.load(open("config.json", "r"))
password = config["ArchipelagoConfig"]["password"]
client_url = config["ArchipelagoConfig"]["client_url"]
client_port = config["ArchipelagoConfig"]["client_port"]
version : dict[str, any] = {"major": 0, "minor": 6, "build": 0, "class": "Version"}
class PlayerClient :
    def __init__(self,slot:str):
        self.slot:str = slot
        self.client_url = client_url
        self.client_port = client_port
        self.uuid : int = uuid.getnode()
        self.password = password
        self.password = self.password if self.password else ""

    async def connect(self) :
        self.ap_connection = await connect(
            f"ws://{self.client_url}:{self.client_port}",
            max_size=None
        )
    async def send_connect(self) -> None:
        print("-- Sending `Connect` packet to log in to server.")
        payload = {
            'cmd': 'Connect',
            'game': '',
            'password': self.password,
            'name': self.slot,
            'version': version,
            'tags': ["TextOnly"],
            'items_handling': 0b000,
            'uuid': self.uuid,
        }
        await self.send_message(payload)
    async def send_message(self, message: dict) -> None :
        try :
            print("sending message ")
            return await self.ap_connection.send(json.dumps([message]))
        except Exception as e :
            print(f"Error sending message: {e}")
    async def send_hint(self,item:str):
        payload =   {
            "cmd": "Say",
            "text": f"!hint {item}"
        }
        await self.send_message(payload)
        return await self.run()
    async def run(self):
        try:
            while True:
                raw_message = await asyncio.wait_for(self.ap_connection.recv(), timeout=5)
                messages = json.loads(raw_message)

                for message in messages:
                    if message.get("cmd") == "PrintJSON":
                        return message
        except TimeoutError:
            return None