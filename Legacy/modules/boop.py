import logging


async def main(message, content):
    if len(content) > 1:
        boopee = " ".join(content[1:])
        logging.info('Booping {}'.format(boopee))
        if boopee == "<@!360513740145164289>" or boopee.lower() == "boopy":
            await message.channel.send('YOU CAN NOT BOOP THE BOOPER')
        else:
            await message.channel.send('GET BOOPED {}'.format(boopee))
    else:
        await message.channel.send('Need to tell me who to boop! Use "!boop help" for more info')


async def help(message):
    await message.channel.send("Type !Boop $NAME to boop whoever you want!")