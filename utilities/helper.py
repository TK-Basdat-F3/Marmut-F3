from django.db import connection
from collections import namedtuple

def map_cursor(cursor):
    description = cursor.description
    query_result = namedtuple("Data", [col[0] for col in description])
    return [query_result(*row) for row in cursor.fetchall()]

def query(query_str: str):
    result = []
    with connection.cursor() as cursor:
        try:
            cursor.execute(query_str)
            if query_str.strip().lower().startswith("select"):
                result = map_cursor(cursor)
            else:
                result = cursor.rowcount
        except Exception as e:
            result = e
    return result

def get_user_type(email):
    if query(f'SELECT * FROM "MARMUT"."artist" WHERE email_akun = \'{email}\''):
        return 'artist'
    elif query(f'SELECT * FROM "MARMUT"."songwriter" WHERE email_akun = \'{email}\''):
        return 'songwriter'
    elif query(f'SELECT * FROM "MARMUT"."podcaster" WHERE email = \'{email}\''):
        return 'podcaster'
    elif query(f'SELECT * FROM "MARMUT"."label" WHERE email = \'{email}\''):
        return 'label'
    else:
        return 'pengguna_biasa'
