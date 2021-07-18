import logging
import sqlite3
from dateutil.parser import parse


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
        date = False
        logging.info("empty args for {}".format(args))
    else:
        args = content[1:]
        args = " ".join(args)
        if is_date(args):
            logging.info("Date is in acceptable format: {}".format(args))
            date = True
        else:
            date = False
            if args.startswith("<@"):
                args = args[3:-1]
            else:
                await message.channel.send("Hello! To use the birthday function, use either of these syntaxes"
                                           "\n'!birthday @User' to check that Users birthday (if it exists in DB)"
                                           "\n'!birthday MM/DD' to save your birthday to the DB")
                return

    try:
        bday = sqlite3.connect('.\\asset\\birthdays.db')
        cur = bday.cursor()
    except:
        logging.critical('CONNECTION ERROR WITH BIRTHDAY DATABASE')
        await message.channel.send("Sorry I'm having issues connecting to the birthday database."
                                   " <@!83792409468604416>, fix this shit")
        return
    if date:
        sqlstmt = "INSERT INTO BIRTHDAY VALUES ({}, {}, {})".format(message.author.id, parse(args).day, parse(args).month)
        logging.info("Executing SQL: {}".format(sqlstmt))
        try:
            cur.execute(sqlstmt)
            await message.channel.send("Thanks <@!{}>! Your birthday has been added to the database".format(message.author.id))
        except sqlite3.IntegrityError:
            logging.critical("USER ALREADY HAS A BIRTHDAY IN DB")
            await message.channel.send("Error in birthday add. User probably already exists in the DB. If you need"
                                       " to change or delete your birthday from the database, alert my admin")
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
