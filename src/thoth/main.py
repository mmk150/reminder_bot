from thoth import Timerz, commandio, databaseio
import dateutil.parser
import discord
import datetime
import secrets

from discord.ext import tasks

import asyncio

intents: discord.Intents = discord.Intents.default()
intents.message_content = True
intents.typing = False
intents.presences = False
#intents.reactions = True
client = discord.Client(intents=intents)
botready=False


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    global botready
    botready=True
    await client.change_presence(activity=discord.Game('thoth;help'))
    check_timers.start()


@tasks.loop(seconds=5)
async def check_timers():
    timer_ob: Timerz.Timerz
    chan: discord.TextChannel
    if not botready:
        return
    else:
        now=datetime.datetime.now()
        r= await next_ten_timers()
        print(r)
        print(len(r))
        if r !=[]:
            for y in r:
                timer_obj= Timerz.Timerz.from_string(y[-1])
                x=dateutil.parser.parse(timer_obj.ping_time)
                delta=x-now
                truedelta=delta.seconds + delta.days*3600*24
                print(truedelta)
                print(y)
                chan_id=int(timer_obj.channel)
                chan=client.get_channel(chan_id)
                if truedelta<= 9:
                    if truedelta<=-600:
                        await send_late_reminder(timer_obj)
                        return
                    badgering_or_not=y[len(y)-3]
                    if int(badgering_or_not)>0:
                        await badger_next_reminder(timer_obj)
                    else:
                        await send_next_reminder(timer_obj)

                    return






@client.event
async def on_message(message):
    author:discord.User
    channel: int
    server: discord.Guild


    author = message.author
    channel = message.channel.id
    server=message.guild
    if server==None:
        return
    if message.author == client.user:
        return
    if message.content.startswith("thoth;"):

        time_now = datetime.datetime.now()
        rest=message.content
        rest=rest[6:]
        del_code = secrets.token_hex(3)
        if message.content.startswith("thoth;help"):
            response= commandio.helpy(rest, channel)
            await message.channel.send(response)
        elif message.content.startswith("thoth;badger"):
            try:
                timer_arr= commandio.parse_message(author, time_now, channel, del_code, rest, 3)
            except:
                x=commandio.error_message()
                await message.channel.send(x)
                return
            for x in timer_arr:
                databaseio.insert_timer(x)
            await message.channel.send("Very well, I'll scribble that down for you. The deletion code for these timers is: " + del_code)
        else:
            try:
                timer_arr= commandio.parse_message(author, time_now, channel, del_code, rest, 0)
            except:
                x = commandio.error_message()
                await message.channel.send(x)
                return
            print(timer_arr)
            if timer_arr[0]=="Deleted!":
                await message.channel.send("I have deleted all reminders with the code: " + timer_arr[1])
            elif timer_arr[0]=="Error_Message":
                response=commandio.error_message()
                await message.channel.send(response)
            else:
                print(timer_arr[0])
                print(timer_arr[0].ping_time)
                for x in timer_arr:
                    databaseio.insert_timer(x)
                await message.channel.send("Very well, I'll scribble that down for you. The deletion code for these timers is: " + del_code)


async def admin_clear():
    while databaseio.search_next_timers()!=[]:
        x= databaseio.search_next_timers()
        for y in x:
            timer= Timerz.Timerz.from_string(y[-1])
            databaseio.remove_timer(timer.del_code)
    return



async def next_ten_timers():
    timers= databaseio.search_next_timers()
    return timers

async def send_next_reminder(timer: Timerz.Timerz):
    user: discord.User
    channeler:discord.TextChannel

    userid = int(timer.user_id)
    print(userid)
    user=await client.fetch_user(userid)
    print(user)
    mention=user.mention
    chan_id=int(timer.channel)
    channeler= client.get_channel(chan_id)
    message=timer.message
    full_message= "Hi " + mention + " , reminder: " + message + " (" + timer.del_code + ")"
    await channeler.send(full_message)
    if timer.delta!="0":
        old_ping_time = dateutil.parser.parse(timer.ping_time)
        print("old_ping_time is: ")
        print(old_ping_time)
        time_delta= datetime.timedelta(seconds=int(float(timer.delta)))
        print("time_delta is: " )
        print(time_delta)
        new_start=old_ping_time+time_delta
        newtimer=Timerz.Timerz(str(new_start), timer.req_time, timer.user_id, timer.del_code, timer.channel, timer.message, timer.badgermode,timer.delta)
        databaseio.insert_timer(newtimer)
    databaseio.pop_timer(timer)
    return

async def badger_next_reminder(timer: Timerz.Timerz):
    user: discord.User
    channeler: discord.TextChannel
    message:str

    chanid=int(timer.channel)
    chan=client.get_channel(chanid)
    user = await client.fetch_user(int(timer.user_id))
    mention=user.mention
    message=timer.message

    full_message: str = "Hi " + mention + " , reminder: " + message + ".\n" + "Please react ✅ to this message to acknowledge." + "(" +timer.del_code + ")"
    if int(timer.badgermode)>1:
        badge_init_delcode= commandio.badger_init(timer)
    else:
        badge_init_delcode=timer.del_code
    r = await chan.send(full_message)




    databaseio.pop_timer(timer)
    asyncio.create_task(reactcheck(r,user,badge_init_delcode))
    return

async def send_late_reminder(timer: Timerz.Timerz):
    user: discord.User
    channeler:discord.TextChannel

    userid = int(timer.user_id)
    print(userid)
    user=await client.fetch_user(userid)
    print(user)
    mention=user.mention
    chan_id=int(timer.channel)
    channeler= client.get_channel(chan_id)
    message=timer.message
    full_message= "Hi " + mention + " , reminder: " + message+ ".\n NOTE: THIS TIMER IS PROBABLY EXPIRED! Sorry for the downtime :c ." + " (" + timer.del_code + ")"
    await channeler.send(full_message)
    if timer.delta!="0":
        old_ping_time = dateutil.parser.parse(timer.ping_time)
        print("old_ping_time is: ")
        print(old_ping_time)
        time_delta= datetime.timedelta(seconds=int(float(timer.delta)))
        print("time_delta is: " )
        print(time_delta)
        new_start=old_ping_time+time_delta
        newtimer=Timerz.Timerz(str(new_start), timer.req_time, timer.user_id, timer.del_code, timer.channel, timer.message, timer.badgermode,timer.delta)
        databaseio.insert_timer(newtimer)
    databaseio.pop_timer(timer)
    return

async def reactcheck(message: discord.Message, user: discord.User, delcode:str):
    allowed_message_id = message.id
    def check(reaction: discord.Reaction, disc_user: discord.User):
        return user.id == disc_user.id and reaction.message.id == allowed_message_id and str(reaction.emoji) == "✅"
    try:
        await client.wait_for('reaction_add', timeout=290.0, check=check)
    except asyncio.TimeoutError:
        return
    databaseio.remove_timer(delcode)
    return







def start():
    import os
    client.run(os.environ.get('THOTH_DISCORD_TOKEN'))



