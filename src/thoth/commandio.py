from . import databaseio
import discord
import datetime
import dateutil
import re
import secrets
from .timecalcs import word_to_time, convert_timer
from .Timerz import Timerz


def parse_message(
    user: discord.User,
    req_time: datetime.datetime,
    channel: discord.TextChannel.id,
    del_code,
    message,
    badgermode,
    command,
):

    x = message.split()
    word = x[0]
    assert type(command) == str
    match command:
        case "reminder":
            print("case rem")
            y = reminder(x[0:], user, req_time, channel, del_code, badgermode)
            # y is an array with a single Timerz
        case "calendar":
            print("case cal")
            y = calendar(x[0:], user, req_time, channel, del_code, badgermode)
            # y is an array with a single Timerz
        case "recurring":
            print("case rec")
            y = recurring(x[0:], user, req_time, channel, del_code, badgermode)
            # y is an array with a single Recurring Timerz
        case "delete":
            print("case del")
            y = delete(x[0], user, channel)
        case _:
            print("case catchall")
            y = ["Error_Message"]
    return y


def reminder(
    message_frag,
    user: discord.User,
    req_time: datetime.datetime,
    channel: discord.TextChannel.id,
    del_code,
    badgermode,
):
    N = float(message_frag[0])
    unit = word_to_time(message_frag[1])
    message = message_maker(message_frag[2:])
    delta = datetime.timedelta(seconds=convert_timer(N, unit))
    ping_time = req_time + delta
    y = [
        Timerz(
            str(ping_time),
            str(req_time),
            str(user.id),
            str(del_code),
            str(channel),
            str(message),
            str(badgermode),
        )
    ]
    return y


def message_maker(message_arr):
    str = ""
    for x in message_arr:
        str = str + " " + x + " "
    return str


def calendar(
    message_frag,
    user: discord.User,
    req_time: datetime.datetime,
    channel: discord.TextChannel.id,
    del_code,
    badgermode,
):
    x = message_frag[0] + " " + message_frag[1]
    message = message_maker(message_frag[2:])

    ping_time = datetime.datetime.strptime(x, "%m/%d/%Y %H:%M")

    y = [
        Timerz(
            str(ping_time),
            str(req_time),
            str(user.id),
            str(del_code),
            str(channel),
            str(message),
            str(badgermode),
        )
    ]
    return y


def recurring(
    message_frag,
    user: discord.User,
    req_time: datetime.datetime,
    channel: discord.TextChannel.id,
    del_code,
    badgermode,
):
    x = message_frag[0] + " " + message_frag[1]
    ping_time_start = datetime.datetime.strptime(x, "%m/%d/%Y %H:%M")
    ratestring = message_frag[3:]
    N = float(ratestring[0])
    unit = word_to_time(ratestring[1])
    message = message_maker(ratestring[2:])
    delta = convert_timer(N, unit)
    now = datetime.datetime.now()
    time_delta = ping_time_start - now
    truedelta = time_delta.seconds + time_delta.days * 3600 * 24
    if delta > 1800 and truedelta > 0:
        y = [
            Timerz(
                str(ping_time_start),
                str(req_time),
                str(user.id),
                str(del_code),
                str(channel),
                str(message),
                str(badgermode),
                str(delta),
            )
        ]
    else:
        y = ["Error_Message"]
    return y


def badger_init(timer: Timerz):
    ping_time_start = dateutil.parser.parse(timer.ping_time)
    delta = datetime.timedelta(seconds=300)
    delcode = secrets.token_hex(3)
    badgermode = 1
    for x in range(1, 5):
        var = ping_time_start + x * delta
        mess = timer.message
        if x == 4:
            mess = mess + ". This is the final reminder!"
        timer = Timerz(
            str(var),
            timer.req_time,
            timer.user_id,
            delcode,
            timer.channel,
            mess,
            str(badgermode),
        )
        databaseio.insert_timer(timer)
    return delcode


def delete(hexcode, user: discord.User, channel):
    print(type(hexcode))
    print(hexcode)
    x = databaseio.search_timer(hexcode)
    timer = Timerz.from_string(x[0][-1])
    print(timer)
    print(user.id)
    userid = int(timer.user_id)
    print(userid)
    if user.id == userid:
        databaseio.remove_timer(hexcode)
        return ["Deleted!", hexcode]
    return ["Permissions Error", hexcode]


def error_message():
    mes = "You seem to be having some trouble with the bot. Use ``/help`` for guidance."
    return mes


def helpy(message_frag, channel: discord.TextChannel.id):
    mes = message_frag.split()
    if len(mes) > 1:
        word = mes[1]
        match word:
            case "badger":
                reply = """Prefixing a valid reminder command with `badger` will have the bot pester you for an acknowledgement of the associated reminder upon delivery, in five minute intervals.
The user must react to the message to acknowledge.
Ex: ``thoth;badger reminder 5 hours eat dinner``."""
            case "reminder":
                reply = """Basic reminder command. Follows the format ``thoth;reminder N TIMEUNIT message``, where N is an integer and TIMEUNIT takes on one of the following values:minutes, hours, days, weeks, months.
Ex: ``thoth;reminder 5 hours eat dinner``.
                """
            case "calendar":
                reply = """Command to schedule a reminder based on a date and time. Follows the format ``thoth;calendar MM/DD/YYYY hh:mm message``, where all variables are integer valued and time is on a 24-hour clock.
Ex: ``thoth;calendar 08/08/2022 19:00 drink water`` will result in the bot reminding you at this date and time to drink water. 
                """
            case "recurring":
                reply = """Command to schedule a recurring reminder. Follows the format ``thoth;recurring MM/DD/YYYY hh:mm every N TIMEUNITS message``, where all date and time variables are integer valued and time is on a 24-hour clock, N is an integer, and TIMEUNITS are as in the thoth;reminder command.
Ex: ``thoth;calendar 08/08/2022 19:00 every 30 minutes drink water`` will result in the bot reminding you at this date and time to drink water, and every thirty minutes afterwards. Note: To prevent abuse, the time between reminders must be at least 30 minutes and the start time must be in the future!!
                """
            case "help":
                reply = """You think you're clever, don't you?
                """
            case "delete":
                reply = """Command to delete a set of reminders. Each time you ask Thoth to write a reminder or set of reminders, it will respond with a code that you can use with this command to delete the reminders associated with that particular code.
                Follows the format ``thoth;delete X`` where X is the deletion code.
                """
            case _:
                reply = error_message()

    else:
        reply = """
        List of commands:
        reminder
        calendar
        recurring
        badger
        delete
        
        Use ```thoth;help COMMAND``` to get a description of individual commands for the bot.
         """
    return reply
