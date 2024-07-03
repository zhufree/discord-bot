import discord
from discord.ext import commands
from config import *
import os, random, json

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='~', intents=intents)

def get_random_audio(key:str):
    target_dir = f'audios/{key}/'
    audio_list = os.listdir(target_dir)
    result_file = random.choice(audio_list)
    file_path = os.path.join(target_dir, result_file)
    filename = result_file.split('/')[-1]
    with open('audios/audio.json', 'r', encoding='utf-8') as f:
        file_dict = json.load(f)
        file_desc = file_dict[key][filename.split('.')[0]]
    return (filename, file_desc, file_path)
    
@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.command(name='info', brief='Information.')
async def info(ctx, *args):
    await ctx.send('Use ~ as prefix, available command: qiyan/qy for qiyan voice, jingnu/jn for jingnu voice, support the jwwj audio drama by purchasing on missevan: https://x.com/jwwj_official/status/1653660028350644225')

@bot.command(name='qiyan', aliases=['qy', 'jingnu', 'jn'], brief='Get a random voice.')
async def random_voice(ctx, *args):
    key = 'qiyan'
    if ctx.invoked_with in ['qiyan', 'qy']:
        key = 'qiyan'
    elif ctx.invoked_with in ['jingnu', 'jn']:
        key = 'jingnu'
    filename, file_desc, file_path = get_random_audio(key)
    file = discord.File(file_path, filename=filename)
    await ctx.send(file_desc, file=file)

if __name__ == '__main__':
    bot.run(jwwj_bot_token)
