from pyquery import PyQuery as pq
import requests
import re
from googletrans import Translator


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


def parse_jjwxc_url(url):
    translator = Translator()
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
        'tags': '{}\n{}'.format(tags, tags_en),
        'summary': '{}\n{}'.format(summary, summary_en),
        'cover': cover
    }
    
    #     'title': '{}/{}'.format(title, title_en),
    #     'author': '{}'.format(author),
    #     'status': '{}'.format(status),
    #     'other_info': 'word count:{}/collected count: {}'.format(wordCount, collectedCount),
    #     'tags': '{}'.format(tags),
    #     'summary': summary,
    #     'cover': cover
    # }


if __name__ == '__main__':
    # parser_weibo_url('https://m.weibo.cn/7462816220/4622537638545785')
    # parse_wechat_url('https://mp.weixin.qq.com/s/YwHhX-A8tRJ37RCNHqLxdQ')
    print(parse_jjwxc_url('http://www.jjwxc.net/onebook.php?novelid=4472787'))