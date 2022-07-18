from discord.ext import commands
import discord
import os, random
from config import *

RABBIT_DIR = './imgs/xrabbits/'
BOX_GIF_URL = 'https://p.qlogo.cn/hy_personal/3e28f14aa0516842a7556984f3d4eeea0d27b7d6546fb2980c3607c086b5debc/0.gif'
bot = commands.Bot(command_prefix='-', )

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.command(name='mint', brief='Mint a X Rabbit.')
async def mint(ctx, *args):
    embed = discord.Embed(
        title='Mint a X Rabbit',
        url='https://opensea.io/collection/xrc',
        color=5763719
    )
    embed.set_image(url=BOX_GIF_URL)
    message = await ctx.reply(embed=embed)
    reveal_ic = "🔄"
    await message.add_reaction(reveal_ic)
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == reveal_ic

    reaction, user = await bot.wait_for('reaction_add', check=check)
    if reaction != None:
        # reveal
        randint = random.randint(0, 7502)
        embed = discord.Embed(
            title=f'X Rabbit#{randint}',
            url=f'https://opensea.io/assets/0x534d37c630b7e4d2a6c1e064f3a2632739e9ee04/{randint}',
            color=5763719
        )
        embed.set_image(url=f'https://xrcmeme.io/static/QmShUrXkgxjQ1eeCuo7hywsK42cGYj6KQ8N5XomM7d9A9M/{randint}.png')
        await message.edit(embed=embed)


if __name__ == '__main__':
    # init_db()
    bot.run(chinese_helper_token)
    # bot.run(discord_bot_token)
    # print(get_prefix('test'))
    