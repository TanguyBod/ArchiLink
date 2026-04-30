from archipelago.base_client import ArchipelagoClient
import asyncio

class TrackerClient(ArchipelagoClient) :
    def __init__(self, 
                 config,
                 logger,
                 player_name):
        super().__init__(config, logger)
        self.tags = set(['Tracker'])
        self.slot_name = player_name
        self.finished_event = asyncio.Event()
        self.total_locations = -1
        self.checked_locations = -1
        
    async def process_messages(self) :
        while self.running :
            try :
                message = await self.message_queue.get()
                if message["cmd"] == "RoomInfo" :
                    await self.send_connect()
                if message["cmd"] == "Connected" :
                    # extract missing_locations and checked locations field length
                    missing_locations = message["missing_locations"]
                    checked_locations = message["checked_locations"]
                    self.total_locations = len(missing_locations) + len(checked_locations)
                    self.checked_locations = len(checked_locations)
                    self.logger.info(f"Tracker client {self.slot_name} connected to server. Informations retrieved")
                    self.running = False # Running = False to stop workers after retrieving the informations we need to compute the checks
                    self.finished_event.set()
            except Exception as e :
                self.logger.error(f"Error processing message (TrackerClient): {e}")
                continue
            