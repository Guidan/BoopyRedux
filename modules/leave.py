from config import channel_roles
from discord.utils import get
import logging


async def main(message, content):
    if len(content) == 1:
        await message.channel.send("That's not how the join function works. For more info, do !join help")
        return
    user_roles = message.author.roles
    if channel_roles.get(content[1]) is None:
        await message.channel.send("{} is not a valid server group. To see a list, do !join help".format(content[1]))
        return
    else:
        role_id = channel_roles.get(content[1])
        role = get(message.guild.roles, id=int(role_id))
        if role in user_roles:
            await message.author.remove_roles(role, reason="automated")
            logging.info("removed {} role from {}".format(role, message.author))
            await message.channel.send("removed {} role from {}!".format(role, message.author))
        else:
            logging.warning("user not in group. Scolding...")
            await message.channel.send("You aren't in that group. To join, type !join {}".format(content[1]))


async def help(message):
    channel_list = list(channel_roles.keys())
    await message.channel.send("To leave a channel group. Use !leave followed by any of the following "
                               "channels: \n{}\nYou have to be in the group to leave. Obviously.".format(channel_list))
