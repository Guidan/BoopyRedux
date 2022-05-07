import config
import discord
import logging
import sqlite3
import json
import requests
from config import birthdayChannels
from dateutil.parser import parse
from datetime import date
from discord.ext import tasks, commands
from discord_slash import SlashCommand, SlashContext

logging.basicConfig(format='%(asctime)s:%(levelname)s: %(message)s', level=logging.INFO)
client = discord.Client()
slash = SlashCommand(client, sync_commands=True)

# loot globals
GOLD = 0
SILVER = 0
COPPER = 0
PLATINUM = 0


@client.event
async def on_ready():
    print('Ready to Boop!')
    check_birthday.start()


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    content = message.content.split()
    with open('./asset/meme.json') as memes:
        meme_data = json.load(memes)
        content = [each_string.lower() for each_string in content]
    content = " ".join(content)
    for meme in meme_data:
        if meme in content:
            logging.info('meme word found: {}'.format(meme))
            await message.channel.send(meme_data[meme])
            return


@slash.slash(
    name="Boop",
    description="Use this command to boop whoever you want!",
    guild_ids=config.server_list)
async def boop(ctx, boopee: str):
    text = boopee
    if text is not None:
        logging.info('Booping {}'.format(text))
        if text == "<@!360513740145164289>" or text.lower() == "boopy":
            await ctx.send('YOU CAN NOT BOOP THE BOOPER')
        else:
            await ctx.send('GET BOOPED {}'.format(text))
    else:
        await ctx.send('Need to tell me who to boop! Use "!boop help" for more info')


@slash.slash(
    name="watch2gether",
    description="Use to create a watch2gether link.",
    guild_ids=config.server_list)
async def w2g(ctx, link: str):
    data_input = {
        "w2g_api_key": config.w2g_api_key,
        "share": link,
        "bg_color": "#343434",
        "bg_opacity": "100"
    }
    headers_input = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    res = requests.post("https://w2g.tv/rooms/create.json", params=data_input, headers=headers_input)
    w2g_link = "https://w2g.tv/rooms/{}".format(res.json()["streamkey"])
    logging.info("sending link for {}".format(w2g_link))
    await ctx.send("Here is your link!\n{}".format(w2g_link))


@slash.slash(
    name="lootAdd",
    description="This function adds currency loot to a table (and converts electrum to silver).",
    guild_ids=config.server_list)
async def lootAdd(ctx, text: str):
    global GOLD, SILVER, COPPER, PLATINUM
    content = text.split()
    if len(content) == 0:
        await ctx.send("I need to know what currency to add!")
        return
    for loot in content:
        try:
            lootType = loot[-1]
            loot = int(loot.rstrip(lootType))
            if lootType == 'p':
                PLATINUM += loot
            elif lootType == 'g':
                GOLD += loot
            elif lootType == 'c':
                COPPER += loot
            elif lootType == 's':
                SILVER += loot
            elif lootType == 'e':
                SILVER += (loot*5)
            else:
                await ctx.send("I don't know wtf this is => {}{}".format(loot, lootType))

        except ValueError:
            await ctx.send("Something is wrong with the numbers you gave me. \nCheck to make sure you follow the"
                                 " syntax: `#c #g #p`. The order doesn't matter but the letter must always follow the number")
            return
    await ctx.send("loot added!")
    logging.info("Platinum:{} Gold:{} Silver:{} Copper:{}".format
                 (PLATINUM, GOLD, SILVER, COPPER))


@slash.slash(
    name="lootSplit",
    description="This command splits the loot for the amount of players specified.",
    guild_ids=config.server_list)
async def lootSplit(ctx, players: int):
    global GOLD, SILVER, COPPER, PLATINUM
    content = players
    if content < 1:
        await ctx.send("The number of players must be at least 1!")
        return
    else:
        denom = {
            "Platinum": 1000,
            "Gold": 100,
            "Silver": 10,
            "Copper": 1
        }
        output = {}
        copperAdd = PLATINUM*1000 + GOLD*100 + SILVER*10 + COPPER  # convert all to copper for easy math
        leftover = copperAdd % players  # get the remainder to output later
        copperAdd -= leftover  # remove the remainder from the loot pile for easy math
        copperShare = int(copperAdd/players)
        for key, value in denom.items():
            output[key] = copperShare // value
            copperShare %= value
        resetLoot()  # reset the loot pile to 0
        response = ("Here is the loot split {} ways:\nPlatinum:{}\nGold:{}\nSilver:{}"
                    "\nCopper:{}".format(players, output["Platinum"], output["Gold"], output["Silver"], output["Copper"]))
        if leftover > 0:
            response = response + ("\nWith {} copper leftover (figure it out amongst yourselves)".format(leftover))
        await ctx.send(response)


@slash.slash(
    name="lootlist",
    description="This command lists the current loot pile numbers",
    guild_ids=config.server_list)
async def lootlist(ctx):
    global GOLD, SILVER, COPPER, PLATINUM
    await ctx.send("Platinum:{}\nGold:{}\nSilver:{}\nCopper:{}".format
                               (PLATINUM, GOLD, SILVER, COPPER))


@tasks.loop(hours=24)
async def check_birthday():
    logging.info("Checking birthdays...")
    try:
        bday = sqlite3.connect('./asset/birthdays.db')
        cur = bday.cursor()
    except:
        logging.critical('CONNECTION ERROR WITH BIRTHDAY DATABASE')
        return
    today = date.today()
    day = today.strftime("%d")
    month = today.strftime("%m")
    sqlstmt = "SELECT ID FROM BIRTHDAY WHERE DAY = {} AND " \
              "MONTH = {}".format(day, month)
    logging.info("Executing sql statement: {}".format(sqlstmt))
    cur.execute(sqlstmt)
    response = cur.fetchall()
    if not response:
        logging.info("It's nobodies bday today")
        return
    else:
        for person in response:
            bdayboi = person[0]
            logging.info("It's {}'s birthday today. Sending message...".format(bdayboi))
            for channel in birthdayChannels:
                generalchannel = client.get_channel(channel)
                await generalchannel.send("@here 🎉🎉🎉🎉 Today is <@!{}>'s birthday!"
                                          " Be sure to wish them a happy birthday! 🎉🎉🎉🎉".format(bdayboi))
    bday.close()


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def resetLoot():
    global GOLD, SILVER, COPPER, PLATINUM
    GOLD = 0
    SILVER = 0
    COPPER = 0
    PLATINUM = 0

client.run(config.token)
# config.py should have TOKEN = whatever token is for bot
