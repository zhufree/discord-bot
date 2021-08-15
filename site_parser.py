from pyquery import PyQuery as pq
import requests
import re
from googletrans import Translator

translator = Translator()

def parse_weibo_m_url(url):
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


def parse_weibo_url(url):
    res = requests.get(url, headers={
        'Host': 'weibo.com',
        'Cookie': 'SINAGLOBAL=3195376581295.619.1629021665163; ULV=1629021665207:1:1:1:3195376581295.619.1629021665163:; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFU0qlXF-MD4FdyiOvX8XzY; SUB=_2AkMXyYMQf8NxqwJRmPESxW3qb4h0yAzEieKhlXLLJRMxHRl-yT9jql04tRB6PEmt_1-7hJ1pSq-FqHDd8OxSkNvAL3Zg; _s_tentry=-; Apache=3195376581295.619.1629021665163',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    })
    html_content = res.text
    title = pq(html_content)('title').text()
    contents = re.findall(r'"html":"(.*)"', html_content)
    if len(contents) > 0:
        doc = pq(contents[-1].replace('\n', '').replace('\r', '').replace(r'>\s+<', '')\
            .replace('\\n', '').replace('\\', ''))
        print(doc.html())
        content = doc('.WB_text').text()
        author = doc('.WB_text').attr('nick-name')
        head = doc('img.W_face_radius').attr('src')
        imgs = ['https:' + i.attr('src') for i in list(doc('li>img').items())]
        video_search = re.search(r'f.video(\S+)&amp;cover', doc.html())
        video_url = None
        if video_search != None:
            video_url = 'https://f.video' + video_search.group(1)\
                .replace('%2F', '/').replace('%3F', '?').replace('%26', '&')\
                .replace('%3D', '=').replace('%2C', ',')
        return {
            'title': title,
            'author': author,
            'head': head,
            'content': content.replace('\n', ''),
            'imgs': imgs,
            'video_url': video_url
        }
    else:
        return None


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
    # print(parse_weibo_m_url('https://m.weibo.cn/status/4669070841222847'))
    # print(parse_weibo_url('https://weibo.com/7224928421/KsYQA587l'))
    print(parse_weibo_url('https://weibo.com/3947333230/KtA9KdESb'))
    # print(parse_wechat_url('https://mp.weixin.qq.com/s/YwHhX-A8tRJ37RCNHqLxdQ '))
    # print(parse_jjwxc_url('http://www.jjwxc.net/onebook.php?novelid=4472787'))
    # print(translate_msg('你好'))
#//wx3.sinaimg.cn/mw690/eb47866ely1gthl2bh3o5j21h90u07g4.jpg