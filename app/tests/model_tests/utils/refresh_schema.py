import psycopg2


def drop_and_create():
    """drop the public schema in the test database and then create it again"""
    connection = psycopg2.connect(dbname="survista_test",
                                  user="postgres",
                                  password="password",
                                  host="127.0.0.1",
                                  port=5432)
    cur = connection.cursor()

    cur.execute('DROP SCHEMA IF EXISTS public CASCADE')
    connection.commit()
    cur.execute('CREATE SCHEMA public')
    connection.commit()

    cur.close()
    connection.close()
