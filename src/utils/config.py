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
            "self_hosted",
            "room_url"
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
            "new_items_on_join_game",
            "player_colors_limited",
            "item_messages_in_thread",
            "deathlink_messages_in_thread",
            "send_join_leave_messages",
            "item_display_level",
            "display_traps",
            "ping_all_items"
        ]    
        for field in advanced_config_fields:
            if field not in data["AdvancedConfig"]:
                return data, False
            
        # Trim data to only the required fields to avoid storing unnecessary data
        trimmed_data = {}
        trimmed_data["ArchipelagoConfig"] = {field: data["ArchipelagoConfig"][field] for field in archipelago_config_fields}
        trimmed_data["DiscordConfig"] = {field: data["DiscordConfig"][field] for field in discord_config_fields}
        trimmed_data["AdvancedConfig"] = {field: data["AdvancedConfig"][field] for field in advanced_config_fields}
        
        # Replace https://archipelago.gg with archipelago.gg in the client_url field if present
        if "client_url" in trimmed_data["ArchipelagoConfig"]:
            trimmed_data["ArchipelagoConfig"]["client_url"] = trimmed_data["ArchipelagoConfig"]["client_url"].replace("https://archipelago.gg", "archipelago.gg")
        
        return trimmed_data, True
    
    except Exception as e:
        print(f"Error while checking config: {e}")
        return data, False

def complete_config(data) :
    # Set default values for optional fields if they are missing
    if "custom_deathlink_flavor" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["custom_deathlink_flavor"] = False
    if "new_items_on_join_game" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["new_items_on_join_game"] = True
    if "player_colors_limited" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["player_colors_limited"] = False
    if "item_messages_in_thread" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["item_messages_in_thread"] = False
    if "deathlink_messages_in_thread" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["deathlink_messages_in_thread"] = False
    if "send_join_leave_messages" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["send_join_leave_messages"] = True
    if "item_display_level" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["item_display_level"] = 1
    if "display_traps" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["display_traps"] = True
    if "self_hosted" not in data["ArchipelagoConfig"]:
        data["ArchipelagoConfig"]["self_hosted"] = False
    if "admin_ids" not in data["DiscordConfig"]:
        data["DiscordConfig"]["admin_ids"] = []
    if "ping_channel_id" not in data["DiscordConfig"] or data["DiscordConfig"]["ping_channel_id"] == "":
        data["DiscordConfig"]["ping_channel_id"] = None
    if "bot_slot" not in data["ArchipelagoConfig"]:
        data["ArchipelagoConfig"]["bot_slot"] = "ArchiLink"
    if "ping_all_items" not in data["AdvancedConfig"]:
        data["AdvancedConfig"]["ping_all_items"] = False
    return data