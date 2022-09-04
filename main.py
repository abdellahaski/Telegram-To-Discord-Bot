from telethon import TelegramClient, events
import aiohttp
import nextcord
import textwrap
import os
import requests
import json
import json5
import random
import validators
from dotenv import load_dotenv

load_dotenv()

path = os.path.join(os.path.dirname(__file__), 'config.json5')
with open(path) as fp:
  config = json5.load(fp)

#print(json5.dumps(config))
appid = os.environ.get("APPID")
apihash = os.environ.get("APIHASH")
apiname = os.environ.get("APINAME")
dlloc = os.environ.get("DLLOC")
text_to_prepend=os.environ.get("TEXT_TO_PREPEND")

channels_avatars={}

#if input_channels_entities is not None:
#  input_channels_entities = list(map(int, input_channels_entities.split(',')))
input_channels_entities=[]
for channel in config:
  input_channels_entities.append(int(channel["TGchannelID"]))


  
async def imgurimg(mediafile): # Uploads image to imgur
    url = "https://api.imgur.com/3/upload"

    payload = {
    'type': 'file'}
    files = [
    ('image', open(mediafile, 'rb'))
    ]
    headers = {
    'Authorization': str(random.randint(1,10000000000))
    }
    response = requests.request("POST", url, headers=headers, data = payload, files = files)
    return(json.loads(response.text))

async def imgur(mediafile): # Uploads video to imgur
    url = "https://api.imgur.com/3/upload"

    payload = {'album': 'ALBUMID',
    'type': 'file',
    'disable_audio': '0'}
    files = [
    ('video', open(mediafile,'rb'))
    ]
    headers = {
    'Authorization': str(random.randint(1,10000000000))
    }
    response = requests.request("POST", url, headers=headers, data = payload, files = files)
    return(json.loads(response.text))

def start():
    client = TelegramClient(apiname, 
                            appid, 
                            apihash)
    client.start()
    print('Started')
    print('Listenning to the following Telegram Channels: '+str(input_channels_entities))
    
    @client.on(events.NewMessage(chats=input_channels_entities))
    async def handler(event):
      channelID=str(event.chat.id)
      for channel in config:
        if str(channel["TGchannelID"]) == channelID:
          senderAvatarUrl=channel["senderAvatarUrl"]
          senderName=channel["senderName"]
          DiscordWebhooks=channel["discordWebhooks"]
        
      if DiscordWebhooks is None:
        print('channel (id:'+channelID+') not configured correctly, please check the config.json5 file')  
        return

      if not senderName or senderName is None or senderName=='':
        senderName=event.chat.title
        
      if(senderAvatarUrl is not None and validators.url(senderAvatarUrl)):
        channels_avatars[channelID]=senderAvatarUrl
        channelAvatarUrl=senderAvatarUrl
      else:
        #Checking if the channel avatar is already in the avatar list
        if(channelID in channels_avatars):
          channelAvatarUrl=channels_avatars[channelID]
        else: # if not we download it and upload it to imgur (since discord accept only avartar urls)
          channel = await client.get_entity(event.chat.id)
          channelAvatar = await client.download_profile_photo(channel,dlloc, download_big=False)
          channelAvatarUrl=await imgurimg(channelAvatar)
          os.remove(channelAvatar)  
          channelAvatarUrl = channelAvatarUrl['data']['link']
          channels_avatars[channelID]=channelAvatarUrl # we store it on the channels avatars array so we can use it another time without reuploading to imgur

      msg = event.message.message
      #Looking for href urls in the text message and appending them to the message
      try:
        for entity in event.message.entities:
          if ('MessageEntityTextUrl' in type(entity).__name__):
            msg +=f"\n\n{entity.url}" 
      except:
        print("no url captured, forwording message")

      if event.message.media is not None:
          
          if('MessageMediaWebPage' in type(event.message.media).__name__):# directly send message if the media attached is a webpage embed 
            for webhookUrl in DiscordWebhooks:
              await send_to_webhook(msg,senderName,channelAvatarUrl,webhookUrl)
          else:
            dur = event.message.file.duration # Get duration
            if dur is None:
              dur=1 # Set duration to 1 if media has no duration ex. photo
            # If duration is greater than 60 seconds or file size is greater than 200MB
            if dur>60 or event.message.file.size > 209715201: # Duration greater than 60s send link to media
              print('Media too long!')
              msg +=f"\n\nLink to Video: https://t.me/c/{event.chat.id}/{event.message.id}" 
              for webhookUrl in DiscordWebhooks:
                await send_to_webhook(msg,senderName,channelAvatarUrl,webhookUrl)
              return
            else: # Duration less than 60s send media
              path = await event.message.download_media(dlloc)
              for webhookUrl in DiscordWebhooks:
                await pic(path,msg,senderName,channelAvatarUrl,webhookUrl)

              os.remove(path)
      else: # No media text message
          for webhookUrl in DiscordWebhooks:
            await send_to_webhook(msg,senderName,channelAvatarUrl,webhookUrl)
        
    client.run_until_disconnected()

async def pic(filem,message,username,channelAvatarUrl,webhookUrl): # Send media to webhook
    if(text_to_prepend is not None):
      message=text_to_prepend+message
    async with aiohttp.ClientSession() as session:
        print('Sending w media')
        webhook = nextcord.Webhook.from_url(webhookUrl, session=session)
        try: # Try sending to discord
          f = nextcord.File(filem)
          await webhook.send(file=f,username=username,avatar_url=channelAvatarUrl)
        except: # If it fails upload to imgur
          print('File too big, uploading to imgur')
          try:
            image = await imgur(filem) # Upload to imgur
            #print(image)
            image = image['data']['link']
            print(f'Imgur: {image}') 
            await webhook.send(content=image,username=username,avatar_url=channelAvatarUrl) # Send imgur link to discord
          except Exception as ee:
            print(f'Error {ee.args}') 
        for line in textwrap.wrap(message, 2000, replace_whitespace=False): # Send message to discord
            await webhook.send(content=line,username=username,avatar_url=channelAvatarUrl) 

async def send_to_webhook(message,username,channelAvatarUrl,webhookUrl): # Send message to webhook
    if(text_to_prepend is not None):
      message=text_to_prepend+message
    async with aiohttp.ClientSession() as session:
        print('Sending w/o media')
        webhook = nextcord.Webhook.from_url(webhookUrl, session=session)
        for line in textwrap.wrap(message, 2000, replace_whitespace=False): # Send message to discord
            await webhook.send(content=line,username=username,avatar_url=channelAvatarUrl)

if __name__ == "__main__":
    start()