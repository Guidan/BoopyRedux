import logging, discord
from discord.utils import get
from config import member_role, welcome_channel


async def main(message, content):
    user_roles = message.author.roles
    role = get(message.guild.roles, id=member_role)
    welcome = get(message.guild.channels, id=welcome_channel)
    logging.info("Channel id = {}".format(message.channel.id))
    if message.channel.id != welcome_channel:
        await message.channel.send("That command only works in the <#{}> channel.".format(welcome_channel))
        return
    if role in user_roles:
        logging.warning("user already a member. Deleting message...")
    else:
        await message.author.add_roles(role, reason="accepted rules")
        logging.info("added {} role to {}".format(role, message.author))
    await message.delete()


async def help(message):
    await message.channel.send("This command is only used to give "
                               "the member role in the <#{}> channel".format(welcome_channel))