from discord.ext import commands
import discord
from config import *

BOX_FILE = './imgs/x-rabbits-box.gif'
TEST_RABBIT = './imgs/xrabbits/0.jpg'
bot = commands.Bot(command_prefix='-', )

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    await bot.process_commands(message)


@bot.command(name='mint', brief='Mint a X Rabbit.')
async def mint(ctx, *args):
    message = await ctx.reply(file=discord.File(BOX_FILE))
    reveal_ic = "🔄"
    await message.add_reaction(reveal_ic)
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == reveal_ic

    reaction, user = await bot.wait_for('reaction_add', check=check)
    while reaction != None:
        # reveal
        await message.delete()
        await ctx.reply(file=discord.File(TEST_RABBIT))


if __name__ == '__main__':
    # test()
    # init_db()
    bot.run(chinese_helper_token)
    # bot.run(discord_bot_token)
    # print(get_prefix('test'))
    