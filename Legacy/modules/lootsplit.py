from Legacy.modules import lootadd


async def main(message, content):
    if len(content) <= 1:
        await message.channel.send("You need to tell me how many players I'm splitting the loot for!")
        return
    else:
        try:
            splitNum = int(content[1])
        except ValueError:
            await message.channel.send("I can only understand number values!")
            return

        denom = {
            "Platinum": 1000,
            "Gold": 100,
            "Silver": 10,
            "Copper": 1
        }
        output = {}
        copperAdd = lootadd.platinum * 1000 + lootadd.gold * 100 + lootadd.silver * 10 + lootadd.copper  # convert all to copper for easy math
        leftover = copperAdd % splitNum  # get the remainder to output later
        copperAdd -= leftover  # remove the remainder from the loot pile for easy math
        copperShare = int(copperAdd/splitNum)
        for key, value in denom.items():
            output[key] = copperShare // value
            copperShare %= value
        lootadd.resetLoot()  # reset the loot pile to 0
        await message.channel.send("Here is the loot split {} ways:\nPlatinum:{}\nGold:{}\nSilver:{}"
                                   "\nCopper:{}".format
                                   (splitNum, output["Platinum"], output["Gold"],output["Silver"],output["Copper"]))
        if leftover > 0:
            await message.channel.send("With {} copper leftover (figure it out amongst yourselves)".format(leftover))


async def help(message):
    await message.channel.send("This command splits the loot for the amount of players specified."
                               "\nSyntax: `!lootsplit <numberOfPlayers>`")
