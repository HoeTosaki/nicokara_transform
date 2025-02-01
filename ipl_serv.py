import os.path
import pandas as pd
from utils import *
from ipl_req import req_song_list
from ipl_match import WavFinder, LrcFinder,LrcTransform
import tqdm
import shutil as sh
import traceback as tb
import warnings

warnings.filterwarnings('ignore', category=pd.core.common.SettingWithCopyWarning)


class SongListManager:
    def __init__(self, song_list_id = '', meta_name='meta_info',csv_encoding='ANSI'):
        self.song_list_id = song_list_id
        self.__class_name__ = 'SongListManager'
        self.wf = WavFinder()
        self.lf = LrcFinder(lrc_path=data_dir('req_lrc'))
        self.lt = LrcTransform()
        self.df = None
        self.meta_name = meta_name
        self.csv_encoding = csv_encoding

    def print(self, *args, **kwargs):
        print(f'[{self.__class_name__}]', *args, **kwargs)

    def register_wav_dirs(self,*wav_dir):
        self.wf.register_wav_dirs(*wav_dir)

    def refresh_meta(self,cache_url=None):
        meta_path = data_dir(f'{self.meta_name}_{self.song_list_id}.csv')

        # load song list including song names and ids.
        song_list = req_song_list(song_list_id=self.song_list_id,cache_url=cache_url) # [(song_name,song_id)]

        # create or reuse
        use_cols = ['song_name', 'song_id', 'artist', 'is_chunK', 'wav_path', 'lrc_path', 'out_path']
        if True or not os.path.exists(meta_path):
            df:pd.DataFrame = pd.DataFrame(data=None,columns=use_cols,dtype=str)
        else:
            df:pd.DataFrame = pd.read_csv(meta_path)
            if any([col not in df.columns for col in use_cols]):
                assert False, self.print(f'invalid meta info at {meta_path}, plz remove it to repair and restart.')

        # req, re-check and fill df song meta.
        exist_song_ids = set([str(song_id) for song_id in df['song_id'].to_list()])
        add_song_num = 0
        for song_name,song_id in song_list:
            if song_id not in exist_song_ids:
                ser = pd.Series({'song_id': song_id,'song_name':song_name}).reindex(df.columns)
                df = pd.concat([df,ser.to_frame().T],ignore_index=True)
                add_song_num += 1
        if add_song_num > 0:
            self.print(f'detected adding new song num={add_song_num}')

        self.print('start to check all songs in meta...')
        for idx in tqdm.tqdm(range(df.shape[0])):
            df_row = df.iloc[idx,:].copy()
            if strs_is_not_blank(df_row['is_chunK']):
                continue
            df.iloc[idx,:] = self.check_song(df_row,update_song=False)

        self.print(f'check all songs in meta ended, df shape = {df.shape}')
        self.df = df
        self.df.to_csv(meta_path,index=False)

    def transform_lrcs(self,out_dir_name='out_lrc',allow_no_wav=False,force=False):
        meta_path = data_dir(f'{self.meta_name}_{self.song_list_id}.csv')
        if self.df is None:
            self.print('meta data not ready, plz exec refresh_meta first.')
            return
        out_dir = data_dir(out_dir_name)
        os.makedirs(out_dir,exist_ok=True)
        self.print('start to tranform and check all songs...')
        batch_song_ids = zip(list(self.df['song_id'].astype(str)),list(self.df['song_name'].astype(str)))
        for idx in tqdm.tqdm(range(self.df.shape[0])):
            df_row = self.df.iloc[idx,:]
            if strs_is_not_blank(df_row['is_chunK']):
                continue
            self.df.iloc[idx,:] = self.check_song(df_row,update_song=True,force=force,batch_song_ids=batch_song_ids,out_dir=out_dir,allow_no_wav=allow_no_wav)
        self.df.to_csv(meta_path, index=False)
        self.print('tranform ended')

    def check_song(self,df_row,update_song=False,force=False,**kwargs):
        has_out = False
        has_wav = False
        has_lrc = False
        song_id = str(df_row['song_id'])
        song_name = str(df_row['song_name'])
        wav_path = str(df_row['wav_path'])
        lrc_path = str(df_row['lrc_path'])
        out_path = str(df_row['out_path'])
        artist = str(df_row['artist'])

        if strs_is_not_blank(wav_path) and os.path.exists(wav_path):
            has_wav = True
            if not update_song and not has_wav:
                self.print(f'lost wav file at song id {song_id} | name {song_name}')

        if strs_is_not_blank(lrc_path) and os.path.exists(lrc_path):
            has_lrc = True
            if not update_song and not has_lrc:
                self.print(f'lost lrc file at song id {song_id} | name {song_name}')

        if strs_is_not_blank(out_path) and os.path.exists(out_path):
            out_files = os.listdir(out_path)
            if f'trans_{song_id}.lrc' in out_files:
                has_out = True
            if not update_song and not has_lrc:
                self.print(f'lost out file at song id {song_id} | name {song_name}')

        if not has_wav:
            df_row['wav_path'] = None
        if not has_lrc:
            df_row['lrc_path'] = None
        if not has_out:
            df_row['out_path'] = None

        if update_song:
            self.lf.register_song_ids(*kwargs['batch_song_ids'], force=force, verbose=False)
            ret = self.lf.search_song_by_id(song_id)
            if force or not has_lrc:
                if ret is None:
                    self.print(f'update song id {song_id} name {song_name} failed at finding lrc.')
                    return df_row
                _song_name,lrc_path = ret
                lrc_path = os.path.abspath(lrc_path)
                assert song_name == _song_name, self.print(f'fatal error song id ({song_id}) not corresponded with name ({song_name}) ')
                has_lrc = True
            if force or not has_wav:
                ret = self.wf.search_song_by_name(song_name)
                if ret is None:
                    self.print(f'update song id {song_id} name {song_name} failed at finding wav.')
                    if not kwargs['allow_no_wav']:
                        return df_row
                else:
                    wav_path = '@@'.join([f'{wav_art}$${os.path.abspath(_wav_path)}' for wav_art,_wav_path in ret])
                    artist = ','.join([f'{wav_art}' for wav_art,_wav_path in ret])
                    if len(ret) > 1:
                        self.print(f'warning for id with dup song names, as: {wav_path}')
                    has_wav = True

            if force or not has_out:
                _out_path:str = os.path.join(kwargs['out_dir'],f'{safe_file_name(song_name)}')
                os.makedirs(_out_path,exist_ok=True)
                try:
                    if has_wav:
                        wav_paths = [ele.split('$$', 1)[-1] for ele in wav_path.split('@@')]
                        for p in wav_paths:
                            sh.copy(p, _out_path)
                except:
                    tb.print_exc()
                    self.print(f'failed to move wav (path={wav_path}) to output dir')
                try:
                    self.lt.transform(lrc_path,os.path.join(_out_path,f'trans_{song_id}.lrc'),title=song_name if strs_is_not_blank(song_name) else None, artist=artist if strs_is_not_blank(artist) else None)
                    out_path = os.path.abspath(_out_path)
                except:
                    tb.print_exc()
                    self.print(f'update song id {song_id} name {song_name} failed at transforming lrc to path {_out_path}.')
                    return df_row
            df_row['wav_path'] = wav_path
            df_row['lrc_path'] = lrc_path
            df_row['out_path'] = out_path
            df_row['artist'] = artist
        return df_row


if __name__ == '__main__':
    print('hello serv')
    slm = SongListManager(song_list_id='13234602350',csv_encoding='mbcs')
    slm.register_wav_dirs(data_dir('./imp_wavs'))
    slm.register_wav_dirs(r'C:\CloudMusic')
    slm.register_wav_dirs(r'D:\music')
    slm.refresh_meta(cache_url='./data/cache.html')
    slm.transform_lrcs(out_dir_name='out_lrc',force=True,allow_no_wav=True)

