import json
import discord
from discord.ext import tasks, commands
from discord.utils import get

TOKEN = ''

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

    if before.channel != None:
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
@commands.has_permissions(manage_messages=True)
async def help(ctx):
    embed = discord.Embed(
        title="Available admin commands",
        description="The list of available commands are:",
        color=0xFCAF17
    )
    embed.set_author(name='Help')
    embed.add_field(name='__**.setLog**__', value="Sets the log channel for the server from the given channe ID", inline=False)
    embed.add_field(name='__**.addVM**__', value="When given a channel ID makes it a VoiceMaster master channel", inline=False)
    embed.add_field(name='__**.removeVM**__', value="Removes the given master channel ID from VoiceMaster", inline=False)
    embed.add_field(name='__**.listVMs**__', value="Lists all the current VoiceMaster master channels", inline=False)
    embed.add_field(name='__**.clearVMs**__', value="Removes all the VoiceMaster master channels", inline=False)
    embed.add_field(name='__**.clear**__', value="Clears the specified number of message from the current channel (default is 5)", inline=False)
    
    await ctx.send(embed=embed)
    try:
        await sendLoggingMessage(str(ctx.author.guild.id)).send(f"{ctx.author.mention} issued a .help command")
    except:
        print("No logging channel set up yet")

@client.command()
@commands.has_permissions(manage_messages=True)
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
@commands.has_permissions(manage_messages=True)
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
@commands.has_permissions(manage_messages=True)
async def listVMs(ctx):
    try:
        vmChannels = ".\n__**Known VM channels in this server**__"
        for ChannelID, CatID in voiceMaster[str(ctx.author.guild.id)].items():
            if ChannelID != "loggingChannel":
                vmChannels += "\n"
                vmChannels += (f"'{client.get_channel(int(ChannelID)).name}' in the '{client.get_channel(int(CatID)).name}' category")
            else:
                vmChannels += "\n**Logging channel**\n"
                vmChannels += (f"'{client.get_channel(int(CatID)).name}' in the '{client.get_channel(client.get_channel(int(CatID)).category_id).name}' category")
                vmChannels += "\n**VoiceMaster channels**"
        await ctx.channel.send(vmChannels)
    except:
        print("Error")


@client.command()
@commands.has_permissions(manage_messages=True)
async def clearVMs(ctx):
    try:
        currentLog = voiceMaster[str(ctx.author.guild.id)].get("loggingChannel")
        voiceMaster.update({str(ctx.author.guild.id) : {"loggingChannel" : str(currentLog)}})
        with open('savedVMs.json', 'w') as fp:
            json.dump(voiceMaster, fp)
        await ctx.channel.send(f"{ctx.author.mention}, all VoiceMaster masters have been removed")
        try:
            await sendLoggingMessage(str(ctx.author.guild.id)).send(f"{ctx.author.mention} has removed all VM masters")
        except:
            print("No logging channel set up yet")
    except:
        print("Error")


@client.command()
@commands.has_permissions(manage_messages=True)
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

#############################################################################################################################################################
# General admin commands stolen from old bot

@client.command(aliases=['cls', 'purge', 'delete', 'Cls', 'Purge', 'Delete', 'Clear'])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5):
    await ctx.channel.purge(limit=int(amount)+1)
    try:
        await sendLoggingMessage(str(ctx.author.guild.id)).send(f'**{ctx.message.author.name}** issued a **.clear** command for {amount} message(s) in {ctx.message.channel.mention}')
    except:
        print("No logging channel set up yet")


@client.command(aliases=['Members'])
@commands.has_permissions(manage_messages=True)
async def members(ctx):
    #print(ctx.message.guild.members)
    memberList = []
    memberCount = ctx.message.guild.member_count
    for each in (ctx.message.guild.members):
        if each.bot == False:
            memberList.append(each.name)
        else:
            memberCount -= 1
    await ctx.send(f"{memberCount} members: {memberList}")
    try:
        await sendLoggingMessage(str(ctx.author.guild.id)).send(f'**{ctx.message.author.name}** issued a **.members** command in {ctx.message.channel.mention}')
    except:
        print("No logging channel set up yet")

#############################################################################################################################################################


client.run(TOKEN)
