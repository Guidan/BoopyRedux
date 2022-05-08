import json
import logging
import config


async def main(message, content):
    if message.content.startswith(config.activator):
        await message.channel.send("Meme doesn't work like that. For more info, do !meme help")
        return
    with open('./asset/meme.json') as memes:
        meme_data = json.load(memes)
        content = [each_string.lower() for each_string in content]
    content = " ".join(content)
    for meme in meme_data:
        if meme in content:
            logging.info('meme word found: {}'.format(meme))
            await message.channel.send(meme_data[meme])
            return


async def help(message):
    with open('./asset/meme.json') as memes:
        meme_data = json.load(memes)
    meme_list = list(meme_data.keys())
    await message.channel.send('The meme module looks for specific meme words in chat. List of words: {}'.format(meme_list))