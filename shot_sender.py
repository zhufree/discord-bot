# coding:utf-8
from telegram.ext import Updater
from telegram import User
from pyquery import PyQuery as pq
import logging
import sys
import time
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
import discord
import asyncio
import multiprocessing
from config import *

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 启动discord client
client = discord.Client()
loop = client.loop
print(loop)
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


# 启动telegram client
# updater = Updater(token=telegram_bot_token, request_kwargs={'proxy_url': 'socks5h://127.0.0.1:1080/'}, use_context=True)

class ImgHandler(LoggingEventHandler):
    last_img_path = ''
    def on_created(self, event):
        super(LoggingEventHandler, self).on_created(event)
        what = 'directory' if event.is_directory else 'file'
        # 排除生成的缩略图和重复log
        if 'thumbnails' not in event.src_path and event.src_path != self.last_img_path:
            logging.info("Created %s: %s", what, event.src_path)
            NameExt = event.src_path.split('.')
            if NameExt[-1] == 'jpg': # jpg后缀判断截图
                logging.info("有新截图...")
                last_img_path = event.src_path
                path_list = event.src_path.split('\\')
                game_id = path_list[-3] # 获取路径中的游戏id
                game_title = get_game_title(game_id) # 根据id获取游戏名
                # send_photo_to_tg(event.src_path, game_title)
                future = asyncio.run_coroutine_threadsafe(send_photo_to_discord(event.src_path, game_title), loop)
                future.result()


# 发送到discord channel
async def send_photo_to_discord(file_path, game_title):
    channel = client.get_channel(discord_channel_id)
    await channel.send(content='Send via discord+zapier #gameshot #{}'.format(game_title), file=discord.File(file_path))


# 发送到telegram channel，因为会自动压缩，改用discord
def send_photo_to_tg(file_path, game_title):
    updater.bot.send_photo(chat_id=telegram_channel_name, caption='Send via telegram+ifttt #gameshot #{}'.format(game_title), photo=open(file_path, 'rb'))


# 打开steam页面获取游戏名
def get_game_title(game_id):
    doc = pq('https://store.steampowered.com/app/{}/'.format(game_id))
    print(doc('.apphub_AppName').text())
    return doc('.apphub_AppName').text()

def start_discord_client():
    client.run(discord_bot_token)

def observe_file():
    print('observer file')
    # 生成事件处理器对象
    event_handler = ImgHandler()

    # 生成监控器对象
    observer = Observer()
    # 注册事件处理器，配置监控目录
    observer.schedule(event_handler, userdata_dir_path, recursive=True)
    # 监控器启动——创建线程
    observer.start()

    # 以下代码是为了保持主线程运行
    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     observer.stop()

    # 主线程任务结束之后，进入阻塞状态，一直等待其他的子线程执行结束之后，主线程再终止
    # observer.join()

# def main():
observe_file()
client.run(discord_bot_token)



if __name__ == '__main__':
    # asyncio.run(main())
    pass
