import discord, config, logging, os
from modules import meme, boop


l = os.listdir('modules')
modules = [x.split('.')[0] for x in l if x.endswith('.py')]
logging.basicConfig(format='%(asctime)s:%(levelname)s:"%(message)s', level=logging.INFO)
client = discord.Client()


@client.event
async def on_ready():
    print('Ready to Boop!')
    logging.info('Modules loaded: {}'.format(modules))


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    content = message.content.split()
    if message.content.startswith(config.activator):
        command = content[0].lstrip(config.activator).lower()
        if command == "help":
            await message.channel.send("I am Boopy. To perform a command, type ! followed by one of these commands:\n{}\n to get help on a command, type !command help".format(modules))
        elif command in modules:
            invoke = ('{}.main(message,content)'.format(command))
            if len(content) > 1:
                if content[1] == "help":
                    invoke = ('{}.help(message)'.format(command))
            await eval(invoke)
        else:
            await message.channel.send("That command doesn't exist")
    else:
        await meme.main(message, content)


client.run(config.token)
# config.py should have TOKEN = whatever token is for bot
