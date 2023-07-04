import discord
import importlib
import inspect
import os
from itertools import cycle

from discord.ext import commands, tasks
from dotenv import load_dotenv

from utils.settings import Settings

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

load_dotenv()
TOKEN = os.getenv("TOKEN")
if TOKEN == None:
    print("TOKEN not found in .env file")
    exit()

bot = commands.Bot(intents=intents)
bot.settings = Settings() # type: ignore

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_message(message):
    eta = 'eta'
    if message.content.lower()=="eta":
        await message.reply("There is currently no ETA. Please read <#1120369654653788302>")

status = cycle(['Watching The Server'])

@tasks.loop(seconds=30)
async def status_swap():
    await bot.change_presence(activity=discord.Game(next(status)))

@bot.event
async def on_ready():
    print(f"{bot.user} is ready")
    print("Loading Views")
    status_swap.start()
    for filename in os.listdir("./views"):
        if filename.endswith(".py"):
            classes = [obj for name, obj in inspect.getmembers(importlib.import_module(f"views.{filename[:-3]}")) if inspect.isclass(obj) and issubclass(obj, discord.ui.View)]
            for view in classes:
                bot.add_view(view(bot=bot)) # type: ignore
                print(f"Loaded {view.__name__}")

bot.run(TOKEN)
