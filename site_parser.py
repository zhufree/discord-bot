from pyquery import PyQuery as pq
import httpx
import re
from config import weibo_cookies

def parse_weibo_m_url(url):
    mid = url.split('/')[-1]
    uid = url.split('/')[-2] # uid可能没有
    web_url = 'https://weibo.com/{}/{}'.format(uid, mid)
    return parse_weibo_url(web_url)


def parse_weibo_url(url):
    weibo_id = re.split(r'[?#]', url)[0].split('/')[-1]
    detail_url = 'https://weibo.com/ajax/statuses/show?id=' + weibo_id
    res = httpx.get(detail_url)
    detail_json = res.json()
    pics = []
    video_url = ''
    long_content = None
    if detail_json['ok'] == 1:
        if 'pic_infos' in detail_json:
            for pic_info in detail_json['pic_infos'].values():
                pics.append(pic_info['large']['url'])
        if 'page_info' in detail_json and 'media_info' in detail_json['page_info']:
            video_url = detail_json['page_info']['media_info']['h5_url']
        if 'continue_tag' in detail_json and weibo_cookies != '':
            expand_res = httpx.get('https://weibo.com/ajax/statuses/longtext?id=' + weibo_id, headers={'Cookie': weibo_cookies})
            try:
                expand_json = expand_res.json()
                if expand_json['ok'] == 1:
                    long_content = expand_json['data']['longTextContent']
            except Exception:
                pass
            finally:
                pass
        return {
            'title': '',
            'url': url,
            'author': detail_json['user']['screen_name'],
            'head': detail_json['user']['profile_image_url'],
            'content': long_content if long_content != None else detail_json['text_raw'],
            'pics': pics,
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
    res = httpx.get(url)
    res.encoding = 'gb2312'
    doc = pq(res.text)
    title = doc('span[itemprop=articleSection]').text()
    # title_en = translator.translate(title).text
    author = doc('span[itemprop=author]').text()
    # author_en = translator.translate(author).text
    status = doc('span[itemprop=updataStatus]').text()
    # status_en = translator.translate(status).text
    wordCount = doc('span[itemprop=wordCount]').text()
    collectedCount = doc('span[itemprop=collectedCount]').text()
    summary = doc('div[itemprop=description]').text().replace('~', '').replace('||', '|')
    # summary_en = translator.translate(summary).text.replace('~', '').replace('||', '|')
    tags = doc('div.smallreadbody>span>a').text().replace(' ', '/')
    cover = doc('img.noveldefaultimage').attr('src')
    # tags_en = translator.translate(tags).text
    return {
        # 'title': '{}({})'.format(title, title_en),
        # 'author': '{}({})'.format(author, author_en),
        # 'status': '{}/{}'.format(status, status_en),
        'title': title,
        'author': author,
        'status': status,
        'other_info': 'word count:{}\ncollected count: {}'.format(wordCount.replace('字', 'chars'), collectedCount),
        'tags': tags,
        'summary': summary,
        'cover': cover
    }

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
}

def parse_douban_url(url):
    res = httpx.get(url, headers=header)
    doc = pq(res.text)
    imgs = doc('.topic-doc img').items()
    pics = []
    for i in imgs:
        pics.append(i.attr('src'))
    return {
        'url': url,
        'title': doc('.article h1').text(),
        'content': doc('.topic-doc p').text(),
        'time': doc('span.create-time').text(),
        'author': doc('span.from').text(),
        'author_pfp': doc('img.pil').attr('src'),
        'pics': pics
    }

def translate_msg(msg):
    return translator.translate(msg).text

if __name__ == '__main__':
    # print(parse_weibo_m_url('https://m.weibo.cn/status/4669070841222847'))
    # print(parse_weibo_url('https://weibo.com/7224928421/KsYQA587l'))
    # print(parse_weibo_url('https://weibo.com/3947333230/KtA9KdESb'))
    # print(parse_wechat_url('https://mp.weixin.qq.com/s/YwHhX-A8tRJ37RCNHqLxdQ '))
    # print(parse_jjwxc_url('https://www.jjwxc.net/onebook.php?novelid=4472787'))
    # print(translate_msg('你好'))
    print(parse_douban_url('https://www.douban.com/group/topic/271430038/'))
