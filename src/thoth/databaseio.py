import sqlite3
import Timerz
import datetime
import os

conn = sqlite3.connect("timers.db")
conn2 = sqlite3.connect("timers_temp.db")
c = conn.cursor()
c2 = conn2.cursor()

c.execute(
    """CREATE TABLE IF NOT EXISTS timers (
        ping_date text,
        req_date text,
        del_code text,
        user_id text,
        channel text,
        message text,
        badgermode text,
        delta text,
        whole text
        )"""
)

c2.execute(
    """CREATE TABLE IF NOT EXISTS temp_timers (
        ping_date text,
        req_date text,
        del_code text,
        user_id text,
        channel text,
        message text,
        badgermode text,
        delta text,
        whole text
        )"""
)


def insert_timer(timer: Timerz):
    print("Delcode is " + timer.del_code)
    c.execute(
        """INSERT INTO timers VALUES 
    (:ping_date,:req_date,:del_code,:user_id,:channel,:message,:badgermode,:delta, :whole)""",
        {
            "ping_date": timer.ping_time,
            "req_date": timer.req_time,
            "del_code": timer.del_code,
            "user_id": timer.user_id,
            "channel": timer.channel,
            "message": timer.message,
            "badgermode": timer.badgermode,
            "delta": timer.delta,
            "whole": timer.to_string(),
        },
    )
    conn.commit()


def search_timer(hexcode):
    c.execute("SELECT * FROM timers WHERE del_code=:del_code", {"del_code": hexcode})
    return c.fetchall()


def search_next_timers():
    c.execute(
        """SELECT *
    FROM timers
    ORDER BY ping_date ASC
    LIMIT 10;
    """
    )
    return c.fetchall()


def get_my_timers(user):
    c.execute(
        """SELECT *
    FROM timers
    WHERE user_id=:user_id
    ORDER BY ping_date ASC
    LIMIT 30;
    """,
        {"user_id": user},
    )
    return c.fetchall()


def remove_timer(hexcode):
    cursor = c.execute(
        "DELETE FROM timers WHERE del_code=:del_code", {"del_code": hexcode}
    )
    print(f"remove_timer affected {cursor.rowcount} rows deleting hexcode={hexcode}")
    conn.commit()


def pop_timer(timer: Timerz):
    cursor = c.execute(
        "DELETE FROM timers WHERE ping_date=:ping_date AND req_date=:req_date AND del_code=:del_code",
        {
            "ping_date": timer.ping_time,
            "req_date": timer.req_time,
            "del_code": timer.del_code,
        },
    )
    print(
        f"pop_timer affected {cursor.rowcount} rows deleting with={timer.ping_time , timer.req_time}"
    )
    conn.commit()


def db_to_temp():
    c.execute(
        """SELECT *
    FROM timers;
    """,
    )
    timers_db = c.fetchall()
    if timers_db:
        ##How to copy things into temp database?
        c2.executemany("INSERT INTO temp_timers VALUES(?,?,?,?,?,?,?,?,?)", timers_db)
        copied = True
        conn2.commit()
    else:
        copied = False
    return copied


def concat_db():
    c2.execute(
        """SELECT *
    FROM temp_timers;
    """,
    )
    temp_db = c2.fetchall()
    added = False
    if temp_db:
        c.executemany("INSERT INTO timers VALUES(?,?,?,?,?,?,?,?,?)", temp_db)
        conn.commit()
        c2.execute("DROP TABLE temp_timers;")
        conn2.commit()
        added = True
    return added
