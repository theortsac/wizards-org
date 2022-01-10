# region Imports
from nextcord.ext import commands, menus
import nextcord
import os
import emoji
from dotenv import load_dotenv
from pymongo import MongoClient
import pymongo
import asyncio
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix="/",
                   case_insensitive=True, intents=intents, help_command=None)
client = MongoClient()
load_dotenv()
token = os.getenv('TOKEN')
username = os.getenv('MONGO_USER')
password = os.getenv('PASSWORD')
mongoClient = pymongo.MongoClient(f"mongodb://{username}:{password}@localhost")
db = mongoClient.WizardsGuild
# endregion

# region Help Command

# Get all the embeds

helpEmbeds = [
    {
        "Emoji": '❔',
        "Name": "Help Command",
        "Description": "It's this command! It shows all the commands and how to use them.",
        "Command": "/help"
    },
    {
        "Emoji": '📚',
        "Name": "Check Wizard Command",
        "Description": "It shows the details of any registered wizard, you need to inform it's Wizard Id, which is just a number.",
        "Command": "/wizard {wizard_id}"
    },
    {
        "Emoji": '🪄',
        "Name": "Magic Types Command",
        "Description": "See all the basic magic types.",
        "Command": "/types"
    },
    {
        "Emoji": '📜',
        "Name": "Register Command",
        "Description": "Register and become a real wizard! You will have your own wizard profile on the server.",
        "Command": "/register"
    },
    {
        "Emoji": '🏆',
        "Name": "Ranking Command",
        "Description": "Check the top 5 wizards with the biggest levels on the server.",
        "Command": "/ranking"
    },
    {
        "Emoji": '📛',
        "Name": "Id Command",
        "Description": "Check the Id of your registered wizard.",
        "Command": "/id"
    },
    {
        "Emoji": '🔄',
        "Name": "Update Command",
        "Description": "Update your wizard information.",
        "Command": "/update {what_you_want_to_update}"
    }

]

help_embed = nextcord.Embed(
    title=":white_check_mark: Here's an explanation of each command:", color=0x87CEEB)

for x in helpEmbeds:
    help_embed.add_field(
        name=f"{x['Emoji']} {x['Name']}", value=f"{x['Description']}\nHow to use: {x['Command']}", inline=False)


@bot.command()
@commands.cooldown(1, 30, commands.BucketType.user)
async def help(ctx):
    await ctx.reply(embed=help_embed)
# endregion

# region Confirm View


class Confirm(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @ nextcord.ui.button(label='Confirm', style=nextcord.ButtonStyle.green)
    async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Accepted!", color=0x00FF00)
        await interaction.message.edit("", embed=embed, view=None)
        self.value = True
        self.stop()

    @ nextcord.ui.button(label='Cancel', style=nextcord.ButtonStyle.red)
    async def cancel(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Refused.", color=0xFF0000)
        await interaction.message.edit("", embed=embed, view=None)
        self.value = False
        self.stop()
# endregion

# region Magic Type Dropdown


class MagicType(nextcord.ui.Select):
    def __init__(self):

        # Set the options that will be presented inside the dropdown
        options = [
            nextcord.SelectOption(
                label='Light', description='Light Magic Type', emoji='💡'),
            nextcord.SelectOption(
                label='Darkness', description='Darkness Magic Type', emoji='🕶️'),
            nextcord.SelectOption(
                label='Fire', description='Fire Magic Type', emoji='🔥'),
            nextcord.SelectOption(
                label='Water', description='Water Magic Type', emoji='🌊'),
            nextcord.SelectOption(
                label='Earth', description='Earth Magic Type', emoji='🪨'),
            nextcord.SelectOption(
                label='Wind', description='Wind Magic Type', emoji='🌪️')
        ]

        super().__init__(placeholder='Say your magic type...',
                         min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.message.edit("", embed=nextcord.Embed(title="Type chosen!", color=0x00ff00), view=None)
        self.view.stop()


# endregion

# region Embed Basic Magic Function


def embedBasicMagics(title):
    embedBasicMagic = nextcord.Embed(
        title=title, color=0xFFFF00)
    embedBasicMagic.add_field(name="💡 Light",
                              value="Light is one of the essential elements for the world, with this power you can control how the light behaves. Is also correlated to the good, can make miracles if the power is very big.", inline=False)
    embedBasicMagic.add_field(name="🕶️️ Darkness",
                              value="You can control how the darkness works, becoming a true master of the shadows. Is correlated with the evil, but not necessarily all the darkness wizards are evil, the power has lots of possibilities in a high level.", inline=False)
    embedBasicMagic.add_field(name="🔥 Fire",
                              value="The fire is a vital element in the whole multiverse, with this power you can control it in almost any shape or form.", inline=False)
    embedBasicMagic.add_field(name="🌊 Water",
                              value="You're almost a god in the water, being able to make it do as you wish, lots of branches when in a high level.", inline=False)
    embedBasicMagic.add_field(name="🪨 Earth",
                              value="Can control the earth and stones, has a very powerful brute attack, so if used with the proper martial arts is amazingly good.", inline=False)
    embedBasicMagic.add_field(name="🌪️ Wind",
                              value="Very fast and versatile, it's very hard to learn how to control, but if the wizard manage to do so he will be very powerful.", inline=False)
    return embedBasicMagic
# endregion

# region Connect Print


@ bot.event
async def on_ready():
    print("Connected.")
# endregion

# region Function Float Point


def afterPoint(x):
    return int(x*100 % 100)

# endregion

# region Create Wizard Embed


def createEmbed(WizardName, found, avatar):
    if (found == None):
        return nextcord.Embed(title="This wizard doesn't exist.", color=0xFF0000)
    else:
        # Get the magic type info
        magicInfo = db.wizardsData.find_one({"_id": "MagicTypes"})
        magicInfo = magicInfo[found["MagicType"]]
        # Create embed
        embed = nextcord.Embed(
            title=f"{found['Emoji']} {found['Name']}", color=int(magicInfo["Color"], 16))
        # Say magic type
        embed.add_field(name=magicInfo["Emoji"] + " Magic Type",
                        value=found["MagicType"], inline=False)
        # Handle owner
        embed.add_field(name="👑 Owner", value=WizardName, inline=False)
        # Handle description
        embed.add_field(name="📔 Description",
                        value=found["Description"], inline=False)
        # Handle Level
        currentLevel = found["ExperiencePoints"] / 100
        embed.add_field(name="🔋 Level",
                        value=f"{int(currentLevel)} ~ {afterPoint(currentLevel)}%", inline=False)
        # Handle Id
        embed.add_field(name="🆔 Identification Number",
                        value=found["WizardId"], inline=False)
        # add the image
        embed.set_thumbnail(url=avatar)
        return embed

# endregion

# region Wizard Command


@ bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def wizard(ctx, *, WizardId):
    try:
        found = db["wizardsData"].find_one({'WizardId': int(WizardId)})
        user = bot.get_user(found['_id'])
        await ctx.reply(embed=createEmbed(str(user), found, user.display_avatar.url))
    except:
        await ctx.reply(embed=nextcord.Embed(
            title="This Wizard doesn't exist.", color=0xFF0000))
# endregion

# region type Command


@ bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def types(ctx):
    await ctx.reply(embed=embedBasicMagics("🧙 These are the basic magic types:"))
# endregion

# region Register


@ bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def register(ctx):
    # check if the id already exists
    if (db["wizardsData"].find_one({'_id': ctx.author.id}) != None):
        await ctx.reply(embed=nextcord.Embed(
            title="You are already registered.", color=0xFF0000))
        return
    try:
        # ask if he really wants to register
        view = Confirm()
        await ctx.author.send(embed=nextcord.Embed(title="Hello! I'm the Wizards' Guild clerk, do you want to register and become a real wizard?", color=0xFFFF00), view=view)
    except:
        # say if we can't send a message to him
        await ctx.reply(embed=nextcord.Embed(
            title="Can't send a message to the you!", color=0xFF0000))
        return
    await view.wait()
    # If there is no answer
    if view.value == None:
        await ctx.reply(embed=nextcord.Embed(title="Timed Out! Answer quicker next time.", color=0xFF0000))
        return
    # If the answer is no
    elif view.value == False:
        return
    # Ask to choose the magic type
    view = MagicType()
    message_view = nextcord.ui.View()
    message_view.add_item(view)
    await ctx.author.send(embed=embedBasicMagics("What's the type of your magic?"), view=message_view)
    await message_view.wait()
    # If there is no answer
    if view.values is None:
        await ctx.reply(embed=nextcord.Embed(title="Timed Out! Answer quicker next time.", color=0xFF0000))
        return
    # Store the MagicType
    type = view.values[0]
    playerData = {"_id": ctx.author.id, "MagicType": type}

    await ctx.author.send(embed=nextcord.Embed(title="Now say your name. (Just send it here, the limit is 30 characters. You have 2 minutes.)", color=0xFFFF00))
    try:
        msg = await bot.wait_for('message', check=lambda x: x.channel == ctx.author.dm_channel and x.author == ctx.author, timeout=120)
    except asyncio.TimeoutError:
        await ctx.reply(embed=nextcord.Embed(title="Timed Out! Answer quicker next time.", color=0xFF0000))
        return
    if (len(msg.content) > 30):
        await ctx.author.send(
            "The name is too long, use the command to register again.")
        return
    playerData.update({"Name": msg.content})
    await ctx.author.send(embed=nextcord.Embed(title="Time to say your description. (Send it here, maximum of 140 characters. You have 5 minutes.)", color=0xFFFF00))
    try:
        msg = await bot.wait_for('message', check=lambda x: x.channel == ctx.author.dm_channel and x.author == ctx.author, timeout=300)
    except asyncio.TimeoutError:
        await ctx.reply(embed=nextcord.Embed(title="Timed Out! Answer quicker next time.", color=0xFF0000))
        return

    if (len(msg.content) > 140):
        await ctx.author.send(
            "The description is too long. Use the command again.")
        return
    playerData.update({"Description": msg.content})
    # do the emoji stuff
    await ctx.author.send(embed=nextcord.Embed(title="Send a message with an emoji that represent you as a wizard. (It needs to be a default emoji, you have 2 minutes.)", color=0xFFFF00))
    try:
        msg = await bot.wait_for('message', check=lambda x: x.channel == ctx.author.dm_channel and x.author == ctx.author, timeout=120)
    except asyncio.TimeoutError:
        await ctx.reply(embed=nextcord.Embed(title="Timed Out! Answer quicker next time.", color=0xFF0000))
        return
    emoji_list = emoji.emoji_lis(msg.content)
    if (len(emoji_list) == 0):
        await ctx.author.send(embed=nextcord.Embed(title="No emoji in the message, try registering again with the command.", color=0xFF0000))
        return
    elif (len(emoji_list) > 1):
        await ctx.author.send(embed=nextcord.Embed(title="More than one emoji in the message, try registering again with the command.", color=0xFF0000))
        return
    elif (len(emoji_list) == 1):
        playerData.update({"Emoji": emoji_list[0]['emoji']})
    # end it all
    WizardId = db["wizardsData"].find_one({'_id': "currentId"})["idNumber"]
    playerData.update({"WizardId": WizardId, "ExperiencePoints": 0})
    try:
        db["wizardsData"].insert_one(playerData)
    except:
        await ctx.author.send("Error")
        return
    db["wizardsData"].update_one({"_id": "currentId"}, {
        '$inc': {"idNumber": 1}})
    await ctx.author.add_roles(ctx.guild.get_role(db.wizardsData.find_one({"_id": "MagicTypes"})[type]["Id"]))
    await ctx.author.send(embed=nextcord.Embed(title=f"Congratulations! You are successfully registered! To check your information, use in the server: /wizard {WizardId}", color=0x00FF00))
    await ctx.send(f"`New wizard registered!`", embed=createEmbed(str(ctx.author), db["wizardsData"].find_one({'WizardId': WizardId}), ctx.author.display_avatar.url))
# endregion

# region Ranking Command


@ bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def ranking(ctx):
    top5 = db.wizardsData.find().sort("ExperiencePoints", -1).limit(5)
    embed = nextcord.Embed(
        title=":mage: Top 5 best wizards! :mage:", color=0x87CEEB)
    position = 1
    for x in top5:
        if 'ExperiencePoints' in x.keys():
            currentLevel = x['ExperiencePoints'] / 100
            if position == 1:
                embed.add_field(
                    name="🥇 - "+x["Name"], value=f"Level {int(currentLevel)} ~ {afterPoint(currentLevel)}%", inline=False)
            if position == 2:
                embed.add_field(
                    name="🥈 - "+x["Name"], value=f"Level {int(currentLevel)} ~ {afterPoint(currentLevel)}%", inline=False)
            if position == 3:
                embed.add_field(
                    name="🥉 - "+x["Name"], value=f"Level {int(currentLevel)} ~ {afterPoint(currentLevel)}%", inline=False)
            if position > 3:
                embed.add_field(
                    name=str(position) + "° - "+x["Name"], value=f"Level {int(currentLevel)} ~ {afterPoint(currentLevel)}%", inline=False)
            position += 1
        else:
            continue
    embed.set_footer(
        text="Congrats to everyone! You are awesome!", icon_url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/282/fire_1f525.png")
    await ctx.reply(embed=embed)
# endregion

# region ID Command


@ bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def id(ctx):
    found = db.wizardsData.find_one({'_id': ctx.author.id})
    if found == None:
        await ctx.reply(embed=nextcord.Embed(
            title="You aren't registered! (Use /register)", color=0xFF0000))
        return
    else:
        await ctx.reply(embed=nextcord.Embed(
            title=f"Your Wizard Id is: {found['WizardId']}!", color=0x00FF00))
        return

# endregion

# region XP Command


@ bot.command()
@ commands.has_guild_permissions(manage_messages=True)
async def xp(ctx, user: nextcord.Member, *, xp):
    db["wizardsData"].update_one(
        {"_id": user.id}, {'$inc': {"ExperiencePoints": int(xp)}})
    await ctx.reply("Done!")
# endregion

# region On cooldown error


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(embed=nextcord.Embed(
            title=f'This command is on cooldown, you can use it in {round(error.retry_after, 2)} seconds!', color=0xFF0000))
# endregion

# region Update Command


@ bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def update(ctx, *, WhatUpdate):
    if (db["wizardsData"].find_one({'_id': ctx.author.id}) == None):
        ctx.reply("You aren't a registered wizard.")
        return
    # UPDATE NAME
    if (WhatUpdate == "name"):
        try:
            # ask if he really wants to register
            view = Confirm()
            await ctx.author.send(embed=nextcord.Embed(title="Are you sure you want to change your name?", color=0xFFFF00), view=view)
        except:
            # say if we can't send a message to him
            await ctx.reply(embed=nextcord.Embed(
                title="Can't send a message to the you!", color=0xFF0000))
            return
        await view.wait()
        # If there is no answer
        if view.value == None:
            await ctx.reply(embed=nextcord.Embed(title="Timed Out! Answer quicker next time.", color=0xFF0000))
            return
        # If the answer is no
        elif view.value == False:
            return
        # If the value is yes
        await ctx.author.send(embed=nextcord.Embed(title="Now say your name. (Just send it here, the limit is 30 characters. You have 2 minutes.)", color=0xFFFF00))
        try:
            msg = await bot.wait_for('message', check=lambda x: x.channel == ctx.author.dm_channel and x.author == ctx.author, timeout=120)
        except asyncio.TimeoutError:
            await ctx.reply(embed=nextcord.Embed(title="Timed Out! Answer quicker next time.", color=0xFF0000))
            return
        if (len(msg.content) > 30):
            await ctx.author.send(
                "The name is too long, use the command to register again.")
            return
        # Update on database
        db.wizardsData.update_one({"_id": ctx.author.id}, {
                                  "$set": {"Name": msg.content}})
        await ctx.author.send(embed=nextcord.Embed(title="Done! Your information was changed.", color=0x00FF00))
    # UPDATE EMOJI
    elif (WhatUpdate == "emoji"):
        try:
            # ask if he really wants to register
            view = Confirm()
            await ctx.author.send(embed=nextcord.Embed(title="Are you sure you want to change your emoji?", color=0xFFFF00), view=view)
        except:
            # say if we can't send a message to him
            await ctx.reply(embed=nextcord.Embed(
                title="Can't send a message to the you!", color=0xFF0000))
            return
        await view.wait()
        # If there is no answer
        if view.value == None:
            await ctx.reply(embed=nextcord.Embed(title="Timed Out! Answer quicker next time.", color=0xFF0000))
            return
        # If the answer is no
        elif view.value == False:
            return
        # If the value is yes
        await ctx.author.send(embed=nextcord.Embed(title="Send a message with an emoji that represent you as a wizard. (It needs to be a default emoji, you have 2 minutes.)", color=0xFFFF00))
        try:
            msg = await bot.wait_for('message', check=lambda x: x.channel == ctx.author.dm_channel and x.author == ctx.author, timeout=120)
        except asyncio.TimeoutError:
            await ctx.reply(embed=nextcord.Embed(title="Timed Out! Answer quicker next time.", color=0xFF0000))
            return
        emoji_list = emoji.emoji_lis(msg.content)
        if (len(emoji_list) == 0):
            await ctx.author.send(embed=nextcord.Embed(title="No emoji in the message, try registering again with the command.", color=0xFF0000))
            return
        elif (len(emoji_list) > 1):
            await ctx.author.send(embed=nextcord.Embed(title="More than one emoji in the message, try registering again with the command.", color=0xFF0000))
            return
        # Update on the database
        elif (len(emoji_list) == 1):
            db.wizardsData.update_one({"_id": ctx.author.id}, {
                "$set": {"Emoji": emoji_list[0]['emoji']}})
            await ctx.author.send(embed=nextcord.Embed(title="Done! Your information was changed.", color=0x00FF00))
    # UPDATE DESCRIPTION
    elif (WhatUpdate == "description"):
        try:
            # ask if he really wants to register
            view = Confirm()
            await ctx.author.send(embed=nextcord.Embed(title="Are you sure you want to change your description?", color=0xFFFF00), view=view)
        except:
            # say if we can't send a message to him
            await ctx.reply(embed=nextcord.Embed(
                title="Can't send a message to the you!", color=0xFF0000))
            return
        await view.wait()
        # If there is no answer
        if view.value == None:
            await ctx.reply(embed=nextcord.Embed(title="Timed Out! Answer quicker next time.", color=0xFF0000))
            return
        # If the answer is no
        elif view.value == False:
            return
        # If the value is yes
        await ctx.author.send(embed=nextcord.Embed(title="Time to say your description. (Send it here, maximum of 140 characters. You have 5 minutes.)", color=0xFFFF00))
        try:
            msg = await bot.wait_for('message', check=lambda x: x.channel == ctx.author.dm_channel and x.author == ctx.author, timeout=300)
        except asyncio.TimeoutError:
            await ctx.reply(embed=nextcord.Embed(title="Timed Out! Answer quicker next time.", color=0xFF0000))
            return
        if (len(msg.content) > 140):
            await ctx.author.send(
                "The description is too long. Use the command again.")
            return
        # Update on database
        db.wizardsData.update_one({"_id": ctx.author.id}, {
                                  "$set": {"Description": msg.content}})
        await ctx.author.send(embed=nextcord.Embed(title="Done! Your information was changed.", color=0x00FF00))
    # UPDATE TYPE OF MAGIC
    elif (WhatUpdate == "magic"):
        try:
            # ask if he really wants to register
            view = Confirm()
            await ctx.author.send(embed=nextcord.Embed(title="**THIS WILL COMPLETELY RESET YOUR LEVEL!** Are you sure you want to change your magic type?", color=0xFFFF00), view=view)
        except:
            # say if we can't send a message to him
            await ctx.reply(embed=nextcord.Embed(
                title="Can't send a message to the you!", color=0xFF0000))
            return
        await view.wait()
        # If there is no answer
        if view.value == None:
            await ctx.reply(embed=nextcord.Embed(title="Timed Out! Answer quicker next time.", color=0xFF0000))
            return
        # If the answer is no
        elif view.value == False:
            return
        # If the value is yes
        view = MagicType()
        message_view = nextcord.ui.View()
        message_view.add_item(view)
        await ctx.author.send(embed=embedBasicMagics("What's the type of your magic?"), view=message_view)
        await message_view.wait()
        # If there is no answer
        if view.values is None:
            await ctx.reply(embed=nextcord.Embed(title="Timed Out! Answer quicker next time.", color=0xFF0000))
            return
        # Update on database
        oldType = db.wizardsData.find_one({'_id': ctx.author.id})["MagicType"]
        db.wizardsData.update_one({"_id": ctx.author.id}, {
                                  "$set": {"MagicType": view.values[0], "ExperiencePoints": 0}})
        await ctx.author.add_roles(ctx.guild.get_role(db.wizardsData.find_one({"_id": "MagicTypes"})[view.values[0]]["Id"]))
        await ctx.author.remove_roles(ctx.guild.get_role(db.wizardsData.find_one({"_id": "MagicTypes"})[oldType]["Id"]))
        await ctx.author.send(embed=nextcord.Embed(title="Done! Your information was changed.", color=0x00FF00))
    else:
        await ctx.reply(embed=nextcord.Embed(title="This information doesn't exist. You can only update the name, emoji, description, or magic.", color=0xFF0000))
# endregion

# region Give 1 XP for each message


@ bot.event
async def on_message(message):
    if (message.channel.id == 910589487812317304 or message.channel.id == 904779755499438101):
        await bot.process_commands(message)
    if (message.channel.id == 907614794020950087 or message.channel.id == 904406637949886494):
        try:
            db["wizardsData"].update_one({"_id": message.author.id}, {
                '$inc': {"ExperiencePoints": 1}})
            return
        except:
            return
# endregion

bot.run(token)
