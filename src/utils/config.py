def check_config(data) :
    try :
        data = complete_config(data)
        
        # Check if all required fields are present
        required_fields = [
            "ArchipelagoConfig",
            "DiscordConfig",
            "AdvancedConfig"
        ]
        for field in required_fields:
            if field not in data:
                return data, False
            
        # Check if all required subfields are present
        archipelago_config_fields = [
            "client_url",
            "client_port",
            "password",
            "bot_slot",
            "self_hosted"
        ]
        for field in archipelago_config_fields:
            if field not in data["ArchipelagoConfig"]:
                return data, False
            
        discord_config_fields = [
            "normal_channel_id",
            "ping_channel_id",
            "admin_ids"
        ]
        for field in discord_config_fields:
            if field not in data["DiscordConfig"]:
                return data, False
            
        advanced_config_fields = [
            "custom_deathlink_flavor",
            "auto_ping_new_items",
            "player_colors_limited",
            "item_messages_in_thread",
            "deathlink_messages_in_thread"
        ]    
        for field in advanced_config_fields:
            if field not in data["AdvancedConfig"]:
                return data, False
            
        # Trim data to only the required fields to avoid storing unnecessary data
        trimmed_data = {}
        trimmed_data["ArchipelagoConfig"] = {field: data["ArchipelagoConfig"][field] for field in archipelago_config_fields}
        trimmed_data["DiscordConfig"] = {field: data["DiscordConfig"][field] for field in discord_config_fields}
        trimmed_data["AdvancedConfig"] = {field: data["AdvancedConfig"][field] for field in advanced_config_fields}
        
        return trimmed_data, True
    
    except Exception as e:
        print(f"Error while checking config: {e}")
        return data, False

def complete_config(data) :
    # Set default values for optional fields if they are missing
    if "custom_deathlink_flavor" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["custom_deathlink_flavor"] = False
    if "auto_ping_new_items" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["auto_ping_new_items"] = True
    if "player_colors_limited" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["player_colors_limited"] = False
    if "item_messages_in_thread" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["item_messages_in_thread"] = False
    if "deathlink_messages_in_thread" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["deathlink_messages_in_thread"] = False
    if "self_hosted" not in data["ArchipelagoConfig"]:
        data["ArchipelagoConfig"]["self_hosted"] = False
    if "admin_ids" not in data["DiscordConfig"]:
        data["DiscordConfig"]["admin_ids"] = []
    if "ping_channel_id" not in data["DiscordConfig"]:
        data["DiscordConfig"]["ping_channel_id"] = None
    if "bot_slot" not in data["ArchipelagoConfig"]:
        data["ArchipelagoConfig"]["bot_slot"] = "ArchiLink"
    
    return data