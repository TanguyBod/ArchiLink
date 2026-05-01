# ArchiLink

A Discord bot designed to interact with an **Archipelago Multiworld** session directly from your server.

While existing tools (such as [Bridgeipelago](https://github.com/Quasky/bridgeipelago/tree/main)) already provide item tracking and hint management, **ArchiLink focuses on improving coordination between players by introducing cross-player todo lists**. This allows players to explicitly communicate needs and priorities, making multiworld collaboration significantly smoother and more structured.

Players can track progress, request hints, and — most importantly — **assign items or goals to other players via shared todo lists** directly from Discord.

Its main features are the following:

- 📦 View all collected items across players  
- 🧾 Create and manage todo lists for other players to communicate needs  
- 🔍 Request in-game hints directly from Discord  
- 📝 Add hints or items to another player's todo list  
- 🔔 Get notified when your required item is found  
- 🤝 Improve coordination and teamwork in multiworld sessions  

## Setup

All setup steps are described [here](https://github.com/TanguyBod/ArchiLink/blob/main/docs/setup.md).

## Commands

Here is the list of available commands:

| Command | Description |
|--------|------------|
| `!register <player_name>` | Link your Discord account to a player. You will receive notifications about this player's items and gain access to player-specific commands such as `!todo`, `!wishlist`, and `!new`. |
| `!unregister [player_name]` | Unlink your account from a player. If no player is specified, unregisters from your current player. |
| `!players` | Display the list of all players in the multiworld. |
| `!hint <text>` | Send a hint request to the tracker. Recognized hints may allow interaction (e.g., adding items to todo lists). |
| `!new` | Check newly received items since your last check (sent via DM). |
| `!todo` | Display your current todo list. |
| `!clearTodo` | Clear your entire todo list. |
| `!removeTodo <item_name>` | Remove a specific item from your todo list. |
| `!progressGraph` | Generate a progression graph for all players (completion %, locations checked, etc.). |
| `!wishlist` | Display items other players have marked for you. |
| `!wastedOnArchipelago` | Display your total playtime in the multiworld session. |
| `!deaths` | Display your total death count. |
| `!deathgraph` | Generate a graph of your deaths over time. |
| `!globaldeaths` | Display a comparative graph of deaths across all players. |
| `!enableping` | Enable notifications when an item in your todo list is found by another player. |
| `!disableping` | Disable ping notifications. |
| `!enablenewitems` | Enable automatic DM notifications for new items when connecting to the game. |
| `!disablenewitems` | Disable automatic DM notifications for new items (use `!new` manually instead). |
| `!help [command]` | Show all commands or detailed info for a specific command. |

