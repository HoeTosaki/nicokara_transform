# nicokara_transform

a sidetool-like routine for automatically transforming NetEase song list into NICO karaoke ver.

## Environment Prepare

1. For Python Running Env., make sure your Python version >= 3.7, and

```
pip install pandas beautifulsoup4 tqdm mutagen
```

2. NicokaraMaker 2, which can be downloaded from Microsoft Appstore at `https://apps.microsoft.com/detail/9p0j9zvx9m4m?hl=ja-jp&gl=JP` 

## Quick Start

here provide a brief procedure with all-in-one CLI as quick start to show its abilities.

### i. Create a song list on NetEase and find its List ID

A demo list with 3 test songs provided at `https://music.163.com/#/playlist?id=13248076598`, where `13248076598` is its list ID `song_list_id`.

**[Custom]** If a customized list is referred, make sure that it has been set as public, as a curl to get song ids within given list is required.

### ii. [Optional] Prepare your song library

Directly downloading song wav data from Netease is currently blocked by anti-spider mechanism.

It is suggested to cache your song list from Netease Client App (by download all button), and find the cache dir path `reg_wav_path` for the next step.

### iii. Parse songs into Nicokara format

execute:

```
cd nicokara_transform/
python3 main.py -u -s 13248076598 -d ./data/sample_wavs -o out_lrc -f -a
```

A csv-table will be find at `/data/` containing meta info of each song like:

| song_name | song_id   | artist       | is_chunK | wav_path                                                     | lrc_path                                                     | out_path                                                    |
| --------- | --------- | ------------ | -------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ----------------------------------------------------------- |
| 想月      | 874284    | めらみぽっぷ |          | めらみぽっぷ$$D:\ニコカラ\git_repo\nicokara_transform\data\sample_wavs\めらみぽっぷ - 想月.mp3 | D:\ニコカラ\git_repo\nicokara_transform\data\req_lrc\874284.lrc | D:\ニコカラ\git_repo\nicokara_transform\data\out_lrc\想月   |
| 砕月      | 41416656  | peЯoco.      |          | peЯoco.$$D:\ニコカラ\git_repo\nicokara_transform\data\sample_wavs\peяoco. - 砕月.mp3 | D:\ニコカラ\git_repo\nicokara_transform\data\req_lrc\41416656.lrc | D:\ニコカラ\git_repo\nicokara_transform\data\out_lrc\砕月   |
| 熱帯夜    | 425280726 | peЯoco.      |          | peЯoco.$$D:\ニコカラ\git_repo\nicokara_transform\data\sample_wavs\peяoco. - 熱帯夜.mp3 | D:\ニコカラ\git_repo\nicokara_transform\data\req_lrc\425280726.lrc | D:\ニコカラ\git_repo\nicokara_transform\data\out_lrc\熱帯夜 |

where `out_path` indicates the input files to NicokaraMaker, and `wav_path` & `lrc_path` are searched wav source file and request lyrics, resp.

**[Custom]** Plz add your library path to -d <path1>:<path2>:...  or eq. add songs into `./data/sample_wavs` , and change song list id `13248076598` to your own. The parameters in the above CMD:

```
-u: use all-in-one routine.
-s: song list id.
-d: song library paths concat by ':'
-o: lyrics output path saved for NicokaraMaker.
-f: force to ignore cache files left by previous execution.
-a: when wav file not matched, if the lyric record should be ignored.
```

### iv. Export Videos by NicokaraMaker

Open NicokaraMaker, and take an example as `song_name=想月`, 

folder at `D:\ニコカラ\git_repo\nicokara_transform\data\req_lrc\874284.lrc  D:\ニコカラ\git_repo\nicokara_transform\data\out_lrc\想月` contains two types of files:

```
*.<mp3/flac/m4a>: turn NicokaraMaker tabs to `素材動画` and fill `音声`　by it.
*.lrc: turn NicokaraMaker tabs to `歌詞編集` and drag it to the tab frame.
```

After import the above two files, plz turn to `動画出力` and export the final video like this:



exported video in `.avi`  format might be huge, post-processing to compress it is encouraged (like using ShanaEncoder).













