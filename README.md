# ArchiLink

A Discord bot designed to interact with an **Archipelago Multiworld** session directly from your server.

While existing tools (such as [Bridgeipelago](https://github.com/Quasky/bridgeipelago/tree/main)) already provide item tracking and hint management, **ArchiLink focuses on improving coordination between players by introducing cross-player todo lists**. This allows players to explicitly communicate needs and priorities, making multiworld collaboration significantly smoother and more structured.
ArchiLink can handle multiple worlds, each of them require a seperated discord channel.

Players can track progress, request hints, and — most importantly — **assign items or goals to other players via shared todo lists** directly from Discord.

Its main features are the following:

- 📦 View all collected items across players  
- 🧾 Create and manage todo lists for other players to communicate needs  
- 🔍 Request in-game hints directly from Discord  
- 📝 Add hints or items to another player's todo list  
- 🔔 Get notified when your required item is found  
- 🤝 Improve coordination and teamwork in multiworld sessions  

[Discord Link](https://discord.gg/7dEp4cMnWF) for any questions or news about the bot.

## Use the Hosted Bot

If you don't want to host the bot yourself, or are unable to run it on your own infrastructure, you can use the publicly hosted ArchiLink bot.

Simply invite it to your Discord server using the link below :

**[Invite ArchiLink](https://discord.com/oauth2/authorize?client_id=1487801706732322997&permissions=8&integration_type=0&scope=bot+applications.commands)**

Once the bot has been added to your server, you can create and configure an Archipelago multiworld by using the following command :

```text
!newWorld
```
If you do not have inserted the [yaml](https://github.com/TanguyBod/ArchiLink/blob/main/archilink.yaml) during your archipelago world creation, you'll have to rename the bot name to a player name in the config.json
You can now edit a copy of the [config.json](https://github.com/TanguyBod/ArchiLink/blob/main/config.template.json) file and drop it in the channel or be guided by the setup wizard.
All fields of the json are described [here](https://github.com/TanguyBod/ArchiLink/blob/main/docs/json.md).
Beware, setup wizard hasn't been updated recently, some errors might happen.
If you have any question, contact me.

## Docker

If you plan to use this bot inside docker follow instructions [here](https://github.com/TanguyBod/ArchiLink/blob/main/docs/docker.md), otherwise go to the next section.

## Setup

All setup steps are described [here](https://github.com/TanguyBod/ArchiLink/blob/main/docs/setup.md).

# Commands

## World management commands

These commands are used to create and manage Archipelago multiworld instances.

| Command | Description |
|--------|------------|
| `!newWorld` | Initialize the bot to follow an Archipelago multiworld. Two configuration methods are available: manual configuration or uploading a `config.json` file. This command can be used in any channel. |
| `!fastConfig <ip> <port> <password (optional)>` | Quickly create a new multiworld using a default configuration. |
| `!deleteWorld` | Delete the world associated with the current channel. The bot will stop tracking this multiworld. This command can only be used by administrators when admins are configured, to prevent accidental deletion. |
| `!activate` | Restart tracking of the current world after a connection issue (for example after Archipelago inactivity). |
---

- Once a world is created, players can interact with it using the following commands.



## Player management commands

These commands allow Discord users to link their account to one or more Archipelago players.

| Command | Description |
|--------|------------|
| `!register <player_name>` | Link your Discord account to a player. You will receive notifications about this player's items and gain access to player-specific commands such as `!todo`, `!wishlist`, and `!new`. You can register to multiple players. |
| `!unregister [player_name]` | Unlink your Discord account from a player. If no player is specified, unregister from all linked players. |
| `!players` | Display the list of all players in the current multiworld. |
| `!current` | Display the player slot currently being tracked. This slot is used by commands such as `!todo`, `!hint`, and `!wishlist`. |
| `!switch [player_name]` | Change the currently tracked player. Without an argument, switches to the next registered player. With a player name, switches directly to that player. |

---

## Hint and item tracking commands

These commands help track item locations and progression.

| Command | Description |
|--------|------------|
| `!hint <text>` | Send a hint request to the tracker. Recognized hints may provide additional interactions, such as adding items to your todo list. |
| `!allhints` | Display all hints available for the currently tracked player. |
| `!wish <item_name>` | Add an available item to your wishlist. The item must have been hinted previously. You can see all hinted items with previous command.|
| `!todo` | Display the current todo list of the tracked player. |
| `!clearTodo` | Clear the entire todo list of the tracked player. |
| `!removeTodo <item_name>` | Remove a specific item from the todo list. |
| `!wishlist` | Display items that other players have added to their todo lists for the tracked player. |

---

## Item notification commands

These commands control how the bot informs you about newly received items.

| Command | Description |
|--------|------------|
| `!new` | Check newly received items since your last check. Results are sent through DM. |
| `!enablenewitems` | Enable automatic DM notifications for new items when connecting to the game. |
| `!disablenewitems` | Disable automatic DM notifications for new items. Use `!new` manually instead. |
| `!enableping` | Enable notifications when another player finds an item currently present in your todo list. |
| `!disableping` | Disable todo item notifications. |

---

## Statistics commands

These commands provide information about the progress of the multiworld.

| Command | Description |
|--------|------------|
| `!wastedOnArchipelago` | Display your total playtime in the multiworld session. |
| `!deaths` | Display your total death count. |
| `!deathgraph` | Generate a graph showing your deaths over time. |
| `!globaldeaths` | Generate a comparative graph showing deaths for all players. |
| `!progressGraph` | Generate a progress graph showing the percentage of checked locations for each player. The number of checks found is displayed above each bar. |

---

## Communication commands

| Command | Description |
|--------|------------|
| `!say <message>` | Send a message to the Archipelago MultiWorld client as the currently tracked player. |

---

## Personalization commands

| Command | Description |
|--------|------------|
| `!setcolor <color>` | Set your preferred display color for your player name. |

---

## Administration commands

These commands are available to everyone if no administrator system is configured. Otherwise, some commands require administrator permissions.

| Command | Description |
|--------|------------|
| `!isAdmin` | Check whether you are an administrator of the current world. |
| `!computeChecks` | Compute the total number of checks for every player. This must be run before generating the progress graph for the first time. The bot connects to the multiworld for every player to retrieve this information, which may temporarily cause lag. |
| `!deactivate` | Stop the bot from tracking the world associated with the current channel. |
| `!listWorlds` | Display the number of worlds currently tracked by this server and their associated channels. |
| `!deleteWorld` | Delete the world associated with the current channel. |
| `!config <field_to_change> <new_value>` | Change one field of the config file, this prevent you from deleting world if a mistake was made in the config. All fields can be changed, bot will restart on his own. |

---

## Help command

| Command | Description |
|--------|------------|
| `!help [command]` | Display the list of available commands or detailed information about a specific command. |
