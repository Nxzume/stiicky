import json
import os
import asyncio
from collections import defaultdict

import discord
from util.sticky import sticker
from util import commands as command_module


DEFAULT_CONFIG = {
    "token": "YOUR_BOT_TOKEN",
    "bot_message": {
        "channel_id_1": "message 1\nThis will be in a new line"
    },
    "allowed_channels": ["channel_id_1"],
    "thresholds": {},
    "prefix": "!"
}


def load_config(path="config.json"):
    if os.path.isfile(path):
        with open(path, "r") as config_file:
            config = json.load(config_file)
        changed = False
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
                changed = True
        if changed:
            with open(path, "w") as config_file:
                json.dump(config, config_file, indent=4)
        return config

    with open(path, "w") as config_file:
        json.dump(DEFAULT_CONFIG, config_file, indent=4)
    return DEFAULT_CONFIG.copy()


config = load_config()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = discord.Client(intents=intents)
client.counter = defaultdict(int)
client.previous_message = {}
client.channel_locks = defaultdict(asyncio.Lock)

commands = {
    name[8:]: function
    for name, function in vars(command_module).items()
    if name.startswith("command_")
}


@client.event
async def on_message(message):
    if message.content.startswith(config["prefix"]):
        parts = message.content[len(config["prefix"]):].split()
        if not parts:
            return
        command = parts[0]
        if command not in commands:
            return

        if not message.author.guild_permissions.manage_channels:
            await message.channel.send("You do not have the permission to run this command.")
            await message.delete()
            return

        if command == "help":
            await commands[command](client, message, config, commands)
        elif command == "restart":
            await commands[command](client, message)
        else:
            await commands[command](client, message, config)
        await message.delete()
        return

    await sticker(
        client,
        message,
        config,
        client.previous_message,
        client.counter,
    )


@client.event
async def on_ready():
    print("Bot is ready!")


client.run(config["token"])
