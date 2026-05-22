import asyncio

import discord
import json
        
STEPS = [
    "ArchipelagoConfig",
    "DiscordConfig",
    "DatabaseConfig",
    "AdvancedConfig"
]
        
class EntryView(discord.ui.View):
    
    # Two buttons, one for manual configuration and one for importing from file

    # Manual configuration button opens the ConfigWizardView
    @discord.ui.button(label="Manual Configuration", style=discord.ButtonStyle.primary)
    async def manual(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ConfigWizardView()
        step_name = STEPS[0]
        embed = discord.Embed(
            title="⚙️ Configuration Wizard",
            description=f"Starting at {step_name}"
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    # Import from file button (Ask user to upload a JSON file, then parse it and create multiworld instance)
    @discord.ui.button(label="Import from File", style=discord.ButtonStyle.secondary)
    async def import_file(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "Please upload a JSON configuration file within 5 minutes.",
            ephemeral=True
        )

        def check(message: discord.Message):
            return (
                message.author.id == interaction.user.id
                and message.channel.id == interaction.channel.id
                and len(message.attachments) > 0
            )

        try:
            # Attend uniquement le PREMIER message valide
            message = await interaction.client.wait_for(
                "message",
                check=check,
                timeout=300
            )

            attachment = message.attachments[0]

            # Vérifie extension
            if not attachment.filename.endswith(".json"):
                await interaction.followup.send(
                    "The uploaded file must be a JSON file.",
                    ephemeral=True
                )
                return

            # Lecture du contenu
            file_bytes = await attachment.read()

            try:
                data = json.loads(file_bytes.decode("utf-8"))
            except json.JSONDecodeError:
                await interaction.followup.send(
                    "Invalid JSON file.",
                    ephemeral=True
                )
                return

            # Ici tu peux créer ton instance multiworld
            print(data)

            await interaction.followup.send(
                "Configuration imported successfully.",
                ephemeral=True
            )

        except asyncio.TimeoutError:
            await interaction.followup.send(
                "Timeout: no file received within 5 minutes.",
                ephemeral=True
            )
            
class ConfigWizardState:
    def __init__(self):
        self.data = {
            "ArchipelagoConfig": {},
            "DiscordConfig": {},
            "DatabaseConfig": {},
            "AdvancedConfig": {}
        }

        self.step = 0

class ConfigWizardView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=600)
        self.state = ConfigWizardState()

    # Dynamic message update based on current step
    async def update_message(self, interaction: discord.Interaction):

        step_name = STEPS[self.state.step]

        embed = discord.Embed(
            title=f"⚙️ Configuration - {step_name}",
            description=f"Step {self.state.step + 1}/{len(STEPS)}",
            color=0x00ffcc
        )

        embed.add_field(
            name="Current data",
            value=f"```json\n{self.state.data[step_name]}\n```",
            inline=False
        )

        await interaction.response.edit_message(embed=embed, view=self)

    # Back button
    @discord.ui.button(label="◀", style=discord.ButtonStyle.secondary)
    async def back(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.state.step > 0:
            self.state.step -= 1

        await self.update_message(interaction)

    # Next button
    @discord.ui.button(label="▶", style=discord.ButtonStyle.primary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):

        if self.state.step < len(STEPS) - 1:
            self.state.step += 1

        await self.update_message(interaction)

    # Edit button opens modal for current step
    @discord.ui.button(label="Edit", style=discord.ButtonStyle.green)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):

        step = STEPS[self.state.step]

        modals = {
            "ArchipelagoConfig": ArchipelagoModal,
            "DiscordConfig": DiscordConfigModal,
            "DatabaseConfig": DatabaseModal,
            "AdvancedConfig": AdvancedModal
        }

        await interaction.response.send_modal(modals[step](self.state))

    # Export button save current config and create multiworld instance
    @discord.ui.button(label="Save config", style=discord.ButtonStyle.success)
    async def export(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            f"```json\n{json.dumps(self.state.data, indent=4)}\n```",
            ephemeral=True
        )

class ArchipelagoModal(discord.ui.Modal, title="Archipelago Config"):

    def __init__(self, state):
        super().__init__()
        self.state = state

    client_url = discord.ui.TextInput(label="Client URL", required=True)
    client_port = discord.ui.TextInput(label="Client Port", required=True)
    password = discord.ui.TextInput(label="Password", required=False)
    bot_slot = discord.ui.TextInput(label="Bot Slot", default="ArchiLink", required=False)

    async def on_submit(self, interaction: discord.Interaction):

        self.state.data["ArchipelagoConfig"] = {
            "client_url": self.client_url.value,
            "client_port": self.client_port.value,
            "password": self.password.value or None,
            "bot_slot": self.bot_slot.value or "ArchiLink",
            "self_hosted": False
        }

        
class DiscordConfigModal(discord.ui.Modal, title="Discord Config"):

    def __init__(self, state):
        super().__init__()
        self.state = state

    app_token = discord.ui.TextInput(label="App Token", required=True)
    normal_channel_id = discord.ui.TextInput(label="Normal Channel ID", required=True)
    ping_channel_id = discord.ui.TextInput(label="Ping Channel ID", required=False)
    debug_channel_id = discord.ui.TextInput(label="Debug Channel ID", required=False)
    command_prefix = discord.ui.TextInput(label="Command Prefix", default="!", required=False)

    async def on_submit(self, interaction: discord.Interaction):

        self.state.data["DiscordConfig"] = {
            "app_token": self.app_token.value,
            "normal_channel_id": self.normal_channel_id.value,
            "ping_channel_id": self.ping_channel_id.value or None,
            "debug_channel_id": self.debug_channel_id.value or None,
            "command_prefix": self.command_prefix.value or "!",
            "admin_ids": []
        }

        
class DatabaseModal(discord.ui.Modal, title="Database Config"):

    def __init__(self, state):
        super().__init__()
        self.state = state

    data_directory = discord.ui.TextInput(label="Data Directory", default="./data")

    async def on_submit(self, interaction: discord.Interaction):

        self.state.data["DatabaseConfig"] = {
            "data_directory": self.data_directory.value
        }

        
class AdvancedModal(discord.ui.Modal, title="Advanced Config"):

    def __init__(self, state):
        super().__init__()
        self.state = state

    custom_deathlink_flavor = discord.ui.TextInput(
        label="Custom Deathlink Flavor (true/false)",
        required=False
    )

    auto_ping_new_items = discord.ui.TextInput(
        label="Auto Ping New Items (true/false)",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):

        self.state.data["AdvancedConfig"] = {
            "custom_deathlink_flavor": self.custom_deathlink_flavor.value.lower() == "true",
            "auto_ping_new_items": self.auto_ping_new_items.value.lower() != "false"
        }
