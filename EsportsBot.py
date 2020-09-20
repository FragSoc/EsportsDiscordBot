import json
import discord
from discord.ext import tasks, commands
from discord.utils import get

TOKEN = 'NzIyMjAxNDY1MTgzMjczMDQy.Xufo9Q.bPKsAuZJRG7IlhPDAJNit35UxKk'

client = commands.Bot(command_prefix = '.')
client.remove_command('help')

created_vc_channels = []

# Open JSON file and retrieve dictionary or create it
try:
    with open('savedVMs.json', 'r') as fp:
        voiceMaster = json.load(fp)
except:
    voiceMaster = {}
print(voiceMaster)

@client.event
async def on_ready():
    print('Bot is now active')
    await client.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.listening, name="your commands"))

def sendLoggingMessage(guild_id):
    loggingChannelID = voiceMaster.get(guild_id).get('loggingChannel')
    if loggingChannelID != None:
        loggingChannel = client.get_channel(int(loggingChannelID))
        return loggingChannel


@client.event
async def on_voice_state_update(member, before, after):
    
    if after.channel != None:
        # They have moved to a VC
        joinedChannelGuildID = str(after.channel.guild.id)
        joinedChannelCatID = str(after.channel.category_id)
        joinedChannelID = str(after.channel.id)
        try:
            if voiceMaster.get(joinedChannelGuildID).get(joinedChannelID) == joinedChannelCatID:
                # The channel is a VM channel
                channelName = f"{member.display_name}'s channel"
                newChannel = await member.guild.create_voice_channel(channelName, category=after.channel.category)
                created_vc_channels.append(newChannel.id)
                await member.move_to(newChannel)
                try:
                    await sendLoggingMessage(joinedChannelGuildID).send(f"{member.mention} has created a temp VM")
                except:
                    print("No logging channel set up yet")
        except:
            print(f"{member.display_name} moved to not a VM channel")

    else:
        # They have just left a channel
        if (before.channel.id in created_vc_channels):
            print(f"{member.display_name} was in a VM channel")
            if  (before.channel.members == []):
                await before.channel.delete()
                try:
                    await sendLoggingMessage(str(before.channel.guild.id)).send(f"Temp VC has been deleted")
                except:
                    print("No logging channel set up yet")
        else:
            print(f"{member.display_name} was not in a VM channel")

#############################################################################################################################################################

@client.command()
async def addVM(ctx, givenVCId):
    try:
        voiceMaster[str(ctx.author.guild.id)]
    except:
        voiceMaster[str(ctx.author.guild.id)] = {'loggingChannel' : None}

    try:
        categoryID = client.get_channel(int(givenVCId)).category_id
        voiceMaster[str(ctx.author.guild.id)].update({givenVCId: str(categoryID)})
        with open('savedVMs.json', 'w') as fp:
            json.dump(voiceMaster, fp)
        await ctx.channel.send(f"{ctx.author.mention}, made that VC into a VoiceMaster VC")
        try:
            await sendLoggingMessage(str(ctx.author.guild.id)).send(f"{ctx.author.mention} made {givenVCId} a VM master")
        except:
            print("No logging channel set up yet")

    except:
        await ctx.channel.send(f"{ctx.author.mention}, are you sure that's the correct ID?")


@client.command()
async def removeVM(ctx, givenVCId):
    try:
        voiceMaster[str(ctx.author.guild.id)]
        del voiceMaster[str(ctx.author.guild.id)][givenVCId]
        with open('savedVMs.json', 'w') as fp:
                json.dump(voiceMaster, fp)
        await ctx.channel.send(f"{ctx.author.mention}, removed that VC from VoiceMaster")
        try:
            await sendLoggingMessage(str(ctx.author.guild.id)).send(f"{ctx.author.mention} removed the {givenVCId} VM master")
        except:
            print("No logging channel set up yet")
    except:
        await ctx.channel.send(f"{ctx.author.mention}, a VC does not exist with that ID")

@client.command()
async def setLog(ctx, givenChannelId):
    try:
        voiceMaster[str(ctx.author.guild.id)]
    except:
        voiceMaster[str(ctx.author.guild.id)] = {'loggingChannel' : None}

    try:
        voiceMaster[str(ctx.author.guild.id)].update({"loggingChannel": str(givenChannelId)})
        with open('savedVMs.json', 'w') as fp:
            json.dump(voiceMaster, fp)
        await ctx.channel.send(f"{ctx.author.mention}, logging channel set")
        try:
            await sendLoggingMessage(str(ctx.author.guild.id)).send(f"{ctx.author.mention} set the logging channel to {givenChannelId}")
        except:
            print("No logging channel set up yet")
    except:
        await ctx.channel.send(f"{ctx.author.mention}, a text channel does not exist with that ID")

client.run(TOKEN)
