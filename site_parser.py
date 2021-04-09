from pyquery import PyQuery as pq
import requests
import re


def parse_weibo_url(url):
    doc = requests.get(url).text
    bid = re.search(r'\"bid\":\s\"(.*)\"', doc).group(1)
    uid = re.search(r'\"uid\":\s(.*)', doc).group(1)
    web_url = 'https://weibo.com/{}/{}'.format(uid, bid)
    return web_url


def parse_wechat_url(url):
    doc = pq(url)
    title =doc('#activity-name').text()
    content = doc('#js_content').text().replace('\n\n\n', '\n').strip()[0:200]+'...'
    return (title, content)

if __name__ == '__main__':
    # parser_m_url('https://m.weibo.cn/7462816220/4622537638545785')
    handle_wechat('https://mp.weixin.qq.com/s/YwHhX-A8tRJ37RCNHqLxdQ')