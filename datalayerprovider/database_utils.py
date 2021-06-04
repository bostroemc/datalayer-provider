import os 
import sys
import signal
import time
import sqlite3
from sqlite3 import Error


def initialize(db):
    conn = None
    table = """CREATE TABLE IF NOT EXISTS order_history (
                    id integer PRIMARY KEY,
                    job_order text,
                    time_in text,
                    time_out text,
                    status integer  
                );"""

    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()
        c.execute(table)

        return conn
    
    except Error as e:
        print(e)

    return conn

def add_job_order(conn, job_order):
    try:
        s = ''' INSERT INTO order_history(job_order, time_in, status)
                    VALUES(?, ?, ?);'''
        
        time_in =  time.strftime("%H:%M:%S", time.localtime())       
        status = 0    # pending=0, active=1, done=2

        c = conn.cursor()
        c.execute(s, (job_order, time_in, status))
        conn.commit()

        return c.lastrowid

    except Error as e:
        print(e)

# not used
def create_connection(db):
    conn = None
    try:
        conn = sqlite3.connect(db)
        return conn
    
    except Error as e:
        print(e)

    return conn

# not used
def create_table(conn, table):
    try:
        c = conn.cursor()
        c.execute(table)

    except Error as e:
        print(e)        

def count(conn):
    try:
        c = conn.cursor()
        h = c.execute("SELECT * FROM order_history")
        return len(h.fetchall())

    except Error as e:
        print(e)             

def fetch(conn, limit, offset):
    try:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(f'SELECT * FROM order_history LIMIT {limit} OFFSET {offset}')    

        r = [dict((c.description[i][0], value) for i, value in enumerate(row)) for row in c.fetchall()]

        return r

    except Error as e:
        print(e)             