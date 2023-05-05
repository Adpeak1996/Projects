import os
from sys import exec_prefix

import discord
import pymysql
from discord.ext import commands, tasks

# Add a discord token here
TOKEN = ''

# Intents and bot command prefix
intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

# Create Database Function
# Use LocalHost as a demonstration
def create_connection():
    return pymysql.connect(
        host = '127.0.0.1',
        user = 'admin',
        password = 'password',
        database = 'test_schema',
        autocommit = True,
        cursorclass = pymysql.cursors.SSCursor,
        connect_timeout=1,
)


# Grab all members from the server
@bot.command(name='db', help='Add members from the Discord Server into the Database')
@commands.has_any_role("Right Hand", "Guild Leader", "God of Bots", "Officer")
async def db(ctx):
    try:
        mydb = create_connection()
        cursor = mydb.cursor()
        mydb

        print("Connection to the database established successfully.")

        guild_id = ctx.author.guild.id
        guild = bot.get_guild(guild_id)
        guild_people = set([people.display_name for people in guild.members])

        print("Successfully retrieved all members from the server.")

        # Get current database users
        cursor.execute("SELECT NICKNAME FROM users")
        db_users = set([row[0] for row in cursor.fetchall()])

        print("Successfully retrieved all users from the database.")

        # Add new users to database
        new_users = guild_people - db_users
        if new_users:
            sql = "INSERT IGNORE INTO users (NICKNAME) VALUES (%s)"
            mydb.ping()
            cursor.executemany(sql, [(r,) for r in new_users])
            
            print("Successfully added new users to the database.")
        else:
            print("No new users to add to the database.")

        await ctx.send('Database has been Updated!')
        await ctx.send(f'{len(new_users)} user(s) added to the database.')

        # Remove users that are no longer in the Discord server
        old_users = db_users - guild_people
        if old_users:
            sql = "DELETE FROM users WHERE NICKNAME=%s"
            mydb.ping()
            cursor.executemany(sql, [(r,) for r in old_users])
            print("Successfully removed old users from the database.")
        else:
            print("No old users to remove from the database.")
        await ctx.send(f'{len(old_users)} user(s) removed from the database.')

        cursor.close()
        mydb.close()

        print("Connection to the database closed successfully.")

    except Exception as e:
        print(e)


# Add all Members from a voice channel to start split
@bot.command(name = 'split', help = 'Starts a loot split')
@commands.has_any_role("Right Hand", "Guild Leader", "God of Bots", "Officer")
async def split(ctx):
    mydb = create_connection()
    cursor = mydb.cursor()
    

    # Title
    await ctx.send("**Players**")

    guild_id = ctx.author.guild.id
    guild = bot.get_guild(guild_id)
    split.guild_people = ([people.display_name for people in guild.members])

    channel_id = ctx.author.voice.channel.id
    channel = bot.get_channel(channel_id)

    # Iterate through each member in the channel and send to discord channel
    for m in channel.members:
        split.msg = await ctx.send(m.display_name)
    # Iterate through each member and add to m || m = all members in channel
    m = []
    split.m = ([m.display_name for m in channel.members])

  
    #split.number_of_people = [str(i) for i in channel.members]
    split.total_people = len(split.m)

    # Add Total number of people
    sql = "UPDATE users SET NUMBEROFPEOPLE = %s"
    mydb.ping()
    cursor.execute(sql, (split.total_people))

    # Reset HALFSPLIT
    sql = "UPDATE users SET HALFSPLIT = %s"
    mydb.ping()
    cursor.execute(sql, (0))


    cursor.close()
    mydb.close()

    

@bot.command(name = '+1/2', help = 'When a player joines late (1/2) Split -- Only use after adding Full Split Players')
@commands.has_any_role("Right Hand", "Guild Leader", "God of Bots", "Officer")
async def joinLate(ctx, *args):
    mydb = create_connection()
    cursor = mydb.cursor()

    player = ' '.join(args)
    
    try:
        if player in split.guild_people:
            split.m.append(player)
            split.total_people = len(split.m)
            sql = "UPDATE users SET NUMBEROFPEOPLE = %s"
            mydb.ping()
            cursor.execute(sql, (split.total_people))
            sql = "UPDATE users SET HALFSPLIT = %s WHERE NICKNAME = %s"
            mydb.ping()
            cursor.execute(sql, (1, player))
            await ctx.send(player + " (1/2)")
        else:
            await ctx.send(player + " is not in the Discord server!")
    except:
        await ctx.send("Error! You must use the split command first!")

    mydb.close()
    cursor.close()


@bot.command(name = '+', help = 'Add a player to Full Split')
@commands.has_any_role("Right Hand", "Guild Leader", "God of Bots", "Officer")
async def joinFull(ctx, *args):
    mydb = create_connection()
    cursor = mydb.cursor()
    player = ' '.join(args)

    try:
        if player in split.guild_people:
            split.m.append(player)
            split.total_people = len(split.m)
            sql = "UPDATE users SET NUMBEROFPEOPLE = %s"
            mydb.ping()
            cursor.execute(sql, (split.total_people))
            await ctx.send(player)
        else:
            await ctx.send(player + " is not in the Discord server!")
    except:
        await ctx.send("Error! You must use the split command first!")
    cursor.close()
    mydb.close()

@bot.command(name = '-', help = 'Remove player from Split')
@commands.has_any_role("Right Hand", "Guild Leader", "God of Bots", "Officer")
async def joinFull(ctx, *args):
    mydb = create_connection()
    cursor = mydb.cursor()

    player = ' '.join(args)

    try:
        if player in split.guild_people:
            split.m.remove(player)
            split.total_people = len(split.m)
            sql = "UPDATE users SET NUMBEROFPEOPLE = %s"
            mydb.ping()
            cursor.execute(sql, (split.total_people))

            await ctx.send(player + " was removed!")
        else:
            await ctx.send(player + " is not in the Discord server!")
    except:
        await ctx.send("Error! You must use the split command first!")
    cursor.close()
    mydb.close()


# Adds Estimated Value into Loot Split
@bot.command(name = '$', help = 'Estimated Value Input')
@commands.has_any_role("Right Hand", "Guild Leader", "God of Bots", "Officer")
async def estimatedSplit(ctx, value):
    mydb = create_connection()
    cursor = mydb.cursor()
    

    # Update estimatedTotal in Database 
    sql = "UPDATE users SET estimatedTotal = estimatedTotal + %s"
    val = value
    cursor.execute(sql, val)

    # Calculate Title
    await ctx.send("**Calculate Split**")
    estimatedSplit.updateValue = int(value)
    cursor.close()
    mydb.close()
    formatNumber = "{:,}".format(int(value))
    await ctx.send("Estimated Value: " + formatNumber + " silver")

# Takes repair cost and deducts from estimatedTotal
@bot.command(name = 'repair', help = 'Subtracts Repair Cost from Estimated Value')
@commands.has_any_role("Right Hand", "Guild Leader", "God of Bots", "Officer")
async def repair(ctx, repairValue):
    mydb = create_connection()
    cursor = mydb.cursor()

    repairValue = int(repairValue)
    tax = .20

    estimatedSplit.updateValue = estimatedSplit.updateValue - int(repairValue)

    repair.totalTax = estimatedSplit.updateValue * tax

    repair.newTotal = estimatedSplit.updateValue - int(repair.totalTax)

    # Update estimatedTotal in Database
    sql = "UPDATE users SET estimatedTotal = %s"
    val = repair.newTotal
    cursor.execute(sql, val)

    repair.totalTax = int(repair.totalTax)
    numberFormat = "{:,}".format(int(repairValue))
    await ctx.send("Repair Bill: " + numberFormat + " silver")
    cursor.close()
    mydb.close()
 
# Add silver bags then update estimatedTotal in Database
@bot.command(name = 'silver', help = 'Adds Silver Bags to Estimated Value')
@commands.has_any_role("Right Hand", "Guild Leader", "God of Bots", "Officer")
async def estimatedSplit(ctx, silverValue):
    mydb = create_connection()
    cursor = mydb.cursor()

    estimatedValue = repair.newTotal + int(silverValue)

    # Update estimatedTotal in Database
    sql = "UPDATE users SET estimatedTotal = %s"
    val = estimatedValue
    cursor.execute(sql, val)
    numberFormat = "{:,}".format(int(silverValue))
    await ctx.send("Silver Bags: " + numberFormat + " silver")

    # Total Title
    await ctx.send("**Total**")

    # Select the estimatedTotal from the Database and get the total NUMBEROFPEOPLE from the Database
    cursor.execute("SELECT estimatedTotal FROM users")
    result = cursor.fetchone()
    cursor.execute("SELECT NUMBEROFPEOPLE FROM users")
    people = cursor.fetchone()
    total = int(result[0]) / int(people[0])
    print(int(people[0]))
    total = int(total)

   
    # Select everyone who gets a half split
    cursor.execute("SELECT NICKNAME FROM users WHERE HALFSPLIT = 1")
    row = cursor.fetchall()
    newRow = [x[0] for x in row]
    if len(newRow) == 0:
        pass
    else:        
        newRow.append("HalfSplit")

    try:
        # Find who gets a half split
        if 'HalfSplit' in newRow:
            for row in newRow:
                halfTotal = total / 2
                sql = "UPDATE users SET SILVER = SILVER + %s WHERE NICKNAME = %s"
                mydb.ping()
                cursor.execute(sql, (halfTotal, row))
            halfFormat = "{:,}".format(int(halfTotal))
        # Grab everyone that is in the split but not in the newRow list for people with halfsplit, then give them full split
        fullSplit = [i for i in split.m if i not in newRow]
        # Create variable for 
        for row in fullSplit:
            sql = "UPDATE users SET SILVER = SILVER + %s WHERE NICKNAME = %s"
            mydb.ping()
            cursor.execute(sql, (total, row))
    except:
        await ctx.send("Error Updating Splits!")

    totalFormat = "{:,}".format(int(total))
    taxFormat = "{:,}".format(int(repair.totalTax))
    await ctx.send("Full Split: " + totalFormat + " silver")
    if len(newRow) == 0:
        await ctx.send("(1/2) Split: 0 silver")
    else:
        await ctx.send("(1/2) Split: " + halfFormat + " silver")
    await ctx.send("Guild Tax: " + taxFormat + " silver")


    sql = "UPDATE users SET estimatedTotal = %s"
    val = 0
    cursor.execute(sql, val)

    cursor.close()
    mydb.close()



# Payout players silver balance
@bot.command(name='payout', help='Pays out a player')
@commands.has_any_role("Right Hand", "Guild Leader", "God of Bots", "Officer")
async def payout(ctx, *args):
    mydb = create_connection()
    cursor = mydb.cursor()

    player = ' '.join(args)

    guild_id = ctx.author.guild.id
    guild = bot.get_guild(guild_id)
    guild_people = [people.display_name for people in guild.members]

    cursor.execute("SELECT SILVER FROM users WHERE NICKNAME = %s", (player,))
    silver = cursor.fetchone()

    if silver:
        silver = int(silver[0])
        silver = "{:,}".format(int(silver))

        try:
            if player in guild_people:
                sql = "UPDATE users SET SILVER = %s WHERE NICKNAME = %s"
                val = (0, player)
                cursor.execute(sql, val)
                await ctx.send(f"{player} has been paid {silver} silver!")
            else:
                await ctx.send(f"{player} is not in the Discord server!")
        except:
            await ctx.send(f"Error! {player} is not in the Database!")
    else:
        await ctx.send(f"{player} does not have any silver to payout.")
        
    cursor.close()
    mydb.close()



# Reset Loot Split
@bot.command(name = 'reset', help = 'Resets Estimated Total and Number of People -- Incase of a mistake')
@commands.has_any_role("Right Hand", "Guild Leader", "God of Bots", "Officer")
async def reset(ctx):
    mydb = create_connection()
    cursor = mydb.cursor()

    sql = "UPDATE users SET estimatedTotal = %s"
    val = (0)
    cursor.execute(sql, val)

    sql = "UPDATE users SET NUMBEROFPEOPLE = %s"
    val = (0)
    cursor.execute(sql, val)

    await ctx.send("The Split has been reset!")

    cursor.close()
    mydb.close()



# Show Loot Owed to You as a member
@bot.command(name = 'bal', help = 'Check your Silver Owed')
async def check(ctx):
    mydb = create_connection()
    cursor = mydb.cursor()


    player = ctx.message.author.display_name

    guild_id = ctx.author.guild.id
    guild = bot.get_guild(guild_id)
    guild_people = ([people.display_name for people in guild.members])

    # Check if mmeber is in the server then convert tuple to string and print result
    try:
        if player in guild_people:
            cursor.execute("SELECT NICKNAME, SILVER FROM users WHERE NICKNAME = %s", ((player,)))
            row = cursor.fetchone()
            silver = int(row[1])
            nickname = str(row[0])
            silver = "{:,}".format(int(silver))
            
            await ctx.send('User**:** ' + nickname + ' **:** Silver**:** ' + silver)
        else:
            await ctx.send(player + " is not in the Discord server!")
    except:
        await ctx.send("Error! " + player + " is not in the Database!")

    cursor.close()
    mydb.close()


# Check another players loot
@bot.command(name='check', help='Check a player\'s silver owed')
async def check(ctx, *args):
    player = ' '.join(args)

    mydb = create_connection()
    cursor = mydb.cursor()

    guild_id = ctx.author.guild.id
    guild = bot.get_guild(guild_id)
    guild_people = [people.display_name for people in guild.members]

    try:
        if player in guild_people:
            cursor.execute('SELECT NICKNAME, SILVER FROM users WHERE NICKNAME = %s', ((player,),))
            row = cursor.fetchone()
            silver = int(row[1])
            nickname = str(row[0])
            silver = '{:,}'.format(int(silver))
            
            await ctx.send('User**:** ' + nickname + ' **:** Silver**:** ' + silver)
        else:
            await ctx.send(player + ' is not in the Discord server!')
    except:
        await ctx.send('Error! ' + player + ' is not in the Database!')

    cursor.close()
    mydb.close()

# Add silver to players balance
@bot.command(name='+figure', help='Add money directly to a player\'s silver')
@commands.has_any_role('Right Hand', 'Guild Leader', 'God of Bots', 'Officer')
async def addSilver(ctx, *args):
    player = ' '.join(args[:-1])
    silver = args[-1]

    mydb = create_connection()
    cursor = mydb.cursor()

    guild_id = ctx.author.guild.id
    guild = bot.get_guild(guild_id)
    guild_people = [people.display_name for people in guild.members]

    try:
        if player in guild_people:
            sql = 'UPDATE users SET SILVER = SILVER + %s WHERE NICKNAME = %s'
            mydb.ping()
            cursor.execute(sql, (silver, player))
            silver = '{:,}'.format(int(silver))
            await ctx.send(silver + ' silver was added to ' + player + '\'s balance.')
        else:
            await ctx.send(player + ' is not in the Discord server!')
    except:
        await ctx.send('Error updating the silver balance of ' + player + '!')

    cursor.close()
    mydb.close()

# Remove silver from players balance
@bot.command(name='-figure', help='Remove money directly from a player\'s silver')
@commands.has_any_role('Right Hand', 'Guild Leader', 'God of Bots', 'Officer')
async def removeSilver(ctx, *args):
    player = ' '.join(args[:-1])
    silver = args[-1]

    mydb = create_connection()
    cursor = mydb.cursor()

    guild_id = ctx.author.guild.id
    guild = bot.get_guild(guild_id)
    guild_people = [people.display_name for people in guild.members]

    try:
        if player in guild_people:
            sql = 'UPDATE users SET SILVER = SILVER - %s WHERE NICKNAME = %s'
            mydb.ping()
            cursor.execute(sql, (silver, player))
            silver = '{:,}'.format(int(silver))
            await ctx.send(player + ' had ' + silver + ' silver removed!')
        else:
            await ctx.send(player + ' is not in the Discord server!')
    except:
        await ctx.send('Error updating the silver balance of ' + player + '!')

    cursor.close()
    mydb.close()


# Check for perms in discord server
@bot.command(name = 'perms', help = 'Check if discord members have perms')
@commands.has_any_role("Right Hand", "Guild Leader", "God of Bots")
async def perms(ctx):
    member = discord.utils.find(lambda r: r.name == 'Member', ctx.message.guild.roles)
    ally = discord.utils.find(lambda r: r.name == 'Guild Ally', ctx.message.guild.roles)
    friendFamily = discord.utils.find(lambda r: r.name == 'Guild Friend / Family', ctx.message.guild.roles)   
    bots = discord.utils.find(lambda r: r.name == 'Bots', ctx.message.guild.roles)
    guild_id = ctx.author.guild.id
    guild = bot.get_guild(guild_id)
    guild_people = ([people.display_name for people in guild.members])    
    for user in ctx.guild.members:
        if (member not in user.roles) and (ally not in user.roles) and (friendFamily not in user.roles) and (bots not in user.roles):
            await ctx.send(f"{user.mention} does not have one of the {member.mention}, {ally.mention}, or {friendFamily.mention} roles.")

    
# Check total silver owed to guild members
@bot.command(name='total', help='Prints each iteration of the SILVER row before adding them up')
@commands.has_any_role("Right Hand", "Guild Leader", "God of Bots", "Officer")
async def total(ctx):
    mydb = create_connection()
    cursor = mydb.cursor()

    try:
        cursor.execute('SELECT SILVER FROM users WHERE SILVER > 0 ORDER BY SILVER DESC')
        silver_rows = cursor.fetchall()
        silver_total = 0
        
        for row in silver_rows:
            silver = int(row[0])
            silver_total += silver
            
        silver_total = '{:,}'.format(silver_total)
        await ctx.send('Total Silver Owed: ' + silver_total)
    except:
        print('Error! Could not retrieve silver rows!')

    cursor.close()
    mydb.close()

# Test if online
@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))



# Run bot
if __name__ == "__main__" :
    bot.run(TOKEN)