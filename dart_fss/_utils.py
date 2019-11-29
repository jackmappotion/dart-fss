# -*- coding: utf-8 -*-
import os
import re
import zipfile
import requests

from typing import List, Union, Dict
from datetime import datetime
from fake_useragent import UserAgent


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def request_get(url: str, params: dict = None, timeout: int = 120, stream: bool = False):
    return requests.get(url=url, params=params, headers=user_agent(), timeout=timeout, stream=stream)


def unzip(file: str, path: str = None, create_folder=True) -> str:
    os.path.altsep = '\\'  # fixed extract bug
    if path:
        extract_path = path
    else:
        extract_path = '\\'.join(file.split('\\')[:-1])

    with zipfile.ZipFile(file, 'r') as zip_ref:
        if create_folder:
            folder = file.split('\\')[-1]
            folder = folder.replace('.zip', '')
            extract_path = os.path.join(extract_path, folder)
        zip_ref.extractall(extract_path)
    return extract_path


def search_file(path: str, filename: str = None, extensions: str = 'xbrl') -> List[str]:
    xbrl_file = []
    for root, _, files in os.walk(path):
        for file in files:
            if filename is not None and re.search(filename, file):
                xbrl_file.append(os.path.join(root, file))
            if file.endswith('.' + extensions):
                xbrl_file.append(os.path.join(root, file))
    return xbrl_file


def dict_to_html(dict_data: dict, exclude=None, header=None) -> str:
    style = r'''
    <style scoped>
        .dart-table tbody tr th {
            vertical-align: top;
            text-overflow: ellipsis;
        }
        .dart-table thead th {
            text-align: right;
            text-overflow: ellipsis;
        }
    </style>
    '''

    table = r'''<table border="1" class="dart-table">'''
    if header is not None:
        table += r'<thead><tr style="text-align: right;">'
        for head in header:
            table += '<th>{}</th>'.format(head)
        table += r'</tr></thead>'
    table += r'<tbody>'

    for key, value in dict_data.items():

        if exclude and key in exclude:
            continue

        if isinstance(value, list):
            table += '<tr><th>{}</th><td>'.format(key)
            if len(value) > 0:
                labels = list(value[0].keys())

                if exclude:
                    labels = [x for x in labels if x not in exclude]

                table += '<table style="width:100%"><thead><tr><th width="20">No.</th>'
                for label in labels:
                    table += '<th>{}</th>'.format(label)
                table += '</tr></thead>'
                table += '<tbody>'
                for idx, v in enumerate(value):
                    table += '<tr><th width="20">{}</th>'.format(idx)
                    for l in labels:
                        table += '<td>{}</td>'.format(v.get(l))
                    table += '</tr>'
                table += '</tbody></table>'
            table += '</td></tr>'
        else:
            table += '<tr><th>{}</th><td>{}<td></tr>'.format(key, value)
    table += '</tbody></table>'

    return style + table


str_or_datetime = Union[str, datetime]


def get_datetime(date: str_or_datetime) -> datetime:
    if isinstance(date, str):
        return datetime.strptime(date, '%Y%m%d')
    elif isinstance(date, datetime):
        return date
    else:
        raise ValueError('Invalid datetime format')


def check_datetime(date: str_or_datetime,
                   start_date: str_or_datetime = None,
                   end_date: str_or_datetime = None) -> bool:
    date = get_datetime(date)
    if start_date is not None:
        start_date = get_datetime(start_date)
        if date < start_date:
            return False
    if end_date is not None:
        end_date = get_datetime(end_date)
        if date > end_date:
            return False
    return True


def compare_str(str1: str, str2: str) -> bool:
    str1 = str1.strip().lower()
    str2 = str2.strip().lower()
    return str1 == str2


CHANGE_AGENT_MINUTE = 10
cached_agent = {
    'datetime': None,
    'agent': None
}


def user_agent() -> Dict[str, str]:
    global cached_agent

    time = cached_agent.get('datetime', None)
    agent = cached_agent.get('agent', None)

    diff_time = int((datetime.now() - time).seconds / 60) if time is not None else 100

    if agent is None or (diff_time > CHANGE_AGENT_MINUTE):
        ua = UserAgent()
        agent = ua.chrome
        cached_agent['agent'] = agent
        cached_agent['datetime'] = datetime.now()

    return {'User-Agent': str(agent)}


def str_unit_to_number_unit(str_unit: str):
    str_unit = re.sub(r'\s+', '', str_unit)
    str_unit_to_unit = {
        '억원': 100000000,
        '천만원': 10000000,
        '백만원': 1000000,
        '십만원': 100000,
        '만원': 10000,
        '천원': 1000,
        '백원': 100,
        '십원': 10,
        '원': 1,
        'USD': 1
    }
    return str_unit_to_unit[str_unit]


def query_to_regex(query):
    if isinstance(query, str):
        regex = re.compile(query, re.IGNORECASE)
    elif isinstance(query, list):
        pattern = '(' + '|'.join(query) + ')'
        regex = re.compile(pattern, re.IGNORECASE)
    else:
        raise TypeError('Invalid query type')
    return regex


def create_folder(path):
    import pathlib
    try:
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        pass


def strWS(word):
    return r'\s*'.join(word)


# Jupyter Notebook Checker
def is_notebook():
    try:
        from IPython import get_ipython
        if 'IPKernelApp' not in get_ipython().config:
            return False
    except Exception:
        return False
    return True

