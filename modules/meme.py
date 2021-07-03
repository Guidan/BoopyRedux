import json
import logging


async def main(message, content):
    if message.content.startswith('!'):
        await message.channel.send("Meme doesn't work like that. For more info, do !meme help")
        return
    with open('.\\asset\meme.json') as memes:
        meme_data = json.load(memes)

    for meme in meme_data:
        if meme in content:
            logging.info('meme word found: {}'.format(meme))
            await message.channel.send(meme_data[meme])


async def help(message):
    with open('.\\asset\meme.json') as memes:
        meme_data = json.load(memes)
    meme_list = list(meme_data.keys())
    await message.channel.send('The meme module looks for specific meme words in chat. List of words: {}'.format(meme_list))