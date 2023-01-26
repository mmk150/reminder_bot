import Timerz, commandio, databaseio
import dateutil.parser
import datetime
import secrets
import discord
from discord import app_commands
from discord.ext import tasks
import asyncio


class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            for g in self.guilds:
                self.tree.copy_global_to(guild=g)
                await self.tree.sync(guild=g)
            self.synced = True
        print(f"We have logged in as {self.user}.")
        check_timers.start()


client = aclient()

guildlist = client.guilds
tree = client.tree


@tree.command(
    name="help",
    description="This function will link you to some more detailed documentation.",
    guilds=guildlist,
)
async def self(interaction: discord.Interaction):
    reply = """```
        Here is a list of my slash commands with abbreviated descriptions:
        /help -> This message!
        /reminder -> A basic reminder -- really a glorified timer. Reminds you when the timer is up.
        /calendar-> Calendar reminder. Input a specific calendar date and time.
        /recurring -> A recurring reminder that repeats according to a frequency(of at least 30 mins).
        /rm -> Short version of basic reminder. Time is in minutes.
        /rec_now -> Short version of recurring reminder. Start date/time determined by the current time.
        /delete -> Command to delete a set of reminders.Input the deletion code associated with the reminder(s).
        /get_reminders -> bot dms you a list of active reminders
        More extensive documentation pending.```
        """
    await interaction.response.send_message(f"Hello {interaction.user}!\n" + reply)


@tree.command(
    name="reminder",
    description="Basic reminder function-- really a glorified timer. Reminds you when the timer is up.",
    guilds=guildlist,
)
@app_commands.describe(
    time="Please input 'N TIMEUNITS' where TIMEUNITS is minutes,hours,days,weeks or months.",
    message="The message you want attached to this reminder.",
    badger="Input '1' to have the bot repeatedly ping until you react to the reminder.",
)
async def self(interaction: discord.Interaction, time: str, message: str, badger: str):
    time_now = datetime.datetime.now()
    channel = interaction.channel_id
    user = interaction.user.id
    user = await client.fetch_user(user)
    del_code = secrets.token_hex(3)
    badger = badger.strip()
    match badger:
        case "1":
            badgermode = 3
        case _:
            badgermode = 0

    message = time + " " + message
    try:
        timer_arr = commandio.parse_message(
            user, time_now, channel, del_code, message, badgermode, "reminder"
        )
    except:
        x = commandio.error_message()
        await interaction.response.send_message(x)
        return
    print(timer_arr)
    if timer_arr[0] == "Error_Message":
        response = commandio.error_message()
        await interaction.response.send_message(response)
    else:
        print(timer_arr[0])
        print(timer_arr[0].ping_time)
        for x in timer_arr:
            databaseio.insert_timer(x)
        await interaction.response.send_message(
            f"Very well, I'll scribble that down for you. The deletion code for these timers is:  {del_code}"
        )


@tree.command(
    name="calendar",
    description="Calendar reminder. Input a specific calendar date and time.",
    guilds=guildlist,
)
@app_commands.describe(
    date="Please input 'MM/DD/YYYY' where these are integer valued and represent a future (or present) date.",
    time="Please input 'hh:mm' to set a time for your reminder on a 24 hour clock (sometimes called 'military time')",
    message="The message you want attached to this reminder.",
    badger="Input 1 to have the bot repeatedly ping until you react to the reminder.",
)
async def self(
    interaction: discord.Interaction, date: str, time: str, message: str, badger: str
):
    time_now = datetime.datetime.now()
    channel = interaction.channel_id
    user = interaction.user.id
    user = await client.fetch_user(user)
    del_code = secrets.token_hex(3)
    badger = badger.strip()
    match badger:
        case "1":
            badgermode = 3
        case _:
            badgermode = 0

    message = date + " " + time + " " + message
    try:
        timer_arr = commandio.parse_message(
            user, time_now, channel, del_code, message, badgermode, "calendar"
        )
    except:
        x = commandio.error_message()
        await interaction.response.send_message(x)
        return
    print(timer_arr)
    if timer_arr[0] == "Error_Message":
        response = commandio.error_message()
        await interaction.response.send_message(response)
    else:
        print(timer_arr[0])
        print(timer_arr[0].ping_time)
        for x in timer_arr:
            databaseio.insert_timer(x)
        await interaction.response.send_message(
            f"Very well, I'll scribble that down for you. The deletion code for these timers is:  {del_code}"
        )


@tree.command(
    name="recurring",
    description="A recurring calendar reminder. Will repeat according to a frequency(of at least 30 mins).",
    guilds=guildlist,
)
@app_commands.describe(
    start_date="Please input 'MM/DD/YYYY' where these are integer valued and represent a future or present date.",
    start_time="Please input 'hh:mm' to set a time for your reminder on a 24 hour clock.",
    frequency="Frequency: input 'N TIMEUNITS' where TIMEUNITS is minutes,hours,days,weeks or months.",
    message="The message you want attached to this reminder.",
    badger="Input 1 to have the bot repeatedly ping until you react to the reminder.",
)
async def self(
    interaction: discord.Interaction,
    start_date: str,
    start_time: str,
    frequency: str,
    message: str,
    badger: str,
):
    time_now = datetime.datetime.now()
    channel = interaction.channel_id
    user = interaction.user.id
    user = await client.fetch_user(user)
    del_code = secrets.token_hex(3)
    badger = badger.strip()
    match badger:
        case "1":
            badgermode = 3
        case _:
            badgermode = 0

    message = start_date + " " + start_time + " every " + frequency + " " + message
    try:
        timer_arr = commandio.parse_message(
            user, time_now, channel, del_code, message, badgermode, "recurring"
        )
    except:
        x = commandio.error_message()
        await interaction.response.send_message(x)
        return
    print(timer_arr)
    if timer_arr[0] == "Error_Message":
        response = commandio.error_message()
        await interaction.response.send_message(response)
    else:
        print(timer_arr[0])
        print(timer_arr[0].ping_time)
        for x in timer_arr:
            databaseio.insert_timer(x)
        await interaction.response.send_message(
            f"Very well, I'll scribble that down for you. The deletion code for these reminders is:  {del_code}"
        )


@tree.command(
    name="delete",
    description="Command to delete a set of reminders.Input the deletion code associated with the reminder(s).",
    guilds=guildlist,
)
@app_commands.describe(
    del_code="Input the deletion code of the reminder(s) you want to delete.",
)
async def self(interaction: discord.Interaction, del_code: str):
    time_now = datetime.datetime.now()
    channel = interaction.channel_id
    user = interaction.user.id
    user = await client.fetch_user(user)
    badgermode = 0

    try:
        timer_arr = commandio.parse_message(
            user, time_now, channel, del_code, del_code, badgermode, "delete"
        )
    except:
        x = commandio.error_message()
        await interaction.response.send_message(x)
        return
    if timer_arr[0] == "Error_Message":
        response = commandio.error_message()
        await interaction.response.send_message(response)
    else:
        print(timer_arr[0])
        await interaction.response.send_message(
            f"I have deleted all reminders with the code: " + timer_arr[1]
        )


@tree.command(
    name="get_reminders",
    description="Messages you a list of your future reminders.",
    guilds=guildlist,
)
async def self(interaction: discord.Interaction):
    channel = interaction.channel_id
    user = interaction.user.id
    user = await client.fetch_user(user)
    message = "Hello, here are your upcoming reminders:\n"
    next_timers = databaseio.get_my_timers(user.id)
    for i in range(len(next_timers)):
        x = next_timers[i]
        timer_obj = Timerz.Timerz.from_string(x[-1])
        temp = [timer_obj.ping_time[0:17], timer_obj.del_code, timer_obj.message]
        newline = f"Reminder: '**{temp[2]}**'. Goes off at: {temp[0]}. This reminder has deletion code: {temp[1]} \n"
        message = message + newline
    try:
        await interaction.user.send(message)
    except:
        await interaction.user.create_dm("Creating DM")
        await interaction.user.send(message)
    await interaction.response.send_message(
        "Sent you a message containing your reminders."
    )


@tree.command(
    name="rm",
    description="Short version of basic reminder. Time is in minutes.",
    guilds=guildlist,
)
@app_commands.describe(
    time="Please input 'N' where N is the number of minutes until the reminder.",
    message="The message you want attached to this reminder.",
)
async def self(interaction: discord.Interaction, time: str, message: str):
    time_now = datetime.datetime.now()
    channel = interaction.channel_id
    user = interaction.user.id
    user = await client.fetch_user(user)
    del_code = secrets.token_hex(3)
    badgermode = 0

    message = time + " minutes " + message
    try:
        timer_arr = commandio.parse_message(
            user, time_now, channel, del_code, message, 0, "reminder"
        )
    except:
        x = commandio.error_message()
        await interaction.channel.send(x)
        return
    print(timer_arr)
    if timer_arr[0] == "Error_Message":
        response = commandio.error_message()
        await interaction.channel.send(response)
    else:
        print(timer_arr[0])
        print(timer_arr[0].ping_time)
        for x in timer_arr:
            databaseio.insert_timer(x)
        await interaction.response.send_message(
            f"Very well, I'll scribble that down for you. The deletion code for these timers is:  {del_code}"
        )


@tree.command(
    name="rec_now",
    description="Short version of recurring reminder. Start date/time determined by the current time.",
    guilds=guildlist,
)
@app_commands.describe(
    frequency="Please input 'N' where N is the number of minutes until you wish to be reminded.",
    message="The message you want attached to this reminder.",
)
async def self(interaction: discord.Interaction, frequency: str, message: str):
    time_now = datetime.datetime.now()
    channel = interaction.channel_id
    user = interaction.user.id
    user = await client.fetch_user(user)
    del_code = secrets.token_hex(3)

    start_date = time_now.date().strftime("%m/%d/%Y")
    time_offset = datetime.timedelta(seconds=120)
    start_time = time_now + time_offset
    start_time = start_time.time().strftime("%H:%M")
    message = start_date + " " + start_time + " every " + frequency + " " + message
    print(message)
    try:
        timer_arr = commandio.parse_message(
            user, time_now, channel, del_code, message, 0, "recurring"
        )
    except:
        x = commandio.error_message()
        await interaction.response.send_message(x)
        return
    print(timer_arr)
    if timer_arr[0] == "Error_Message":
        response = commandio.error_message()
        await interaction.response.send_message(response)
    else:
        print(timer_arr[0])
        print(timer_arr[0].ping_time)
        for x in timer_arr:
            databaseio.insert_timer(x)
        await interaction.response.send_message(
            f"Very well, I'll scribble that down for you. The deletion code for these timers is:  {del_code}"
        )


@tasks.loop(seconds=5)
async def check_timers():
    timer_ob: Timerz.Timerz
    chan: discord.TextChannel
    if not client.synced:
        return
    else:
        now = datetime.datetime.now()
        r = await next_ten_timers()
        print(r)
        print(len(r))
        if r != []:
            for y in r:
                timer_obj = Timerz.Timerz.from_string(y[-1])
                x = dateutil.parser.parse(timer_obj.ping_time)
                delta = x - now
                truedelta = delta.seconds + delta.days * 3600 * 24
                print(truedelta)
                print(y)
                chan_id = int(timer_obj.channel)
                chan = client.get_channel(chan_id)
                if truedelta <= 9:
                    if truedelta <= -600:
                        await send_late_reminder(timer_obj)
                        return
                    badgering_or_not = y[len(y) - 3]
                    if int(badgering_or_not) > 0:
                        await badger_next_reminder(timer_obj)
                    else:
                        await send_next_reminder(timer_obj)
                    return


async def next_ten_timers():
    timers = databaseio.search_next_timers()
    return timers


async def send_next_reminder(timer: Timerz.Timerz):
    user: discord.User
    channeler: discord.TextChannel

    userid = int(timer.user_id)
    print(userid)
    user = await client.fetch_user(userid)
    print(user)
    mention = user.mention
    chan_id = int(timer.channel)
    channeler = client.get_channel(chan_id)
    message = timer.message
    full_message = (
        "Hi " + mention + " , reminder: " + message + " (" + timer.del_code + ")"
    )
    await channeler.send(full_message)
    if timer.delta != "0":
        old_ping_time = dateutil.parser.parse(timer.ping_time)
        print("old_ping_time is: ")
        print(old_ping_time)
        time_delta = datetime.timedelta(seconds=int(float(timer.delta)))
        print("time_delta is: ")
        print(time_delta)
        new_start = old_ping_time + time_delta
        newtimer = Timerz.Timerz(
            str(new_start),
            timer.req_time,
            timer.user_id,
            timer.del_code,
            timer.channel,
            timer.message,
            timer.badgermode,
            timer.delta,
        )
        databaseio.insert_timer(newtimer)
    databaseio.pop_timer(timer)
    return


async def badger_next_reminder(timer: Timerz.Timerz):
    user: discord.User
    channeler: discord.TextChannel
    message: str

    chanid = int(timer.channel)
    chan = client.get_channel(chanid)
    user = await client.fetch_user(int(timer.user_id))
    mention = user.mention
    message = timer.message

    full_message: str = (
        "Hi "
        + mention
        + " , reminder: "
        + message
        + ".\n"
        + "Please react ✅ to this message to acknowledge."
        + "("
        + timer.del_code
        + ")"
    )
    if int(timer.badgermode) > 1:
        badge_init_delcode = commandio.badger_init(timer)
    else:
        badge_init_delcode = timer.del_code
    r = await chan.send(full_message)

    databaseio.pop_timer(timer)
    asyncio.create_task(reactcheck(r, user, badge_init_delcode))
    return


async def send_late_reminder(timer: Timerz.Timerz):
    user: discord.User
    channeler: discord.TextChannel

    userid = int(timer.user_id)
    print(userid)
    user = await client.fetch_user(userid)
    print(user)
    mention = user.mention
    chan_id = int(timer.channel)
    channeler = client.get_channel(chan_id)
    message = timer.message
    full_message = (
        "Hi "
        + mention
        + " , reminder: "
        + message
        + ".\n NOTE: THIS TIMER IS PROBABLY EXPIRED! Sorry for the downtime :c ."
        + " ("
        + timer.del_code
        + ")"
    )
    await channeler.send(full_message)
    if timer.delta != "0":
        old_ping_time = dateutil.parser.parse(timer.ping_time)
        print("old_ping_time is: ")
        print(old_ping_time)
        time_delta = datetime.timedelta(seconds=int(float(timer.delta)))
        print("time_delta is: ")
        print(time_delta)
        new_start = old_ping_time + time_delta
        newtimer = Timerz.Timerz(
            str(new_start),
            timer.req_time,
            timer.user_id,
            timer.del_code,
            timer.channel,
            timer.message,
            timer.badgermode,
            timer.delta,
        )
        databaseio.insert_timer(newtimer)
    databaseio.pop_timer(timer)
    return


async def reactcheck(message: discord.Message, user: discord.User, delcode: str):
    allowed_message_id = message.id

    def check(reaction: discord.Reaction, disc_user: discord.User):
        return (
            user.id == disc_user.id
            and reaction.message.id == allowed_message_id
            and str(reaction.emoji) == "✅"
        )

    try:
        await client.wait_for("reaction_add", timeout=290.0, check=check)
    except asyncio.TimeoutError:
        return
    databaseio.remove_timer(delcode)
    return


client.run("OTY2ODM0MjQwMDQ0MDI3OTU0.GJgCCC.5oyHkxl-jaxDmR3UiqjVhOk_kHUtAQLFmoeRPw")
