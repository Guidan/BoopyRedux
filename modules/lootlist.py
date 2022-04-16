import logging
from modules import lootadd


async def main(message, content):
    await message.channel.send("Platinum:{}\nGold:{}\nSilver:{}\nCopper:{}".format
                               (lootadd.platinum, lootadd.gold, lootadd.silver, lootadd.copper))


async def help(message):
    await message.channel.send("This command lists the current loot pile numbers")
