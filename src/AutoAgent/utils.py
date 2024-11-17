# -*- coding: utf-8 -*-

import codecs
import time

def read_file(file_path):
    lines = []
    with codecs.open(file_path, "r", "utf-8") as file:
        lines = file.readlines()
    return lines

def save_file(file_path, lines):
    with codecs.open(file_path, "w", "utf-8") as file:
        for line in lines:
        	file.write(line + "\n")
    file.close()

def get_current_timestamp():
    timestamp = int(time.time())
    return timestamp

def get_current_datetime():
    import datetime    
    now = datetime.datetime.now()
    datetime = now.strftime('%Y-%m-%d %H:%M:%S')
    return datetime
