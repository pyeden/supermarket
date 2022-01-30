import json
import os
import random
import time

import requests
from concurrent import futures
from pathlib import Path
from django.db.transaction import get_connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supermarket.settings')

base_url = 'https://pages.tmall.com/wow/chaoshi/act/category?wh_logica=HD&wh_callback=__chaoshi_category'

headers = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'if-none-match': 'W/2dbb-GWGx5v69aN/r7zDNgThaz/TvrEY',
    'referer': 'https://chaoshi.tmall.com/',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': "macOS",
    'sec-fetch-dest': 'script',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
}


def insert_data():
    p = Path('data')
    for file in p.rglob('*.json'):
        table = f'app_{file.stem}'
        columns = []
        rows = []
        c_list = ['dateAdd', 'dateUpdate', 'dateDelete', 'is_delete']
        l_list = ['1642166520', '1642166520', '1642166520', 0]
        with file.open() as f:
            try:
                data = json.load(f)
                data = data['data']
                if 'dataList' in data:
                    data = data['dataList']
                for item in data:
                    row = []
                    for k, v in item.items():
                        if k not in columns:
                            columns.append(k)
                        row.append(v)
                    row.extend(l_list)
                    rows.append(row)
            except Exception as e:
                continue
        columns.extend(c_list)
        news = [row for row in rows if len(row) == len(columns)]
        keys = '("' + '","'.join(columns) + '")'
        conn = get_connection()
        with conn.cursor() as c:
            for row in news:
                # (0, "",, 0, "https://dcdn.it120.cc/2019/12/29/8396f65d-d615-46d8-b2e5-aa41820b9fe5.png", 0, "显示", "首页轮播图", "index", 951, "1642166520", "1642166520", "1642166520", 0)'
                values = '('
                for index, i in enumerate(row):
                    if index == 0:
                        if isinstance(i, str):
                            if i == '':
                                i = f'"",'
                            else:
                                i = f'"{i}",'
                            values += i
                        else:
                            values = f'{values}{i},'
                    elif 0 < index < len(row) - 1:
                        if isinstance(i, str):
                            if i == '':
                                i = f'"",'
                            else:
                                i = f'"{i}",'
                            values += i
                        else:
                            values = f'{values}{i},'
                    else:
                        if isinstance(i, str):
                            if i == '':
                                i = f'"")'
                            else:
                                i = f'"{i}")'
                            values += i
                        else:
                            values = f'{values}{i})'

                sql = f"""insert into {table} {keys} values {values} """
                try:
                    c.execute(sql)
                except Exception as e:
                    print(sql)
                    continue


def get_tian_mao_info():
    pass


def get_proxy():
    url = 'http://api.xdaili.cn/xdaili-api//newExclusive/getIp?spiderId=9895c669da7e4e43bf620a684833eb7c&orderno=DX20221302189CANoh1&returnType=2&count=1&machineArea=200000'
    ips = []
    while 1:
        res = load_url(url)
        code = res.get("ERRORCODE")
        if code in ("0", 0):
            ips = res.get("RESULT")
            break
        else:
            print(f'提取代理失败： {res}')
            time.sleep(16)
            continue
    ip_port = random.choice([f'{ip["ip"]}:{ip["port"]}' for ip in ips])
    return {'https': f'{ip_port}'}


def load_url(url, proxy=None, method='get', headers=None, timeout=600):
    while 1:
        try:
            res = requests.request(
                method,
                url,
                timeout=timeout,
                headers=headers,
                proxies=proxy)
            if res.status_code != 200:
                print(f'请求失败: {res.status_code}---{res.content}')
                continue
            break
        except Exception as e:
            print(f'请求失败: {e}')
            return {}
    try:
        data = res.json()
    except Exception as e:
        print(e)
        data = json.loads(res.text.split()[0][len('__chaoshi_category')+1: -1])
    return data


def get_urls(proxy):
    json_data = load_url(base_url, proxy)
    data_1 = {data['name']: data['recommends'] for data in json_data['data']}
    data = {}
    for k, v in data_1.items():
        d = {}
        for i in v:
            d.update({i['name']: f"https:{i['link']}"})
        data[k] = d
        print(k)
    return data


def main():
    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        proxy = get_proxy()
        urls = get_urls(proxy)
        test = load_url(list(list(urls.values())[0].values())[0], proxy, 'get', headers, 60)
        future_to_url = {executor.submit(load_url, proxy, 'get', headers, 60): name for name, url in urls.values()}
        for future in futures.as_completed(future_to_url):
            name = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (name, exc))
            else:
                print('%r page is %d bytes' % (name, len(data)))


if __name__ == '__main__':
    # insert_data()
    main()
