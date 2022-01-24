from collections import namedtuple


def namedtuple_fetchall(cursor):
    """
    [Result(id=54360982, parent_id=None), Result(id=54360880, parent_id=None)]
    """
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def dict_fetchall(cursor):
    """
    [{'parent_id': None, 'id': 54360982}, {'parent_id': None, 'id': 54360880}]
    """
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]