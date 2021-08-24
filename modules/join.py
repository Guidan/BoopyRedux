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
        logging.info("checking guild roles...")
        role = get(message.guild.roles, id=int(role_id))
        if role in user_roles:
            logging.warning("user already in role. Scolding...")
            await message.channel.send("You are already in that role. To leave, type !leave {}".format(content[1]))
        else:
            await message.author.add_roles(role, reason="automated")
            logging.info("added {} role to {}".format(role, message.author))
            await message.channel.send("added {} role to {}!".format(role, message.author))


async def help(message):
    channel_list = list(channel_roles.keys())
    await message.channel.send("To join a channel of interest. Use !join followed by any of the following "
                               "channels: \n{}".format(channel_list))
