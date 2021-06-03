
import os 
import sys
import signal
import time
import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    
    except Error as e:
        print(e)

    return conn

def create_table(conn, table):
    try:
        c = conn.cursor()
        c.execute(table)

    except Error as e:
        print(e)

def add_job_order(conn, job_order):
    try:
        sql = ''' INSERT INTO order_history(job_order)
                    VALUE(?)'''
        
        c = conn.cursor()
        c.execute(sql, job_order)
        conn.commit()

        return c.lastrowid

    except Error as e:
        print(e)