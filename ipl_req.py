import requests
from bs4 import BeautifulSoup
import urllib.request
import time
from utils import *
import traceback as tb
from selenium import webdriver


def req_wyy(url,retry_times=3,delay=2,header=None,verbose_info=None,decode='utf-8', succ_delay=0.5,**kwargs):
    if not header:
        header = {}
    header['Host'] = 'music.163.com'
    header['Referer'] = 'https://music.163.com/'
    header['User-Agent'] = r'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'
    header['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'
    header['Cookie'] = '9d89ce1eae3d3e2b19be57c8952325a0=2c2031bf-1ea9-4e13-95b2-92484a027d34.7Gy7ZchFj-UO2zUyp9t7c02AHJY; order=id%20desc; serverType=nginx; pro_end=-1; ltd_end=-1; memSize=1998; bt_user_info=%7B%22status%22%3Atrue%2C%22msg%22%3A%22%u83B7%u53D6%u6210%u529F%21%22%2C%22data%22%3A%7B%22username%22%3A%22150****2797%22%7D%7D; SetName=; ChangePath=10; sites_path=/www/wwwroot; site_model=php; rank=list; Path=/www/wwwroot; file_recycle_status=true; record_paste_type=1; 2960fc2d6b4dcc284ebdc9f9c7152a8e=fe986542-e123-4711-8f28-b9831ed1368f.m8tBDL5hClgqdn1saSugCHrIR28; request_token=7WZXvunZ1PPL1g32EV0FmSgjvpxwmcm1ILzewTIFJGQN9h0m; backup_path=/www/backup; config-tab=0; network-unitType=KB/s; disk-unitType=KB/s; loginState=false; NMTID=00OSmkDYf3dRDa4iEuilZaxB7ffow0AAAGCixxa6Q'
    cur_times = 0
    while cur_times <= retry_times:
        try:
            resp = requests.get(url,headers=header)
            if hasattr(resp,'status_code') and resp.status_code == 200 and hasattr(resp,'content'):
                time.sleep(succ_delay)
                return resp.content if decode is None else resp.content.decode(decode)
            else:
                print(f'[Req Exception] request failed with info:{verbose_info}')
        except:
            tb.print_exc()
            if verbose_info is not None:
                print(f'[Req Exception] request throw exceptions with info:{verbose_info}')
        cur_times += 1
        time.sleep(delay)
    print(f'[Req Exception] request meets upperbound of retries with info:{verbose_info}')
    return None


def req_song_list(song_list_id='13234602350', succ_delay=0.5,**kwargs):
    if 'cache_url' in kwargs and kwargs['cache_url']:
        with open(kwargs['cache_url'],'r',encoding='utf-8') as f:
            resp = '\n'.join(f.readlines())
    else:
        resp = req_wyy(url=f'https://music.163.com/playlist?id={song_list_id}',verbose_info=f'songlist id={song_list_id}', succ_delay=succ_delay,**kwargs)
    song_list = []
    if not resp:
        print(f'[Req Song List] failed to request song list, plz check if ur id({song_list_id}) is correct.')
        return song_list
    song_list_view = BeautifulSoup(resp, 'lxml').find('ul', {'class': 'f-hide'}).find_all('a')
    for song in song_list_view:
        if hasattr(song,'text') and hasattr(song,'href'):
            song_name = str(song.text)
            song_href = str(song['href']).replace('/song?id=','')
            if strs_is_not_blank(song_name,song_href):
                song_list.append((song_name,song_href))
            else:
                print(f'[Req Song List] invalid song name or href, info:{song_name} | {song_href}')
        else:
            print('[Req Song List] invalid view')
    print(f'[Req Song List] return song list id = {song_list_id}, num. of valid songs = {len(song_list)}')
    return song_list


def req_song_lyric(song_id='874284',song_name=None,succ_delay=0.001,**kwargs):
    resp:str = req_wyy(url=f'http://music.163.com/api/song/media?id={song_id}', verbose_info=f'song id={song_id}',succ_delay=succ_delay,**kwargs)
    is_valid = False
    if resp:
        try:
            resp:dict = eval(resp)
            if 'lyric' in resp:
                is_valid = True
        except:
            tb.print_exc()
    if not is_valid:
        print(f'[Req Song Lyric] failed to request song lyric, plz check if ur id({song_id}) is correct.')
        return None
    lrc = resp['lyric']
    if not strs_is_not_blank(lrc):
        print(f'[Req Song Lyric] warning of no lyrics for {song_name}, plz check if ur id({song_id}) is correct.')
    return lrc


def req_song_wav(song_id='874284',song_name=None,save_path=None,retry_times=3,delay=2, succ_delay=0.5,**kwargs):
    save_path = save_path if save_path is not None else data_dir('tmp_wavs',f'{song_id}{"" if song_name is None else "-" + song_name}.mp3')
    verbose_info = f'song {song_name} | id {song_id}'
    cur_times = 0
    while cur_times <= retry_times:
        try:
            urllib.request.get(f'http://music.163.com/song/media/outer/url?id={song_id}.mp3', save_path)
            time.sleep(succ_delay)
            print(f'[Req Song Wav] succ on {verbose_info}')
            return
        except:
            if verbose_info is not None:
                tb.print_exc()
                print(f'[Req Song Wav] request throw exceptions with info:{verbose_info}')
        cur_times += 1
        time.sleep(delay)
    print(f'[Req Song Wav] request meets upperbound of retries with info:{verbose_info}')


# def req_song_list_sel(song_list_id = '13234602350', succ_delay=0.5,**kwargs):
#     from selenium import webdriver
#     from selenium.webdriver.edge.service import Service
#     # option = webdriver.ChromeOptions()
#     # option.add_argument('--user-data-dir=/Users/superhin/Library/Application Support/Google/Chrome/')
#     service = Service(executable_path='C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
#     driver = webdriver.Edge(service=service)
#     driver.get(f'https://music.163.com/playlist?id={song_list_id}')
#     # driver.quit()


if __name__ == '__main__':
    print('hello req')
    # print(req_song_lyric())
    # req_song_wav()
    print(req_song_list(song_list_id='13234602350'))
    # print(req_song_list_sel(song_list_id='13234602350'))

