import discord


async def sticker(client, message, config, previous_message, counter):
    if message.author == client.user:
        return

    channel_id = str(message.channel.id)
    allowed = config["allowed_channels"]
    if allowed and channel_id not in allowed:
        return

    threshold = config["thresholds"].get(channel_id)
    if not threshold:
        return

    lock = client.channel_locks[channel_id]
    async with lock:
        counter[channel_id] += 1
        if counter[channel_id] < threshold:
            return

        bot_message = config["bot_message"].get(channel_id, "default message")
        prev_msg = previous_message.get(channel_id)
        if prev_msg:
            try:
                await prev_msg.delete()
            except discord.errors.NotFound:
                pass

        previous_message[channel_id] = await message.channel.send(bot_message)
        counter[channel_id] = 0
