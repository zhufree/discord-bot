import discord
import logging
from discord.ext import commands
from config import *
import httpx
import json
import sqlite3
import os, re, random
import time
from zhconv import convert
# import emoji

from site_parser import parse_weibo_m_url, parse_weibo_url, parse_wechat_url, parse_jjwxc_url, parse_douban_url, translate_msg

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

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix= (get_prefix), intents=intents)
last_url = ''

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    global last_url
    if message.author.bot:
        return
    if 'https://mp.weixin.qq.com/s' in message.content:
        urls = re.findall(r'https://mp\.weixin\.qq\.com/s/\S+', message.content)
        for url in urls:
            detail = parse_wechat_url(url)
            embed = discord.Embed(
                title=detail['title'],
                description=detail['content'],
                url=url,
                color=5763719
            )
            embed.set_image(url=detail['img'])
            embed.set_author(
                name=detail['author'],
                icon_url=detail['head']
            )
            await message.channel.send(embed=embed)
    elif 'https://weibo.com/' in message.content:
        urls = re.findall(r'https://weibo.com/\d+/\S+', message.content)
        for url in urls:
            detail = parse_weibo_url(url)
            embed = discord.Embed(
                title=detail['title'],
                description=detail['content'],
                url=url,
                color=5763719
            )
            embed.set_author(
                name=detail['author'],
                icon_url=detail['head']
            )
            if len(detail['pics']) > 0:
                embed.set_image(url=detail['pics'][0])
            await message.channel.send(url + ' send by ' + message.author.mention, embed=embed)
            if len(detail['pics']) > 1:
                if len(detail['pics']) < 5:
                    await message.channel.send('\n'.join(detail['pics'][1:]))
                else:
                    await message.channel.send('\n'.join(detail['pics'][1:5]))
    elif 'https://m.weibo.cn/' in message.content:
        urls = re.findall(r'https://m.weibo.cn/\d+/\d+', message.content) + re.findall(r'https://m.weibo.cn/status/\d+', message.content)
        for url in urls:
            detail = parse_weibo_m_url(url)
            embed = discord.Embed(
                title=detail['title'],
                description=detail['content'],
                url=detail['url'],
                color=5763719
            )
            embed.set_author(
                name=detail['author'],
                icon_url=detail['head']
            )
            if len(detail['pics']) > 0:
                embed.set_image(url=detail['pics'][0])
            await message.channel.send(detail['url'] + ' send by ' + message.author.mention, embed=embed)
            if len(detail['pics']) >= 2:
                if len(detail['pics']) < 5:
                    await message.channel.send('\n'.join(detail['pics'][1:]))
                else:
                    await message.channel.send('\n'.join(detail['pics'][1:5]))
    elif 'https://www.jjwxc.net/onebook.php?novelid=' in message.content:
        urls = re.findall(r'https://www\.jjwxc\.net/onebook\.php\?novelid=\d+', message.content)
        for url in urls:
            if url == last_url:
                pass
            else:
                last_url = url
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
    elif message.content.startswith('https://www.mtlnovel.com/'):
        url = message.content.split(' ')[0]
    elif 'https://www.douban.com/group/topic/' in message.content:
        urls = re.findall(r'https://www\.douban\.com/group/topic/\d+', message.content)
        for url in urls:
            if url == last_url:
                pass
            else:
                last_url = url
                douban_info = parse_douban_url(url)
                embed = discord.Embed(
                    title = douban_info['title'],
                    description=douban_info['content'],
                    url=url
                )
                embed.set_author(name=douban_info['author'])
                embed.set_thumbnail(url=douban_info['author_pfp'])
                embed.set_footer(text='powered by CNYuriTranslation')
                if len(douban_info['pics']) > 0:
                    embed.set_image(url=douban_info['pics'][0])
                embed.add_field(name="time",value=douban_info['time'])
                await message.channel.send(douban_info['url'] + ' send by ' + message.author.mention, embed=embed)
                if len(douban_info['pics']) >= 2:
                    if len(douban_info['pics']) < 5:
                        await message.channel.send('\n'.join(douban_info['pics'][1:]))
                    else:
                        await message.channel.send('\n'.join(douban_info['pics'][1:5]))
    else:
        await bot.process_commands(message)

# @bot.event
# async def on_reaction_add(reaction, user):
#     if type(reaction.emoji) == str:
#         emoji_str = emoji.demojize(reaction.emoji)
#         if emoji_str == ':United_States:' or emoji_str == ':United_Kingdom:':
#             msg = translate_msg(reaction.message.content)
#             embed = discord.Embed(
#                 description=msg,
#                 color=5763719
#             )
#             await reaction.message.channel.send(embed=embed)


@commands.command(name='changeprefix', aliases=['cp'], brief='Change command prefix of the bot.')
@commands.has_permissions(administrator=True)
async def change_prefix(ctx, prefix=''):
    if prefix == '':
        await ctx.send("You should add the prefix you want after ths command.")
    else:
        save_prefix(ctx.guild.id, prefix)
        await ctx.send("Prefix has been changed to {}".format(prefix))

bot.add_command(change_prefix)

@bot.command(name='test', aliases=['t'], brief='Show a sentence of a poetry.')
async def test(ctx, *args):
    file_path = 'test.mp3'
    file = discord.File(file_path, filename='test.mp3')
    await ctx.send("Here is your file:", file=file)

@bot.command(name='一言', aliases=['yiyan', 'yy'], brief='Show a simple sentece.')
async def yiyan(ctx, *args):
    msg = httpx.get('https://v1.hitokoto.cn/?encode=text').text
    if len(args) > 0 and args[0] == 'f':
        msg = convert(msg, 'zh-hant')
    await ctx.send(msg)

@bot.command(name='诗词', aliases=['shici', 'sc'], brief='Show a sentence of a poetry.')
async def shici(ctx, *args):
    res_json = json.loads(httpx.get('https://v1.jinrishici.com/all').text)
    msg = "{}\n——{} {}".format(res_json['content'], res_json['origin'], res_json['author'])
    if len(args) > 0 and args[0] == 'f':
        msg = convert(msg, 'zh-hant')
    await ctx.send(msg)


if __name__ == '__main__':
    # test()
    # init_db()
    bot.run(chinese_helper_token)
    # bot.run(discord_bot_token)
    # print(get_prefix('test'))
    