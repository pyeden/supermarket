import json
import os
import time
from pathlib import Path
from django.db.transaction import get_connection
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'supermarket.settings')


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
        keys = '("'+'","'.join(columns)+'")'
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
                    elif 0 < index < len(row)-1:
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


if __name__ == '__main__':
    insert_data()