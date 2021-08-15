from pyquery import PyQuery as pq
import requests
import re
from googletrans import Translator

translator = Translator()

def parse_weibo_url(url):
    html_content = requests.get(url).text
    doc = pq(html_content)
    bid = re.search(r'\"bid\":\s\"(.*)\"', html_content).group(1)
    uid = re.search(r'\"uid\":\s(.*)', html_content).group(1)
    web_url = 'https://weibo.com/{}/{}'.format(uid, bid)
    content = pq(re.search(r'\"text\":\s\"(.*)\"', html_content).group(1)).text()
    if (len(content) > 500):
        content = content[0:500]+'...'
    pics = re.findall(r'\"url\":\s\"(.*)\"', html_content)
    large_pics = []
    for i in pics:
        if 'large' in i:
            large_pics.append(i)
    video_url = re.search(r'\"mp4_720p_mp4\":\s\"(.*)\"', html_content).group(1) if 'mp4_720p_mp4' in html_content else None
    return {
        'url': web_url,
        'title': re.search(r'\"status_title\":\s\"(.*)\"', html_content).group(1),
        'author': re.search(r'\"screen_name\":\s\"(.*)\"', html_content).group(1),
        'author_head': re.search(r'\"profile_image_url\":\s\"(.*)\"', html_content).group(1),
        'author_url': re.search(r'\"profile_url\":\s\"(.*)\"', html_content).group(1),
        'content': content,
        'pics': large_pics,
        'video_url': video_url
    }


def parse_wechat_url(url):
    doc = pq(url)
    author = doc('#profileBt > a').text()
    head = list(doc('img').items())[1].attr('data-src')
    img = doc('img.rich_pages:first').attr('data-src')
    title = doc('#activity-name').text()
    content = doc('#js_content').text().replace('\n\n\n', '\n').strip()[0:500]+'...'
    return {
        'title': title,
        'author': author,
        'head': head,
        'img': img,
        'content': content
    }


def parse_jjwxc_url(url):
    res = requests.get(url)
    res.encoding = 'gb2312'
    doc = pq(res.text)
    title = doc('span[itemprop=articleSection]').text()
    title_en = translator.translate(title).text
    author = doc('span[itemprop=author]').text()
    author_en = translator.translate(author).text
    status = doc('span[itemprop=updataStatus]').text()
    status_en = translator.translate(status).text
    wordCount = doc('span[itemprop=wordCount]').text()
    collectedCount = doc('span[itemprop=collectedCount]').text()
    summary = doc('div[itemprop=description]').text().replace('~', '').replace('||', '|')
    summary_en = translator.translate(summary).text.replace('~', '').replace('||', '|')
    tags = doc('div.smallreadbody>span>a').text().replace(' ', '/')
    cover = doc('img.noveldefaultimage').attr('src')
    tags_en = translator.translate(tags).text
    return {
    # {
        'title': '{}({})'.format(title, title_en),
        'author': '{}({})'.format(author, author_en),
        'status': '{}/{}'.format(status, status_en),
        'other_info': 'word count:{}\ncollected count: {}'.format(wordCount.replace('字', 'chars'), collectedCount),
        'tags': '{}'.format(tags_en),
        'summary': '{}'.format(summary_en),
        'cover': cover
    }


def translate_msg(msg):
    return translator.translate(msg).text

if __name__ == '__main__':
    print(parse_weibo_url('https://m.weibo.cn/status/4669070841222847'))
    # print(parse_weibo_url('https://m.weibo.cn/status/4669872175319179'))
    # print(parse_wechat_url('https://mp.weixin.qq.com/s/YwHhX-A8tRJ37RCNHqLxdQ '))
    # print(parse_jjwxc_url('http://www.jjwxc.net/onebook.php?novelid=4472787'))
    # print(translate_msg('你好'))
