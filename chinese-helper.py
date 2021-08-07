import discord
import logging
from discord.ext import commands
from config import *
import requests
import json
import sqlite3
import os 
import time
from zhconv import convert

from site_parser import parse_weibo_url, parse_wechat_url, parse_jjwxc_url

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
    elif message.content.startswith('http://www.jjwxc.net/onebook.php?novelid='):
        url = message.content.split(' ')[0]
        novel_info = parse_jjwxc_url(url)
        embed = discord.Embed(
            title = novel_info['title'],
            description=novel_info['summary'],
            url=url
        )
        embed.set_author(name=novel_info['author'])
        embed.add_field(name="tags",value=novel_info['tags'])
        embed.add_field(name="status",value=novel_info['status'])
        embed.add_field(name="other data",value=novel_info['other_info'])
        embed.set_thumbnail(url=novel_info['cover'])
        embed.set_footer(text='powered by CNYuriTranslation')
        await message.channel.send(embed=embed)
    else:
        await bot.process_commands(message)


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
async def yiyan(ctx, *args):
    msg = requests.get('https://v1.hitokoto.cn/?encode=text').text
    if len(args) > 0 and args[0] == 'f':
        msg = convert(msg, 'zh-hant')
    await ctx.send(msg)

@bot.command(name='诗词', aliases=['shici', 'sc'], brief='Show a sentence of a poetry.')
async def shici(ctx, *args):
    res_json = json.loads(requests.get('https://v1.jinrishici.com/all').text)
    msg = "{}\n——{} {}".format(res_json['content'], res_json['origin'], res_json['author'])
    if len(args) > 0 and args[0] == 'f':
        msg = convert(msg, 'zh-hant')
    await ctx.send(msg)


@bot.command(name='热搜', aliases=['resou', 'rs'], brief='Show weibo hot rank.')
async def resou(ctx, *args):
    res_json = json.loads(requests.get('https://api.oioweb.cn/api/summary.php').text)
    title_list = [i['title'] for i in res_json]
    count = 5
    page_index = 0
    msg = '\n'.join(title_list[page_index*count:(page_index+1)*count])
    if len(args) > 0 and args[0] == 'f':
        msg = convert(msg, 'zh-hant')
    message = await ctx.send(msg)
    prev_ic = "⬅️"
    next_ic = "➡️"
    await message.add_reaction(prev_ic)
    await message.add_reaction(next_ic)

    valid_reactions = [prev_ic, next_ic]

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in valid_reactions

    async def reset_reaction():
        await message.clear_reactions()
        await message.add_reaction(prev_ic)
        await message.add_reaction(next_ic)

    reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    while reaction != None:
        if str(reaction.emoji) == next_ic:
            if page_index >= 10: 
                page_index = 0
            else:
                page_index += 1
        else:
            if page_index <= 0: 
                page_index = 0
            else:
                page_index -= 1

        if (page_index+1)*count < len(title_list):
            msg = '\n'.join(title_list[page_index*count:(page_index+1)*count])
        else:
            msg = '\n'.join(title_list[page_index*count:])
        if len(args) > 0 and args[0] == 'f':
            msg = convert(msg, 'zh-hant')
        await message.edit(content=msg)
        await reset_reaction()
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)


def test():
    res_json = json.loads(requests.get('https://api.oioweb.cn/api/summary.php').text)
    title_list = [i['title'] for i in res_json]
    print(len(title_list))

if __name__ == '__main__':
    # test()
    # init_db()
    bot.run(chinese_helper_token)
    # bot.run(discord_bot_token)
    # print(get_prefix('test'))
    