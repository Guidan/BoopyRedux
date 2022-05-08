import json
import logging
import sqlite3
from datetime import date

import discord
import requests
from dateutil.parser import parse
from discord.ext import tasks
from discord.utils import get
from discord_slash import SlashCommand

import config
from config import birthdayChannels

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
async def lootAdd(ctx, loot: str):
    global GOLD, SILVER, COPPER, PLATINUM
    content = loot.split()
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
                SILVER += (loot * 5)
            else:
                await ctx.send("I don't know wtf this is => {}{}".format(loot, lootType))

        except ValueError:
            await ctx.send("Something is wrong with the numbers you gave me. \nCheck to make sure you follow the"
                           " syntax: `#c #g #p`. The order doesn't matter but the letter must always follow the number")
            return
    await ctx.send("loot added!", hidden=True)
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
        copperAdd = PLATINUM * 1000 + GOLD * 100 + SILVER * 10 + COPPER  # convert all to copper for easy math
        leftover = copperAdd % players  # get the remainder to output later
        copperAdd -= leftover  # remove the remainder from the loot pile for easy math
        copperShare = int(copperAdd / players)
        for key, value in denom.items():
            output[key] = copperShare // value
            copperShare %= value
        resetLoot()  # reset the loot pile to 0
        response = ("Here is the loot split {} ways:\nPlatinum:{}\nGold:{}\nSilver:{}"
                    "\nCopper:{}".format(players, output["Platinum"], output["Gold"], output["Silver"],
                                         output["Copper"]))
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


@slash.slash(
    name="price",
    description="Get the price of any game from isthereanydeal.com",
    guild_ids=config.server_list)
async def price(ctx, game_name: str):
    plain_header = {
        "key": config.itad_api_key,
        "title": game_name
    }
    res = requests.get("https://api.isthereanydeal.com/v02/game/plain/", params=plain_header)

    if not res.json()['.meta']['match']:
        logging.warning("unable to find plain for {}".format(game_name))
        await ctx.send("I was unable to find that title on isthereanydeal.com")
        return
    game_plain = res.json()['data']['plain']
    logging.info("Game plain found: {}".format(game_plain))

    # Get current prices from API
    prices_params = {
        "key": config.itad_api_key,
        "plains": game_plain
    }
    res = requests.get("https://api.isthereanydeal.com/v01/game/prices/", params=prices_params)
    # Check if there are no prices listed to catch errors
    if not res.json()['data'][game_plain]['list']:
        logging.warning("No prices found, but plain exists. Returning...")
        url = res.json()['data'][game_plain]['urls']['game']
        await ctx.send("No prices listed for that game. See page here: {}".format(url))
        return
    price = res.json()['data'][game_plain]['list'][0]['price_new']
    logging.info(price)
    price_url = res.json()['data'][game_plain]['list'][0]['url']

    # Get historical low from API
    lowest_params = {
        "key": config.itad_api_key,
        "plains": game_plain
    }
    res = requests.get("https://api.isthereanydeal.com/v01/game/lowest/", params=lowest_params)
    lowest = res.json()['data'][game_plain]['price']
    url = res.json()["data"][game_plain]["urls"]["game"]

    await ctx.send("**Price info for {}**\n**Price**: ${}\n**URL**:{}\n\n**History Lowest**: $"
                   "{}\n\n_prices are from isthereanydeal.com_".format(game_name, price, price_url, lowest))


@slash.slash(
    name="birthdayadd",
    description="Add your birthday to the database.",
    guild_ids=config.server_list)
async def birthday_add(ctx, date: str):
    try:
        bday = sqlite3.connect('./asset/birthdays.db')
        cur = bday.cursor()
    except:
        logging.critical('CONNECTION ERROR WITH BIRTHDAY DATABASE')
        await ctx.send("Sorry I'm having issues connecting to the birthday database."
                       " <@!83792409468604416>, fix this shit")
        return

    if is_date(date):
        logging.info("Date is in acceptable format: {}".format(date))
    else:
        ctx.send("That date isn't in a format I can understand. Try using a different format (I'm pretty flexible)",
                 hidden=True)
    sqlstmt = "INSERT INTO BIRTHDAY VALUES ({}, {}, {})".format(ctx.author.id, parse(date).day, parse(date).month)
    logging.info("Executing SQL: {}".format(sqlstmt))
    try:
        cur.execute(sqlstmt)
        await ctx.send("Thanks <@!{}>! Your birthday has been added to the database".format(ctx.author.id), hidden=True)
    except sqlite3.IntegrityError:
        logging.critical("USER ALREADY HAS A BIRTHDAY IN DB")
        await ctx.send("Error in birthday add. User probably already exists in the DB. If you need"
                       " to change or delete your birthday from the database, talk to Vavs")
    except sqlite3.OperationalError:
        logging.critical("Operational error. Database is probably locked by admin")
        await ctx.send("Hey Vavs, I can't access the database. Is your DB Browser open? What an amateur...")
    bday.commit()
    bday.close()


@slash.slash(
    name="birthday",
    description="Get the birthday of a user",
    guild_ids=config.server_list)
async def birthday(ctx, user: str):
    try:
        bday = sqlite3.connect('./asset/birthdays.db')
        cur = bday.cursor()
    except:
        logging.critical('CONNECTION ERROR WITH BIRTHDAY DATABASE')
        await ctx.send("Sorry I'm having issues connecting to the birthday database."
                       " <@!83792409468604416>, fix this shit")
        return
    args = user.strip()[3:-1]
    sqlstmt = "SELECT * FROM BIRTHDAY WHERE ID = {}".format(args)
    logging.info("Running SQL Query: {}".format(sqlstmt))
    cur.execute(sqlstmt)
    birth = cur.fetchone()
    if birth is None:
        logging.info("{} not found in DB".format(args))
        await ctx.send("I'm sorry, <@!{}>'s birthday isn't in the database. You can add your own "
                       "birthday by doing '/birthdayadd $DATE'.".format(args), hidden=True)
    else:
        day = birth[1]
        month = birth[2]
        snowflake = birth[0]
        response = parse("{}/{}".format(month, day)).strftime("%B %e")
        await ctx.send("<@{}>'s birthday is on {}!".format(snowflake, response), hidden=True)
    bday.close()


@slash.slash(
    name="join",
    description="Join a game-specific role to get access to channels. Enter 'help' for a list of roles",
    guild_ids=config.server_list)
async def join(ctx, role="help"):
    if role == "help":
        channel_list = list(config.channel_roles.keys())
        await ctx.send("To join a channel of interest, use /join followed by any of the following "
                       "channels: \n{}".format(channel_list), hidden=True)
        return
    user_roles = ctx.author.roles
    if config.channel_roles.get(role) is None:
        await ctx.send("{} is not a valid server group. To see a list, do !join help".format(role), hidden=True)
        return
    else:
        role_id = config.channel_roles.get(role)
        logging.info("checking guild roles...")
        role = get(ctx.guild.roles, id=role_id)
        if role in user_roles:
            logging.warning("user already in role. Scolding...")
            await ctx.send("You are already in that role. To leave, type !leave {}".format(role))
        else:
            await ctx.author.add_roles(role, reason="automated")
            logging.info("added {} role to {}".format(role, ctx.author))
            await ctx.send("added {} role to {}!".format(role, ctx.author), hidden=True)


@slash.slash(
    name="leave",
    description="Used to leave a channel group. Enter 'help' to see a list of available channels",
    guild_ids=config.server_list)
async def leave(ctx, role="help"):
    if role == "help":
        channel_list = list(config.channel_roles.keys())
        await ctx.send("To leave a channel you no longer want, use /leave followed by any of the following "
                       "channels (you have to be in the channel): \n{}".format(channel_list), hidden=True)
        return
    user_roles = ctx.author.roles

    if config.channel_roles.get(role) is None:
        await ctx.send("{} is not a valid server group. To see a list, do !join help".format(role), hidden=True)
        return
    else:
        role_id = config.channel_roles.get(role)
        role = get(ctx.guild.roles, id=int(role_id))
        if role in user_roles:
            await ctx.author.remove_roles(role, reason="automated")
            logging.info("removed {} role from {}".format(role, ctx.author))
            await ctx.send("removed {} role from {}!".format(role, ctx.author), hidden=True)
        else:
            logging.warning("user not in group. Scolding...")
            await ctx.send("You aren't in that group. To join, type !join {}".format(role), hidden=True)


@slash.slash(
    name="accept",
    description="By running this command you accept the rules in #welcome",
    guild_ids=config.server_list, )
async def accept(ctx):
    user_roles = ctx.author.roles
    role = get(ctx.guild.roles, id=config.member_role)
    logging.info("Channel id = {}".format(ctx.channel.id))
    if ctx.channel.id != config.welcome_channel:
        await ctx.send("That command only works in the <#{}> channel.".format(config.welcome_channel), hidden=True)
        return
    if role in user_roles:
        logging.warning("user already a member.")
        await ctx.send("You are already a member of the Exhibit", hidden=True)
    else:
        await ctx.author.add_roles(role, reason="accepted rules")
        await ctx.send("Role added! Welcome to the Exhibit!", hidden=True)
        logging.info("added {} role to {}".format(role, ctx.author))


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
    sqlstmt = "SELECT ID FROM BIRTHDAY WHERE DAY = {} AND MONTH = {}".format(day, month)
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
