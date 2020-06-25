import os
import discord
import security_camera
import secrets

TOKEN = secrets.BOT_TOKEN
GUILD = secrets.GUILD

# webhook for push notifications
WEBHOOK_ID = secrets.WEBHOOK_ID
WEBHOOK_TOKEN = secrets.WEBHOOK_TOKEN

client = discord.Client()
# Create webhook
webhook = discord.Webhook.partial(WEBHOOK_ID, WEBHOOK_TOKEN, adapter=discord.RequestsWebhookAdapter())

guild = None
channel = None
ready = False

def send(msg):
    webhook.send(msg)

def sendFile(filePath):
    webhook.send(file=discord.File(filePath))

@client.event
async def on_message(message):
    print('got message', message)
    if message.author == client.user:
        return

    if message.content.lower() == 'live':
        await message.channel.send(security_camera.LINK)
    
    if message.content.lower() == 'link':
        await message.channel.send(security_camera.WEBSITE)

    elif message.content.lower() == 'last':
        mostRecentFile = security_camera.getMostRecentImage()
        if mostRecentFile != None:
            await message.channel.send(file=discord.File(mostRecentFile))
    elif message.content.lower() == 'now':
        await message.channel.send(file=discord.File(security_camera.getNow()))
    elif message.content.lower() == 'videos':
        videos = security_camera.getVideosFromToday()
        if len(videos) == 0:
            await message.channel.send('Sorry, there aren\'t any videos from today.')
        else:
            await message.channel.send('Sending over the videos from today')
            for video in videos:
                try:
                    await message.channel.send(file=discord.File(video))
                except:
                    await message.channel.send('Couldn\t\'t send video file, it was too large')
                    return
            await message.channel.send('That should be all the videos!')
    elif message.content.lower() == 'help':
        message.channel.send(' live\n link\n last\n now\n videos')
    # TODO: clear (different folders or all), get videos, logs


@client.event
async def on_ready():
    global guild, channel, ready
    for g in client.guilds:
        if g.name == GUILD:
            guild = g

    for c in guild.text_channels:
        if c.name == secrets.CHANNEL:
            channel = c

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    print(guild.members)

    #await channel.send('RabbitBot has started')
    ready = True



client.run(TOKEN)