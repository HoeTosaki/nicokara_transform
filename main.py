import requests
from bs4 import BeautifulSoup
import urllib.request


def requests_html(url):
    # 我们增加一个headers，如果不加，网易云会认为我们是爬虫程序，从而拒绝我们的请求
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE',
    }
    # 利用requests模块请求网易云的歌词页面
    demo = requests.get(url, headers=headers)
    # 如果正确获取到网页则返回文本内容
    if demo.status_code == 200:
        return  demo.text
    else:
        print(url,"请求失败")


def parser_html(txt):
    # 这里我就不异常处理了，直接获取内容，eval函数把文本内容转换为字典
    dic = eval(text)
    print("文本当前的数据类型是:",type(dic))
    # 字典是键值对类型的，获取歌词部分
    lyric = dic['lyric']
    # 通过观察文本内容发现，文本每行以 '\n'字符结束，用文本的split切割\n字符获取每行的歌词内容
    for line in lyric.split('\n'):
        print(line)


def req_songlist():
    headers = {
        'Host': 'music.163.com',
        'Referer': 'https://music.163.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    }

    url = "https://music.163.com/playlist?id=98332770"

    response = requests.get(url=url, headers=headers)
    html = response.content.decode(encoding="utf-8")
    # print(html)
    soup = BeautifulSoup(html, 'lxml')
    results = soup.find('ul', {'class': 'f-hide'})
    results = results.find_all('a')
    print(results)
    for music in results:
        print(music.text, music['href'])


def download():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
    }

    url = "https://music.163.com/playlist?id=98332770"

    response = requests.get(url=url, headers=headers)
    html = response.content.decode(encoding="utf-8")
    # print(html)
    soup = BeautifulSoup(html, 'lxml')
    results = soup.find('ul', {'class': 'f-hide'})
    results = results.find_all('a')
    print(results)
    for music in results:
        # print(music.text, music['href'])
        # 下载歌曲
        music_url = "http://music.163.com/song/media/outer/url?id={}.mp3".format(music['href'].split("=")[1])
        print(music_url)
        urllib.request.urlretrieve(music_url, music.text + '.mp3')


if __name__ == '__main__':
    print('hello lrc transform')
    # url中的信息就是歌词链接，可以试试你自己的链接，更改ID即可
    url = 'http://music.163.com/api/song/media?id=2648874043'
    # text里就是网页的内容了
    text = requests_html(url)
    # 把text里的内容交给parser_html函数解析
    parser_html(text)

    # req_songlist()


