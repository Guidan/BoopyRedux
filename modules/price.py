import logging

import requests
from config import itad_api_key


async def main(message, content):
    if len(content) < 2:
        await message.channel.send("You need to tell me what game I'm looking up. For more info, do !price help")
        return

    # Pull game plain from chat content
    game_name = " ".join(content[1:])
    plain_header = {
        "key": itad_api_key,
        "title": game_name
    }
    res = requests.get("https://api.isthereanydeal.com/v02/game/plain/", params=plain_header)

    if not res.json()['.meta']['match']:
        logging.warning("unable to find plain for {}".format(game_name))
        await message.channel.send("I was unable to find that title on isthereanydeal.com")
        return
    game_plain = res.json()['data']['plain']
    logging.info("Game plain found: {}".format(game_plain))

    # Get current prices from API
    prices_params = {
        "key": itad_api_key,
        "plains": game_plain
    }
    res = requests.get("https://api.isthereanydeal.com/v01/game/prices/", params=prices_params)
    # Check if there are no prices listed to catch errors
    if not res.json()['data'][game_plain]['list']:
        logging.warning("No prices found, but plain exists. Returning...")
        url = res.json()['data'][game_plain]['urls']['game']
        await message.channel.send("No prices listed for that game. See page here: {}".format(url))
        return
    price = res.json()['data'][game_plain]['list'][0]['price_new']
    logging.info(price)
    price_url = res.json()['data'][game_plain]['list'][0]['url']

    # Get historical low from API
    lowest_params = {
        "key": itad_api_key,
        "plains": game_plain
    }
    res = requests.get("https://api.isthereanydeal.com/v01/game/lowest/", params=lowest_params)
    lowest = res.json()['data'][game_plain]['price']
    url = res.json()["data"][game_plain]["urls"]["game"]

    await message.channel.send("**Price info for {}**\n**Price**: ${}\n**URL**:{}\n\n**History Lowest**: $"
                               "{}\n\n_prices are from isthereanydeal.com_".format(game_name, price, price_url,lowest))


async def help(message):
    await message.channel.send("To get pricing info on any game. Type !price <game name>. "
                               "Prices are pulled from isthereanydeal.com")