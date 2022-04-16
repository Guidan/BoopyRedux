import logging

gold = 0
silver = 0
copper = 0
platinum = 0


async def main(message, content):
    global gold, silver, copper, platinum
    content.pop(0)
    if len(content) < 1:
        await message.channel.send("I need to know what currency to add!")
        return
    for loot in content:
        try:
            lootType = loot[-1]
            loot = int(loot.rstrip(lootType))
            if lootType == 'p':
                platinum += loot
            elif lootType == 'g':
                gold += loot
            elif lootType == 'c':
                copper += loot
            elif lootType == 's':
                silver += loot
            elif lootType == 'e':
                silver += (loot*5)
            else:
                await message.channel.send("I don't know wtf this is => {}{}".format(loot, lootType))

        except ValueError:
            await message.channel.send("Something is wrong with the numbers you gave me. \nCheck to make sure you follow the"
                                 " syntax: `#c #g #p`. The order doesn't matter but the letter must always follow the number")
            return
    logging.info("Platinum:{} Gold:{} Silver:{} Copper:{}".format
                 (platinum, gold, silver, copper))


async def help(message):
    await message.channel.send("This function adds currency loot to a table (and converts electrum to silver)."
                               " To add to the pile, use the syntax: `!lootadd #p #g #s #e #c`"
                               "\nThe order doesn't matter but the number amount must be before the type of currency.")


# Function to reset loot pile to initial values
def resetLoot():
    global gold, silver, copper, platinum
    gold = 0
    silver = 0
    copper = 0
    platinum = 0