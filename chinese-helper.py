import discord
import logging
from discord.ext import commands
from config import *
import requests
import json
import sqlite3
import os 
import time
from site_parser import parse_weibo_url, parse_wechat_url

DB_NAME = "bot.db"
def init_db():
    if not os.path.exists("bot.db"):
        connect = sqlite3.connect("bot.db")
        cursor = connect.cursor()
        cursor.execute('''CREATE TABLE [Prefix](
            [GUILD_ID] TEXT PRIMARY KEY    NOT NULL,
            [PREFIX]         INT     NOT NULL);''')
        connect.commit()
        connect.close()

def save_prefix(g_id, pfx):
    connect = sqlite3.connect("bot.db")
    cursor = connect.cursor()
    cursor.execute("""INSERT OR REPLACE INTO Prefix (GUILD_ID, PREFIX) VALUES (?, ?)""", (g_id, pfx))
    connect.commit()
    connect.close()

def get_prefix(client, message):
    connect = sqlite3.connect("bot.db")
    cursor = connect.cursor()
    cursor.execute("""SELECT PREFIX from Prefix WHERE GUILD_ID = "{}";""".format(message.guild.id))
    row = cursor.fetchone()
    if row is None:
        p = '!'
    else:
        p = row[0]
    connect.close()
    return p

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# client = discord.Client()
bot = commands.Bot(command_prefix= (get_prefix), )

@commands.command(name='changeprefix', aliases=['cp'], brief='Change command prefix of the bot.')
@commands.has_permissions(administrator=True)
async def change_prefix(ctx, prefix=''):
    if prefix == '':
        await ctx.send("You should add the prefix you want after ths command.")
    else:
        save_prefix(ctx.guild.id, prefix)
        await ctx.send("Prefix has been changed to {}".format(prefix))

bot.add_command(change_prefix)


@bot.command(name='一言', aliases=['yiyan', 'yy'], brief='Show a simple sentece.')
async def yiyan(ctx):
    msg = requests.get('https://v1.hitokoto.cn/?encode=text').text
    await ctx.send(msg)

@bot.command(name='诗词', aliases=['shici', 'sc'], brief='Show a sentence of a poetry.')
async def shici(ctx):
    res_json = json.loads(requests.get('https://v1.jinrishici.com/all').text)
    msg = "{}\n——{} {}".format(res_json['content'], res_json['origin'], res_json['author'])
    await ctx.send(msg)

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.content.startswith('https://mp.weixin.qq.com/s'):
        url = message.content.split(' ')[0]
        title, content = parse_wechat_url(url)
        await message.channel.send(content)
    elif message.content.startswith('https://m.weibo.cn/'):
        url = message.content.split(' ')[0]
        web_url = parse_weibo_url(url)
        await message.channel.send(web_url)
    else:
        await bot.process_commands(message)

# bot.run(discord_bot_token)

if __name__ == '__main__':
    init_db()
    bot.run(chinese_helper_token)
    # print(get_prefix('test'))
    