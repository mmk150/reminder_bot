import sqlite3
from thoth.Timerz import Timerz
import datetime

conn = sqlite3.connect('timers.db')

c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS timers (
        ping_date text,
        req_date text,
        del_code text,
        user_id text,
        channel text,
        message text,
        badgermode text,
        whole text
        )""")


def insert_timer(timer: Timerz):
    print("Delcode is " + timer.del_code)
    c.execute("""INSERT INTO timers VALUES 
    (:ping_date,:req_date,:del_code,:user_id,:channel,:message,:badgermode,:whole)""",
              {'ping_date': timer.ping_time,
               'req_date': timer.req_time,
               'del_code': timer.del_code,
               'user_id': timer.user_id,
               'channel': timer.channel,
               'message': timer.message,
               'badgermode': timer.badgermode,
               'whole': timer.to_string()
               }
              )
    conn.commit()


def search_timer(hexcode):
    c.execute("SELECT * FROM timers WHERE del_code=:del_code", {'del_code': hexcode})
    return c.fetchall()


def search_next_timers():
    c.execute("""SELECT *
    FROM timers
    ORDER BY ping_date ASC
    LIMIT 10;
    """)
    return c.fetchall()


def remove_timer(hexcode):
    cursor = c.execute("DELETE FROM timers WHERE del_code=:del_code", {'del_code': hexcode})
    print(f"remove_timer affected {cursor.rowcount} rows deleting hexcode={hexcode}")
    conn.commit()

def pop_timer(timer : Timerz):
    cursor = c.execute("DELETE FROM timers WHERE ping_date=:ping_date AND req_date=:req_date AND del_code=:del_code",{'ping_date': timer.ping_time, 'req_date':timer.req_time, "del_code":timer.del_code})
    print(f"pop_timer affected {cursor.rowcount} rows deleting with={timer.ping_time , timer.req_time}")
    conn.commit()
