import subprocess
import re
from glob import glob
from PIL import Image
from more_itertools import chunked

def new_size(img, max_dim=300):
    '''
    Return the new width and heigh of the image to rescale to a max dimension
    of `max_dim`.
    '''
    w,h = img.size
    scale = max_dim / max(w,h)
    if scale >= 1:
        return w,h
    w = round(w*scale)
    h = round(h*scale)
    return w,h

def zip_dirs(dir_list, 
             num_dirs=5, 
             zip7exe='C:/Program Files/7-zip/7z.exe'
             out_prefix='dog-images'):
    '''
    Use 7-zip to zip `num_dirs` of directories at a time from `dir_list`
    '''
    for i, c in enumerate(chunked(dirs, num_dirs), 1):
        proc = subprocess.Popen([zip7exe, 
                'a', 
                f'{out_prefix}-images-{i:0>2}.zip',
                *c, 
                '-mx=9'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)
        out, err = proc.communicate()
        yield out.decode()

if __name__ == '__main__':

    files = glob('**/*.jpg', recursive=True)
    dirs = glob('*')
    
    for i,f in enumerate(files, 1):
        img = Image.open(f)
        img_sm = img.resize(new_size(img, 350), Image.LANCZOS)
        img.close()
        if img_sm.mode == 'RGBA':
            img_sm = img_sm.convert('RGB')
        img_sm.save(f, quality=65)
        print(f'\r Resizing images: {i:,} / {len(files):,}'
              f' ({round(100*i/len(files), 2)}%)', end=' ')
              
    for res in zip_dirs(dirs, 5):
        count = res.count('Compressing')
        archive = re.findall(r'Creating archive (.*)\r\n', res)
        archive = archive[0] if archive else 'MISSING_FILE'
        print(f'{count} files compressed into {archive}')
