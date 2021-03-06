import logging
import sqlite3
from config import birthdayChannels
from dateutil.parser import parse
from datetime import date


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


async def main(message, content):

    if len(content) < 2:
        args = message.author.id
        datename = False
        logging.info("empty args for {}".format(args))
    else:
        args = content[1:]
        args = " ".join(args)
        if is_date(args):
            logging.info("Date is in acceptable format: {}".format(args))
            datename = True
        else:
            datename = False
            if args.startswith("<@"):
                args = args.strip()[3:-1]
            else:
                await message.channel.send("Hello! To use the birthday function, use either of these syntaxes"
                                           "\n'!birthday @User' to check that Users birthday (if it exists in DB)"
                                           "\n'!birthday MM/DD' to save your birthday to the DB")
                return

    try:
        bday = sqlite3.connect('./asset/birthdays.db')
        cur = bday.cursor()
    except:
        logging.critical('CONNECTION ERROR WITH BIRTHDAY DATABASE')
        await message.channel.send("Sorry I'm having issues connecting to the birthday database."
                                   " <@!83792409468604416>, fix this shit")
        return
    if datename:
        sqlstmt = "INSERT INTO BIRTHDAY VALUES ({}, {}, {})".format(message.author.id, parse(args).day, parse(args).month)
        logging.info("Executing SQL: {}".format(sqlstmt))
        try:
            cur.execute(sqlstmt)
            await message.channel.send("Thanks <@!{}>! Your birthday has been added to the database".format(message.author.id))
        except sqlite3.IntegrityError:
            logging.critical("USER ALREADY HAS A BIRTHDAY IN DB")
            await message.channel.send("Error in birthday add. User probably already exists in the DB. If you need"
                                       " to change or delete your birthday from the database, alert my admin")
        except sqlite3.OperationalError:
            logging.critical("Operational error. Database is probably locked by admin")
            await message.channel.send("Hey Vavs, I can't access the database. Is your DB Browser open? What an amateur...")
        bday.commit()
        bday.close()
    else:
        sqlstmt = "SELECT * FROM BIRTHDAY WHERE ID = {}".format(args)
        logging.info("Running SQL Query: {}".format(sqlstmt))
        cur.execute(sqlstmt)
        birth = cur.fetchone()
        if birth is None:
            logging.info("{} not found in DB".format(args))
            await message.channel.send("I'm sorry, <@!{}>'s birthday isn't in the database. You can add your own "
                                       "birthday by doing '!birthday $DATE'.".format(args))
        else:
            day = birth[1]
            month = birth[2]
            ID = birth[0]
            response = parse("{}/{}".format(month, day)).strftime("%B %e")
            await message.channel.send("<@{}>'s birthday is on {}!".format(ID, response))
    bday.close()


async def help(message):
    await message.channel.send("Hello! To use the birthday function, use either of these syntaxes"
                               "\n'!birthday @User' to check that Users birthday (if it exists in DB)"
                               "\n'!birthday $DATE' to save your birthday to the DB")


async def birthday_check(client):
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
                await generalchannel.send("@here ???????????????? Today is <@!{}>'s birthday!"
                                          " Be sure to wish them a happy birthday! ????????????????".format(bdayboi))

    bday.close()
