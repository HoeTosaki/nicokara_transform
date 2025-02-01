import os

import tqdm

from utils import *
# import eyed3
import traceback as tb
from ipl_req import req_song_lyric
import re

class WavFinder:
    def __init__(self):
        self.reg_dirs = set()
        self.song_map = dict()
        self.__class_name__ = 'WavFinder'

    def print(self,*args,**kwargs):
        print(f'[{self.__class_name__}]',*args,**kwargs)

    def register_wav_dirs(self,*in_dirs):
        [self._register_wav_dir(in_dir=in_dir) for in_dir in in_dirs if strs_is_not_blank(in_dir)]

    def _register_wav_dir(self,in_dir):
        if in_dir in self.reg_dirs:
            self.print(f'dup dir provided as {in_dir}')
            return
        upd_song_num = 0
        upd_dup_song_num = 0
        for root, dirs, files in os.walk(in_dir):
            for file in files:
                cur_path = os.path.join(root,file).lower()
                if strs_is_not_blank(cur_path) and (cur_path.endswith('.mp3') or cur_path.endswith('.m4a') or cur_path.endswith('.wav') or cur_path.endswith('.flac')):
                    try:
                        ret = self.parse_wav_tag(wav_path=cur_path)
                        if ret is not None:
                            wav_title,wav_artist = ret
                            if wav_title in self.song_map and wav_artist not in [e1 for (e1, e2) in self.song_map[wav_title]]:
                                self.song_map[wav_title].append((wav_artist, cur_path))
                                self.print(
                                    f'warning for one name hit multiple song files, as song name:{wav_title} | song artist: {[e1 for e1, e2 in self.song_map[wav_title]]} | song path:{[e2 for e1, e2 in self.song_map[wav_title]]}')
                                upd_dup_song_num += 1
                            else:
                                self.song_map[wav_title] = [(wav_artist, cur_path)]
                            upd_song_num += 1
                    except:
                        tb.print_exc()
                        self.print(f'Exception on parsing song path {cur_path}')
        self.print(f'update song num {upd_song_num} | update duplicate song num {upd_dup_song_num} | total unique song num {len(self.song_map.keys())} | total song num {sum([len(lst) for lst in self.song_map.values()])}')

    def search_song_by_name(self,song_name):
        return self.song_map[song_name] if song_name in self.song_map else None

    def parse_wav_tag(self,wav_path,use_engine='mutagen'):
        if use_engine == 'mutagen':
            from mutagen.mp3 import MP3
            from mutagen.mp4 import MP4
            from mutagen.easyid3 import EasyID3
            from mutagen.flac import FLAC
            if wav_path.endswith('.mp3'):
                cur_wav = MP3(wav_path,ID3=EasyID3)
                if 'title' in cur_wav and 'artist' in cur_wav and len(cur_wav['title']) > 0 and len(cur_wav['artist']) > 0:
                    return cur_wav['title'][0], cur_wav['artist'][0]
            elif wav_path.endswith('.m4a'):
                cur_wav = MP4(wav_path)
                if '©nam' in cur_wav.tags and '©ART' in cur_wav.tags and len(cur_wav.tags['©nam']) > 0 and len(cur_wav.tags['©ART']) > 0:
                    return cur_wav.tags['©nam'][0], cur_wav.tags['©ART'][0]
            elif wav_path.endswith('.flac'):
                cur_wav = FLAC(wav_path)
                return cur_wav['title'][0], cur_wav['artist'][0]
        elif use_engine == 'eyed3':
            if wav_path.endswith('.mp3'):
                import eyed3.load
                cur_wav = eyed3.load(wav_path)
                if cur_wav is not None and cur_wav.tag is not None:
                    return cur_wav.tag.title, cur_wav.tag.artist
        else:
            raise NotImplementedError
        self.print(f'unrecognized audio file at {wav_path}.')
        return None

class LrcFinder:
    def __init__(self,lrc_path):
        self.song_map = dict()
        self.__class_name__ = 'LrcFinder'
        self.lrc_path = lrc_path
        os.makedirs(self.lrc_path,exist_ok=True)

    def print(self, *args, **kwargs):
        print(f'[{self.__class_name__}]', *args, **kwargs)

    def register_song_ids(self,*song_name_ids,force=False,verbose=True):
        failed_song_num = 0
        dup_song_num = 0
        for song_id, song_name in tqdm.tqdm(song_name_ids):
            if strs_is_not_blank(song_id, song_name):
                ret_status = self._register_song_id(song_id=song_id,song_name=song_name,force=force)
                if ret_status == -1:
                    failed_song_num += 1
                elif ret_status == 0:
                    dup_song_num += 1
            if verbose:
                self.print(f'total song num {len(self.song_map.keys())} | failed song num {failed_song_num} | duplicate song num {dup_song_num}')

    def _register_song_id(self,song_id,song_name,force):
        if song_id in self.song_map:
            self.print(f'dup song provided as name={song_name} | id={song_id}')
            return 0
        lrc_path = os.path.join(self.lrc_path, f'{song_id}.lrc')
        if not force and os.path.exists(lrc_path):
            self.print(f"song id {song_id} | name {song_name} checked and skip.")
            self.song_map[song_id] = (song_name,lrc_path)
            return 1
        lrc = req_song_lyric(song_id,song_name)
        if lrc:
            try:
                with open(os.path.join(self.lrc_path, f'{song_id}.lrc'),'w',encoding='utf-8') as f:
                    f.write(lrc)
                self.song_map[song_id] = (song_name, lrc_path)
                return 1
            except:
                tb.print_exc()
                self.print(f'failed to write lyrics at {lrc_path}')
        self.print(f"song id {song_id} | name {song_name} failed to request.")
        return -1

    def search_song_by_id(self, song_id):
        return self.song_map[song_id] if song_id in self.song_map else None


class LrcTransform:
    def __init__(self):
        self.__class_name__ = 'LrcTransform'
        self.re_kanji = None
        self.re_kana = None

    def print(self, *args, **kwargs):
        print(f'[{self.__class_name__}]', *args, **kwargs)

    def transform(self,in_lrc_path,out_lrc_path,title=None,artist=None):
        try:
            with open(in_lrc_path,'r',encoding='utf-8') as f1:
                with open(out_lrc_path,'w',encoding='utf-8') as f2:
                    annos = []
                    prev_line = None
                    for line in f1.readlines():
                        line = line.strip()
                        if strs_is_not_blank(line):
                            res = self.split_ts(line)
                            if res is not None:
                                ts,text = res
                                if prev_line is not None:
                                    f2.write(f'{prev_line} {ts}\n')
                                if strs_is_not_blank(text):
                                    cur_annos,pure_text = self.anno_kanji(text)
                                    if cur_annos:
                                        annos.extend([f'{anno},{ts}' for anno in cur_annos])
                                    prev_line = f'{ts} {pure_text}'
                                else:
                                    prev_line = None
                    if prev_line is not None:
                        f2.write(f'{prev_line}')
                    f2.write('\n')
                    [f2.write(f'@Ruby{idx+1}={anno}\n') for idx,anno in enumerate(annos)]
                    if title:
                        f2.write(f'@Title={title}\n')
                    if artist:
                        f2.write(f'@Artist={artist}\n')
        except:
            tb.print_exc()
            self.print(f'exception in transform lyric from {in_lrc_path} to {out_lrc_path}')

    def split_ts(self,line:str):
        match = re.search(r'\[([^\]]+)\]', line)
        if not match:
            return None
        ts,text = match.group(0),line[match.end():]
        text:str = text.strip()
        ts:str = ts.strip().replace('[','').replace(']','')
        split_ts = ts.split(':')
        if any([ch.isalpha() for ch in ts]):
            return None
        if len(split_ts) >= 3:
            try:
                sep_ts = [str(int(float(ele))).zfill(2)[:2] for ele in split_ts[:3]]
            except:
                tb.print_exc()
                self.print(f'failed to parse timestamp = {ts} | text = {text}')
                return None

        else:
            try:
                sep_ts = [int(float(split_ts[0])), None, None]
                sec_split_ts = ':'.join(split_ts[1:]).replace(':','.').split('.')
                if len(sec_split_ts) == 1:
                    sep_ts[1] = int(float(sec_split_ts[0]))
                    sep_ts[2] = 0
                else:
                    sep_ts[1] = int(float(sec_split_ts[0]))
                    sep_ts[2] = int(float(sec_split_ts[1]))
                sep_ts = [str(ele).zfill(2)[:2] for ele in sep_ts]
            except:
                tb.print_exc()
                self.print(f'failed to parse timestamp = {ts} | text = {text}')
                return None
        sep_ts = f"[{':'.join(sep_ts)}]"
        return sep_ts, text

    def anno_kanji(self,_text:str):
        text = _text.replace('（','(').replace('）',')')

        def process_text(s):
            matches = []
            pattern = re.compile(r'(.{0,5})(\([^)]*\))')

            def repl(match):
                prefix = match.group(1)
                bracket_part = match.group(2)
                matches.append(prefix + bracket_part)
                return prefix.strip()
            processed_s = pattern.sub(repl, s)
            return matches, processed_s
        matches, pure_text = process_text(text)
        self.re_kanji = re.compile(r'[\u4e00-\u9fa5]') if self.re_kanji is None else self.re_kanji
        self.re_kana = re.compile(r'[\u3040-\u309F\u30A0-\u30FF]') if self.re_kana is None else self.re_kana
        annos = []
        is_anno = True
        for mat in matches:
            spl_mat = mat.split('(',1)
            if len(spl_mat) < 2:
                continue
            kanji:str = spl_mat[0].strip()
            kana:str = spl_mat[1].replace('(','').replace(')','').strip()
            for ekana in kana:
                if not self.re_kana.search(ekana) and not self.re_kanji.search(ekana):
                    is_anno = False
                    break
            if not is_anno:
                break
            idx_lst = [idx for idx, ch in enumerate(kanji) if self.re_kanji.match(ch) or ch in ('々',)]
            if not idx_lst:
                is_anno = False
                break
            kanji = kanji[min(idx_lst):]
            if strs_is_not_blank(kanji,kana):
                annos.append(','.join([kanji,kana]))
        if not is_anno:
            self.print(f'text={text}, bracket here might not indicate or possess annotation of kanji, plz check.')
            return [],_text
        return annos, pure_text.strip()


if __name__ == '__main__':
    print('hello match')
    # wf = WavFinder()
    # wf.register_wav_dirs('./data/imp_wavs')
    # print(wf.song_map)
    # lf = LrcFinder(lrc_path=data_dir('req_lrc'))
    # lf.register_song_ids(('874284','想月'),force=True)
    # print(lf.song_map)

    lt = LrcTransform()
    print(lt.split_ts('[03:82.15] why1'))
    print(lt.split_ts('[03:82:15] why1'))
    print(lt.split_ts('[033:82.145] why1'))
    print(lt.split_ts('[3:2.153123:321:dwad] why1'))
    print(lt.anno_kanji('一人(ひとり)で泣(な)き続(つづ)けてるだけ'))