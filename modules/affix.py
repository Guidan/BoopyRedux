import requests


async def main(message,content):
    res = requests.get('https://raider.io/api/v1/mythic-plus/affixes?region=us&locale=en')
    affixes = res.json()['title']
    await message.channel.send('The mythic plus affixes for this week are: {}'.format(affixes))

async def help(message):
    await message.channel.send('Use !affix to find out what the mythic plus affixes are for the week!')