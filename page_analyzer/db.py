import psycopg2
import os


def connect(url):
    return psycopg2.connect(url)


def close(conn):
    return conn.close()



