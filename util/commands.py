import os
import sys
import json

import discord
from discord.utils import get


def save_config(config, path="config.json"):
    with open(path, "w") as config_file:
        json.dump(config, config_file, indent=4)


async def command_setprefix(client, message, config):
    """sets the prefix for the bot"""
    parts = message.content.split()
    if len(parts) < 2 or not parts[1]:
        await message.channel.send("Please provide a prefix")
        return

    config["prefix"] = parts[1]
    save_config(config)
    await message.channel.send(f"Command prefix set to {parts[1]}")


async def command_setmessage(client, message, config):
    channel_id = str(message.channel.id)
    message_content = message.content[len(config["prefix"] + "setmessage "):]
    config["bot_message"][channel_id] = message_content
    if channel_id not in config["allowed_channels"]:
        config["allowed_channels"].append(channel_id)
    config["thresholds"].setdefault(channel_id, 1)
    save_config(config)
    await message.channel.send("Successfully set message for this channel.")


async def command_rchannel(client, message, config):
    channel = message.channel
    channel_id = str(channel.id)
    if channel_id not in config["allowed_channels"]:
        await message.channel.send(f"Channel {channel.name} is not in allowed channels.")
        return

    config["allowed_channels"].remove(channel_id)
    config["thresholds"].pop(channel_id, None)
    config["bot_message"].pop(channel_id, None)
    client.counter.pop(channel_id, None)
    client.previous_message.pop(channel_id, None)
    save_config(config)
    await message.channel.send(f"Removed channel {channel.name} from allowed channels.")


async def command_limit(client, message, config):
    try:
        new_threshold = int(message.content.split()[1])
    except (ValueError, IndexError):
        await message.channel.send("Please provide a valid threshold")
        return

    channel_id = str(message.channel.id)
    config["thresholds"][channel_id] = new_threshold
    client.counter[channel_id] = 0
    save_config(config)
    await message.channel.send(f"Threshold for this channel set to {new_threshold}")


async def command_help(client, message, config, commands):
    regular_commands = {
        "help": "Shows the list of available commands and their descriptions.",
        "setprefix": "Sets the prefix for server commands.",
        "purge": "Mention a user or amount of messages to delete a maximum of 100 messages per use.",
        "clear": "1-100 - Deletes the specified number of message sent by the bot in the current channel.",
        "setmessage": "Sets the message sent with this command to the current channel and add starts the sticky feature.",
        "rchannel": "Removes the bot's message from the current channel.",
        "limit": "Sets how many messages before the sticky reposts in this channel.",
        "restart": "Restarts the bot."
    }
    embed = discord.Embed(title="Commands:", description="A List of available commands", color=0x00FFFF)
    for command, description in regular_commands.items():
        embed.add_field(
            name=f"{config['prefix']}{command}",
            value=description,
            inline=False,
        )
    await message.channel.send(embed=embed)


async def command_clear(client, message, config):
    try:
        amount = int(message.content.split()[1])
    except (ValueError, IndexError):
        return await message.channel.send("Invalid number")

    messages = [
        msg
        async for msg in message.channel.history(limit=amount)
        if msg.author == client.user
    ]
    if not messages:
        await message.channel.send("No messages to delete.")
        return

    await message.channel.delete_messages(messages)
    await message.channel.send("Deleted previous bot messages.")


async def command_purge(client, message, config):
    if len(message.mentions) == 0 and len(message.content.split()) == 1:
        return await message.channel.send("Please mention a user or amount of messages to delete.")

    try:
        amount = int(message.content.split()[-1])
    except (ValueError, IndexError):
        amount = 100

    if message.mentions:
        user = message.mentions[0]
    else:
        try:
            user = get(client.get_all_members(), id=int(message.content.split()[1]))
        except (ValueError, IndexError):
            user = None

    if user is None:
        return await message.channel.send("Please mention a user or specify a valid ID.")

    deleted = await message.channel.purge(limit=amount, check=lambda m: m.author == user)
    await message.channel.send(f"Deleted {len(deleted)} messages.")


async def command_restart(client, message):
    await message.channel.send("Restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)


__all__ = [
    "command_setprefix",
    "command_help",
    "command_clear",
    "command_restart",
    "command_setmessage",
    "command_rchannel",
    "command_limit",
    "command_purge",
]
