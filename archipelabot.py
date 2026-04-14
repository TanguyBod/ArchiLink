from websockets.asyncio.client import connect
import aiofiles
import json
from time import sleep
import uuid
import asyncio
from asyncio import Queue
import os
import discord
from discord import app_commands
from discord.ext import commands, tasks
from PlayerClient import PlayerClient
# All configuration will be defined in the config.json file.

config = json.load(open("config.json", "r"))

client_url = config["ArchipelagoConfig"]["client_url"]
client_port = config["ArchipelagoConfig"]["client_port"]

messages_to_send = Queue(maxsize=2000) # Queue of messages to send to the server, received from the discord bot

data_dir = "./data"
if not os.path.exists(data_dir) :
    os.makedirs(data_dir)
datapackage_path = f"{data_dir}/datapackage.json"
reversed_datapackage_path = f"{data_dir}/reversed_datapackage.json"
    
class TrackerClient() :
    tags : set[str] = {'TextOnly', 'Tracker', 'DeathLink'}
    version : dict[str, any] = {"major": 0, "minor": 6, "build": 0, "class": "Version"}
    items_handling: int = 0b000 # Does not receive any items
    
    def __init__(self) :
        self.client_url : str = config["ArchipelagoConfig"]["client_url"]
        self.client_port : str = config["ArchipelagoConfig"]["client_port"]
        self.password : str = config["ArchipelagoConfig"]["password"]
        self.password = self.password if self.password else ""
        self.slot_name : str = config["ArchipelagoConfig"]["bot_slot"]
        self.uuid : int = uuid.getnode()
        self.ap_connection = None
        self.player_db = PlayerDB()
        self.datapackage = None
        self.message_queue = asyncio.Queue(maxsize=2000)
        self.running = True
        self.nb_workers = 4
        self.lock = asyncio.Lock() # Lock to protect shared resources
        self.workers_started = False
        
    async def connect(self) :
        self.ap_connection = await connect(
            f"ws://{self.client_url}:{self.client_port}",
            max_size=None
        )

    async def run(self):
        while self.running:
            try:
                await self.connect()
                if not self.workers_started:
                    for _ in range(self.nb_workers):
                        asyncio.create_task(self.process_messages())
                    self.workers_started = True

                while self.running:
                    raw = await self.ap_connection.recv()
                    messages = json.loads(raw)
                    for message in messages:
                        await self.message_queue.put(message)

            except Exception as e:
                print(f"Connection error: {e}")
                await asyncio.sleep(5)
    
    async def process_messages(self):
        while self.running:
            try :
                message = await self.message_queue.get()
                print(message)
                if message["cmd"] == "RoomInfo" :
                    # Check DataPackage and send connect
                    await self.check_data_package()
                    await self.send_connect()
                if message["cmd"] == "DataPackage" :
                    # save DataPackage in a json, needed if bot is restarted
                    async with aiofiles.open(datapackage_path, "w", encoding="utf-8") as file:
                        await file.write(json.dumps(message, indent=2, ensure_ascii=False))
                    self.datapackage = message
                if message["cmd"] == "Connected" :
                    for slot, slot_info in message["slot_info"].items() :
                        player_slot = int(slot)
                        player_game = slot_info["game"]
                        player_name = slot_info["name"]
                        if player_game == "Archipelago" :
                            continue
                        print(f"Creating player {player_name} in slot {player_slot} playing {player_game}.")
                        self.player_db.create_player(player_slot, player_game, player_name)
                    # Reverse datapack now (otherwise games is an empty list)
                    await self.build_reverse_data_dict()
                    async with aiofiles.open(reversed_datapackage_path, "w", encoding="utf-8") as file:
                        await file.write(json.dumps(self.datapackage, indent=2, ensure_ascii=False))
                if message["cmd"] == "PrintJSON" :
                    await self.process_json_message(message)
            except Exception as e :
                print(f"Error processing message: {e}")
                continue

    async def process_json_message(self, message: dict) -> None :
        if message["type"] == "Chat" :
            data_list = message["data"]
            for data in data_list :
                await messages_to_send.put(data['text'])
        if message["type"] == "ItemSend" :
            msg_str = ""; flag = None; item_player = Item()
            msg_summary = []; player_recieving = None; player_sending = None
            for data in message["data"] :
                if data["text"].strip() in ["(", ")"] :
                    continue
                elif "type" not in data.keys():
                    msg_str += data["text"]
                elif data["type"] == "player_id" :
                    player_slot = int(data["text"])
                    player_sending = self.player_db.get_player_by_slot(player_slot)
                    msg_str += f"{player_sending.player_name}"
                    msg_summary.append(f"{player_sending.player_name}")
                    item_player.player_sending = player_sending
                elif data["type"] == "item_id" :
                    item_id = data["text"]
                    player_recieving = self.player_db.get_player_by_slot(int(data["player"]))
                    game_receiving = player_recieving.player_game
                    flag = data["flags"]
                    color = await get_ansi_color_from_flag(flag)
                    item_name = self.datapackage["data"]["games"][game_receiving]["id_to_item_name"][item_id]
                    msg_str += f"\u001b[0;{color}m{item_name}\u001b[0m"
                    msg_summary.append(item_name)
                    item_player.item_name = item_name
                    item_player.item_id = item_id
                    item_player.game = game_receiving
                    item_player.flag = flag
                elif data["type"] == "location_id" :
                    location_id = data["text"]
                    player_sending = self.player_db.get_player_by_slot(int(data["player"]))
                    game_sending = player_sending.player_game
                    location_name = self.datapackage["data"]["games"][game_sending]["id_to_location_name"][location_id]
                    msg_str += f"\nCheck: {location_name}"
                    msg_summary.append(location_name)
                    item_player.location_name = location_name
                    item_player.location_id = location_id
                else :
                    print(f"Unknown data type : {data['type']}")
            if player_recieving is None :
                raise ValueError(f"Player receiving item not found in message : {message}")
            if player_sending.player_slot != player_recieving.player_slot :
                print(f"Item sent from {player_sending.player_name} added to player {player_recieving.player_name} new items list.")
                async with self.lock:
                    player_recieving.new_items.append(item_player)
            await messages_to_send.put(msg_str)
        else :
            print(f"Unknown message type : {message['type']}")

    async def check_data_package(self) -> None :
        print("-- Checking DataPackage.")
        if os.path.exists(datapackage_path) :
            async with aiofiles.open(datapackage_path, "r") as f:
                self.datapackage = json.loads(await f.read())
            return
        payload = {
            'cmd': 'GetDataPackage'
        }
        await self.send_message(payload)
            
    async def send_connect(self) -> None:
        print("-- Sending `Connect` packet to log in to server.")
        payload = {
            'cmd': 'Connect',
            'game': '',
            'password': self.password,
            'name': self.slot_name,
            'version': self.version,
            'tags': list(self.tags),
            'items_handling': self.items_handling,
            'uuid': self.uuid,
        }
        await self.send_message(payload)

    async def send_message(self, message: dict) -> None :
        try :
            await self.ap_connection.send(json.dumps([message]))
        except Exception as e :
            print(f"Error sending message: {e}")
            
    async def build_reverse_data_dict(self):
        """
        Build a reverse data dict to allow efficient data retrieval.
        Reverse item_name_to_id and location_name_to_id to id_to_item_name
        and id_to_location_name.
        """
        
        if self.datapackage is None :
            raise ValueError(f"Trying to reverse datapackage but it is empty")
        reverse = {"cmd": "DataPackage", "data" : {"games" : {}}}
        games = self.datapackage["data"]["games"]
        played_games = self.player_db.get_all_played_games()
        for game_name, game_data in games.items():
            if game_name not in played_games :
                continue # No need to store data for unplayed games
            reverse["data"]["games"][game_name] = {
                "id_to_item_name": {},
                "id_to_location_name": {}
            }
            for item_name, item_id in game_data["item_name_to_id"].items():
                reverse["data"]["games"][game_name]["id_to_item_name"][str(item_id)] = item_name
            for location_name, location_id in game_data["location_name_to_id"].items() :
                reverse["data"]["games"][game_name]["id_to_location_name"][str(location_id)] = location_name
        self.datapackage = reverse

async def get_ansi_color_from_flag(flag: int) -> int :
    if flag is None :
        return 37
    elif flag & 0b001 :
        return 33 # ANSI code for yellow
    elif flag & 0b010 :
        return 34 # ANSI code for blue
    elif flag & 0b100 :
        return 31 # ANSI code for red
    else :
        return 37 # ANSI code for white

class Player :
    def __init__(self, 
                 player_slot : int,
                 player_game : str,
                 player_name : str,
                 discord_id : int = None
                 ) :
        self.player_slot = player_slot
        self.player_game = player_game
        self.player_name = player_name
        self.discord_id = discord_id
        self.new_items: list[Item] = [] # List of new items received, to be sent to discord when queried
        self.todolist: list[Item] = []
        self.allow_ping = True

class PlayerDB :
    def __init__(self) :
        self.players_by_slot: dict[int, Player] = {}
        self.players_by_name: dict[str, Player] = {}
        self.players_by_discord: dict[int, Player] = {}

    def create_player(self, 
                      player_slot : int, 
                      player_game : str, 
                      player_name : str, 
                      discord_id : int = None
                    ) -> Player :
        if player_slot in self.players_by_slot:
            raise ValueError(f"Player slot {player_slot} already exists.")
        player = Player(int(player_slot), player_game, player_name, discord_id)
        self.players_by_slot[player_slot] = player
        self.players_by_name[player_name] = player
        if discord_id is not None:
            self.players_by_discord[discord_id] = player
        return player

    def get_player_by_slot(self, player_slot : int) -> Player :
        return self.players_by_slot.get(player_slot)

    def get_player_by_name(self, player_name : str) -> Player :
        return self.players_by_name.get(player_name)

    def get_player_by_discord_id(self, discord_id : int) -> Player :
        return self.players_by_discord.get(discord_id)

    def get_all_players_names(self) -> list[str] :
        return [player.player_name for player in self.players_by_name.values()]
    
    def get_all_played_games(self) -> list[str] :
        return [player.player_game for player in self.players_by_name.values()]
    
    def get_all_discord_ids(self) -> list[int] :
        return [player.discord_id for player in self.players_by_discord.values() if player.discord_id is not None]

    def print_players(self) -> None :
        for player in self.players_by_name.values() :
            print(f"Player {player.player_name or 'Unknown'} in slot {player.player_slot or 'Unknown'} playing {player.player_game or 'Unknown'} registered to discord id {player.discord_id or 'Unknown'}.")

    def set_discord_id(self, player, discord_id):
        if player.discord_id:
            self.players_by_discord.pop(player.discord_id, None)
        player.discord_id = discord_id
        self.players_by_discord[discord_id] = player

class Item :
    def __init__(self,
                 item_name : str = None,
                 item_id : int = None,
                 game : str = None,
                 location_name : str = None,
                 location_id: int = None,
                 player_sending : Player = None,
                 player_recieving : Player = None,
                 flag : int = None
                 ) :
        self.item_name = item_name
        self.item_id = item_id
        self.game = game
        self.location_name = location_name
        self.location_id = location_id
        self.player_sending = player_sending
        self.player_recieving = player_recieving
        self.flag = flag

# Init player db and tracker :
tracker_client = TrackerClient()
player_client = PlayerClient("Adam")

# ==============================================================
#                     Discord Bot part
# ==============================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
NORMAL_CHANNEL_ID = config["DiscordConfig"]["normal_channel_id"]
ADMIN_CHANNEL_ID = config["DiscordConfig"]["admin_channel_id"]
APP_TOKEN = config["DiscordConfig"]["app_token"]
@bot.command()
async def hint(ctx, *, hint: str):
    try:
        print(f"player id : ${ctx.author.id}")
        player = await tracker_client.player_db.get_player_by_discord_id(ctx.author.id)
        print(f"player slot : ${player.player_slot}")
        player_client_instance = PlayerClient(player.player_name)
        await player_client_instance.connect()
        await player_client_instance.send_connect()
        data = await player_client_instance.send_hint(hint)
        ctx.send(f"data: {data}")
    except e:
        print(f"Error creating player: {e}")

@bot.command()
async def players(ctx):
    players = tracker_client.player_db.get_all_players_names()
    await ctx.send("test")

@bot.command()
async def register(ctx, player_name: str) :
    # Check if player name is valid
    if player_name not in tracker_client.player_db.get_all_players_names() :
        await ctx.send(f"Player name {player_name} not found. Please check the spelling and try again.\n\
Available player names are : {', '.join(tracker_client.player_db.get_all_players_names())}")
    elif tracker_client.player_db.get_player_by_name(player_name).discord_id is not None :
        player = tracker_client.player_db.get_player_by_name(player_name)
        await ctx.send(f"Player {player_name} is already registered by {player.discord_id}.\nIf you think this is an error, please contact the administrator.")
    else :
        # Get discord id of the user
        discord_id = ctx.author.id
        player = tracker_client.player_db.get_player_by_name(player_name)
        tracker_client.player_db.set_discord_id(player, discord_id)
        await ctx.send(f"Player {player_name} successfully registered to discord user {ctx.author.name}#{ctx.author.discriminator}.")

@bot.command()
async def unregister(ctx, player_name: str) :
    # Check if player name is valid
    if player_name not in tracker_client.player_db.get_all_players_names() :
        await ctx.send(f"Player name {player_name} not found. Please check the spelling and try again.\n\
Available player names are : {', '.join(tracker_client.player_db.get_all_players_names())}")
    else :
        player = tracker_client.player_db.get_player_by_name(player_name)
        if player.discord_id is None :
            await ctx.send(f"Player {player_name} is not registered to any discord user.")
        elif player.discord_id != ctx.author.id :
            await ctx.send(f"Player {player_name} is registered to another discord user. You cannot unregister it.\nIf you think this is an error, please contact the administrator.")
        else :
            tracker_client.player_db.set_discord_id(player, None)
            await ctx.send(f"Player {player_name} successfully unregistered from discord user {ctx.author.name}#{ctx.author.discriminator}.")

@bot.command()
async def new(ctx) :
    discord_id = ctx.author.id
    player = tracker_client.player_db.get_player_by_discord_id(discord_id)
    user = await bot.fetch_user(discord_id)
    if player is None :
        await ctx.send(f"You are not registered to any player. Please register first using `!register <player_name>` command.")
    elif len(player.new_items) == 0 :
        print(f"Player found : {player.player_name} but no new items to send.")
        # DM player if no new items, to avoid spamming the channel
        # Check if bot can DM the user
        if user.dm_channel is None :
            await user.create_dm() 
        await user.dm_channel.send("You have not received any new items since the last time you checked.")
    else :
        if user.dm_channel is None :
            await user.create_dm()
        print(f"Player found : {player.player_name} with {len(player.new_items)} new items to send.")
        msg = "```ansi\n"
        async with tracker_client.lock:
            items = list(player.new_items)
            player.new_items.clear()
        l1 = len(player.player_name) + 2
        l2 = max(len(item.item_name) for item in items) + 2
        l3 = max(len(item.player_sending.player_name) for item in items) + 2
        l4 = max(len(item.location_name) for item in items) + 2
        msg += f"{'You'.ljust(l1)} || {'Item'.ljust(l2)} || {'Sender'.ljust(l3)} || {'Location'.ljust(l4)}\n"
        for item in items :
            color = await get_ansi_color_from_flag(item.flag)
            msg += f"{player.player_name.ljust(l1)} || \u001b[0;{color}m{item.item_name.ljust(l2)}\u001b[0m || {item.player_sending.player_name.ljust(l3)} || {item.location_name.ljust(l4)}\n"
            if len(msg) > 1900 : # Discord message limit is 2000 characters, keep some margin
                msg += "```"
                await user.dm_channel.send(msg)
                msg = "```ansi\n"
        msg += "```"
        await user.dm_channel.send(msg)
        
@bot.command()
async def enableping(ctx) :
    discord_id = ctx.author.id
    player = tracker_client.player_db.get_player_by_discord_id(discord_id)
    if player is None :
        await ctx.send(f"You are not registered to any player. Please register first usign `!register <name>` command.")
    else :
        player.allow_ping = True
        await ctx.send(f"This discord bot can now ping you")
 
@bot.command()
async def disableping(ctx) :
    discord_id = ctx.author.id
    player = tracker_client.player_db.get_player_by_discord_id(discord_id)
    if player is None :
        await ctx.send(f"You are not registered to any player. Please register first usign `!register <name>` command.")
    else :
        player.allow_ping = False
        await ctx.send(f"This discord bot won't bother you anymore with pings")

@bot.command()
async def todo(ctx) :
    discord_id = ctx.author.id
    player = tracker_client.player_db.get_player_by_discord_id(discord_id)
    if player is None :
        await ctx.send(f"You are not registered to any player. Please register first usign `!register <name>` command.")
    elif player.todolist = []
        await ctx.send(f"All is good, nobody needs you")
    else :
        async with tracker_client.lock:
            items = list(player.todolist)
        msg = "```ansi\n Behold: the highly negotiated list of items your teammates absolutely needed\n\n"
        l1 = max(len(item.player_recieving.player_name) for item in items)
        l2 = max(len(item.item_name) for item in items) + 2
        l3 = max(len(item.location_name) for item in items) + 2
        msg += f"{'For'.ljust(l1)} || {'Item'.ljust(l2)} || {'Location'.ljust(l3)}\n"
        for item in items :
            msg += f"{item.player_recieving.player_name.ljust(l1)} || {item.item_name.ljust(l2)} || {item.location_name.ljust(l3)}"
            if len(msg) > 1900 : # Discord message limit is 2000 characters, keep some margin
                msg += "```"
                await ctx.send(msg)
                msg = "```ansi\n"
        msg += "```"
        await ctx.send(msg)

async def discord_sender(channel) :
    while True:
        try:
            msg = await messages_to_send.get()
            await channel.send(msg)
        except Exception as e:
            print(f"Error sending Discord message: {e}")
   
@bot.event
async def on_ready():
    channel = bot.get_channel(NORMAL_CHANNEL_ID) or await bot.fetch_channel(NORMAL_CHANNEL_ID)
    bot.loop.create_task(discord_sender(channel))

async def main():
    await asyncio.gather(
        #player_client.run(),
        tracker_client.run(),
        bot.start(APP_TOKEN)
    )

if __name__ == "__main__":
    asyncio.run(main())