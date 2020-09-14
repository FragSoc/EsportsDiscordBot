import json
import discord
from discord.ext import tasks, commands
from discord.utils import get

TOKEN = **Add token here**

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

@client.event
async def on_voice_state_update(member, before, after):
    if after.channel != None:
        # They have moved to a VC
        joinedChannelGuildID = str(after.channel.guild.id)
        joinedChannelCatID = str(after.channel.category_id)
        joinedChannelID = str(after.channel.id)
        #print(f'GuildID: {joinedChannelGuildID} CatID: {joinedChannelCatID} ChannelID: {joinedChannelID}')
        try:
            if voiceMaster.get(joinedChannelGuildID).get(joinedChannelCatID) == joinedChannelID:
                # The channel is a VM channel
                channelName = f"{member.display_name}'s channel"
                newChannel = await member.guild.create_voice_channel(channelName, category=after.channel.category)
                created_vc_channels.append(newChannel.id)
                await member.move_to(newChannel)
        except:
            print(f"{member.display_name} moved to not a VM channel")

    else:
        # They have just left a channel
        if (before.channel.id in created_vc_channels) and (before.channel.members == []):
            await before.channel.delete()
        else:
            print(f"{member.display_name} was not in a VM channel")

#############################################################################################################################################################

@client.command()
async def addVM(ctx, givenVCId):
    try:
        voiceMaster[ctx.author.guild.id]
    except:
        voiceMaster[ctx.author.guild.id] = {'loggingChannel' : None}

    try:
        categoryID = client.get_channel(int(givenVCId)).category_id
        voiceMaster[ctx.author.guild.id].update({categoryID : givenVCId})
        with open('savedVMs.json', 'w') as fp:
                json.dump(voiceMaster, fp)
        await ctx.channel.send(f"{ctx.author.mention}, made that VC into a VoiceMaster VC")

    except:
        await ctx.channel.send(f"{ctx.author.mention}, are you sure that's the correct ID?")


client.run(TOKEN)
