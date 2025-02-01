import os


def data_dir(*dir_names,dir_path='./data',force_create=True):
    mk_dir = dir_path
    if dir_names is None:
        cur_path = dir_path
    else:
        tot_dir_name = [dir_path] + list(dir_names)
        cur_path = os.path.join(*tot_dir_name)
        mk_dir = os.path.join(*tot_dir_name[:-1])
    if force_create:
        os.makedirs(mk_dir, exist_ok=True)
    return cur_path


def str_is_not_blank(s:str):
    s = str(s)
    return s is not None and s != '' and s.strip() != '' and s.strip().lower() not in ('nan','none','nil')


def strs_is_not_blank(*ss):
    return all([str_is_not_blank(s) for s in ss])


def safe_file_name(filename:str):
    for ch in ('<','>',':','"','/','\\','|','*','?','\n'):
        filename = filename.replace(ch,'')
    return filename

if __name__ == '__main__':
    print('hello util')