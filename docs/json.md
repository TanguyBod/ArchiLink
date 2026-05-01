# JSON Configuration Reference

This document describes every field available in `config.json`.

A template is available [here](https://github.com/TanguyBod/ArchiLink/blob/main/config.template.json).

---

# `ArchipelagoConfig`

Configuration related to the Archipelago server connection.

## `client_url`

```json
"client_url": ""
```

The hostname or IP address of your Archipelago server.

### Examples

```json
"client_url": "archipelago.gg"
```

```json
"client_url": "127.0.0.1"
```

---

## `client_port`

```json
"client_port": ""
```

The port used by the Archipelago server.

### Example

```json
"client_port": "38281"
```

---

## `password`

```json
"password": null
```

Optional password required to connect to the Archipelago room.

If the room does not require a password, leave this value as `null`.

### Examples

No password:

```json
"password": null
```

With password:

```json
"password": "mySecretPassword"
```

---

## `bot_slot`

```json
"bot_slot": "ArchiLink"
```

The slot name the bot will use when connecting to the Archipelago room.

This slot must exist in your generated Archipelago multiworld.

### Example

```json
"bot_slot": "DiscordBot"
```

---

# `DiscordConfig`

Configuration related to the Discord bot.

---

## `app_token`

```json
"app_token": ""
```

Your Discord bot token from the Discord Developer Portal.


### Example

```json
"app_token": "YOUR_DISCORD_BOT_TOKEN"
```

---

## `normal_channel_id`

```json
"normal_channel_id": ""
```

The Discord channel ID where standard bot messages will be sent. To get the ID of a channel you'll need to go to your discord settings, under `Developer tab`, enable `Developer Mode`. Then you can right click a channel and copy its ID.

### Example

```json
"normal_channel_id": "123456789012345678"
```

---

## `ping_channel_id`

```json
"ping_channel_id": ""
```

The Discord channel ID used for item pings or important notifications.

### Example

```json
"ping_channel_id": "123456789012345678"
```

---

## `command_prefix`

```json
"command_prefix": "!"
```

Prefix used for bot commands in Discord.

### Example

If the prefix is:

```json
"command_prefix": "!"
```

Commands will look like:

```text
!help
!status
```

---

## `admin_ids`

```json
"admin_ids": []
```

List of Discord user IDs allowed to access admin-only commands.

### Example

```json
"admin_ids": [
    "123456789012345678",
    "987654321098765432"
]
```

> 💡 To get a Discord user ID, enable **Developer Mode** in Discord and right-click a user.

---

# `DatabaseConfig`

Configuration related to local data storage.

---

## `data_directory`

```json
"data_directory": "./data"
```

Directory where the bot stores its local data and database files.

Relative and absolute paths are supported.

### Examples

Relative path:

```json
"data_directory": "./data"
```

Absolute path:

```json
"data_directory": "/home/user/archilink/data"
```

---

# `AdvancedConfig`

Additional optional features and advanced behaviors.

---

## `custom_deathlink_flavor`

```json
"custom_deathlink_flavor": false
```

Enable custom DeathLink message formatting.

When enabled, the bot may send customized DeathLink messages instead of default ones.

### Values

| Value | Description |
|---|---|
| `true` | Enable custom DeathLink messages |
| `false` | Use default behavior |

---

## `auto_ping_new_items`

```json
"auto_ping_new_items": true
```

This field allow the bot to send message new items to a player when he join the game. If set to false, players will have to manually activate it. It can be enabled/disabled per player with commands.

### Values

| Value | Description |
|---|---|
| `true` | Automatically ping users |
| `false` | Disable automatic pings |

---

# Full Example

```json
{
    "ArchipelagoConfig": {
        "client_url" : "archipelago.gg",
        "client_port" : "38281",
        "password" : null,
        "bot_slot" : "Archipelabot"
    },
    "DiscordConfig": {
        "app_token" : "YOUR_BOT_TOKEN",
        "normal_channel_id" : "123456789012345678",
        "ping_channel_id" : "123456789012345678",
        "command_prefix" : "!",
        "admin_ids" : [
            "123456789012345678"
        ]
    },
    "DatabaseConfig": {
        "data_directory" : "./data"
    },
    "AdvancedConfig": {
        "custom_deathlink_flavor" : false,
        "auto_ping_new_items" : true
    }
}
```