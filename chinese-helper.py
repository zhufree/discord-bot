import discord
import logging
from discord.ext import commands
from config import *
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

client = discord.Client()

bot = commands.Bot(command_prefix='.')

@bot.command(name='一言')
async def test(ctx):
    await message.channel.send('Hello!')
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(chinese_helper_token)