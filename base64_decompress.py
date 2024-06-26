#!/usr/bin/env python3

import os
import re
import bz2
import gzip
import shutil
import base64
import tarfile
import argparse as ap
from subprocess import check_output

# reverts from base64 encoding
def undo_base64(file):
    with open(file, 'rb') as in_file:
        with open('data', 'wb') as out_file:
            base64.decode(in_file, out_file)
    os.rename('data', file)

# untars a tar archive
def untar(file):
    with tarfile.open(file, 'r') as in_file:
        with open('data', 'wb') as out_file:
            shutil.copyfileobj(in_file.extractfile(in_file.getmembers().pop(0)), out_file)
    os.rename('data', file)

# decompresses with gzip algorithm
def gzip_decompress(file):
    with gzip.open(file, 'rb') as in_file:
        with open('data', 'wb') as out_file:
            shutil.copyfileobj(in_file, out_file)
    os.rename('data', file)

# decompresses with bzip2 algorithm
def bz2_decompress(file):
    with bz2.open(file) as in_file:
        with open('data', 'wb') as out_file:
            shutil.copyfileobj(in_file, out_file)
    os.rename('data', file)

# reverses a hexdump
def hexdump_reverse(file):
    output = check_output(['xxd', '-r', file])
    with open(file, 'wb') as f:
        f.write(output)
        
# reads the contents of the contained text file
def read_contents(file, first_line):
    print(first_line.encode('utf-8'))

# checks what type of file the input is and continues accordingly
def check_file_type(file, keyword):
    done = False
    i = 0
    while not done:
        if(i > 8):
            done = True
        else:
            i = i + 1
        try:
            file_output_decode = check_output(['file', file])
            file_output = file_output_decode.decode('utf-8')
            print(file_output)
        except Exception as e:
            print('Something went wrong! ' + e)
        if 'gzip' in file_output:
            gzip_decompress(file)
        elif 'tar' in file_output:
            untar(file)
        elif 'bzip2' in file_output or 'bz2' in file_output:
            bz2_decompress(file)
        elif 'text' in file_output:
            with open(file) as f:
                fl = f.readline()
                if "00000000" in fl:
                    hexdump_reverse(file)
                elif keyword in fl:
                    print("keyword found.")
                    read_contents(file, fl)
                    done = True
                elif re.search('([A-Za-z0-9+/=])+', fl) and not re.search('([, | .])+', fl):
                    print('found base64 file!')
                    undo_base64(file)
                else:
                    print("Nothing matches.")
                    done = True
# function to test if file exists
def check_file_exists(file):
    if file is None  or not os.path.isfile(file):
        return False
    else:
        return True

# function for argparse stuff
def create_parser():
    p = ap.ArgumentParser()
    # adding flags
    p.add_argument('-f', action='store', dest='file', type=str,
                    help="Absolute path to the file to be processed.")
    p.add_argument('-k', action='store', dest='keyword', type=str, help='keyword to look for in ASCII text file.')
    return p.parse_args()

def main():
    args = create_parser()
    check_file_exists(args.file)
    check_file_type(args.file, args.keyword)

if __name__== '__main__':
    main()