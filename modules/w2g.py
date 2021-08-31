import logging
import requests
from config import w2g_api_key


async def main(message, content):
    if len(content) == 1:
        link = "https://youtu.be/Y1pVQkmcTso"
    else:
        link = content[1]

    data_input = {
        "w2g_api_key": w2g_api_key,
        "share": link,
        "bg_color": "#343434",
        "bg_opacity": "100"
    }
    headers_input = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    await message.delete()
    res = requests.post("https://w2g.tv/rooms/create.json", params=data_input, headers=headers_input)
    w2g_link = "https://w2g.tv/rooms/{}".format(res.json()["streamkey"])
    logging.info("sending link for {}".format(w2g_link))
    await message.channel.send("Here is your link!\n{}".format(w2g_link))


async def help(message):
    await message.channel.send("To create a watch2gether link, simply use !w2g "
                               "<link> to create a room with that video!")
