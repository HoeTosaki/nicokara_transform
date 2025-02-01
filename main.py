import argparse
from ipl_serv import SongListManager


def all_in_one_routine(song_list_id,reg_wav_dirs,out_lrc_dir,force,allow_no_wav):
    print('start all in one routine.')
    slm = SongListManager(song_list_id=song_list_id)
    slm.register_wav_dirs(*reg_wav_dirs)
    slm.refresh_meta(cache_url=None)
    slm.transform_lrcs(out_dir_name=out_lrc_dir,force=force,allow_no_wav=allow_no_wav)
    print('all in one routine normally finished.')


if __name__ == '__main__':
    # print('hello lrc transform')
    parser = argparse.ArgumentParser(description='Netease2NicoKara Lyric Transform Side Tool')
    parser.add_argument('-u','--use_all_in_one', action='store_true', help='is in all in one routine.')
    parser.add_argument('-s', '--song_list_id', required=True, type=str, help='is in all in one routine.')
    parser.add_argument('-d','--reg_wav_dirs', required=False, type=str, help='registered dir for wav files, path split by ":" ')
    parser.add_argument('-o', '--out_lrc_dirs', required=True, type=str,help='output dir for lyrics adpated to nicokara.')
    parser.add_argument('-f', '--force', action='store_true', help='force to ignore cache files left by previous execution.')
    parser.add_argument('-a', '--allow_no_wav', action='store_true', help='when wav file not matched, if the lyric record should be ignored.')

    args = parser.parse_args()
    if args.use_all_in_one:
        all_in_one_routine(args.song_list_id,args.reg_wav_dirs.split(':') if args.reg_wav_dirs is not None else None,
                           args.out_lrc_dirs,args.force,args.allow_no_wav)
    else:
        print('currently not supported operation.')



