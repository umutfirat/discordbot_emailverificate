import os
import discord
import random
from discord import Intents
from discord.ext import commands
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import utils
import requests
from sinkaf import Sinkaf

token = "your_token"

def sendUser(discordId, userMail):
    url = "websiteurl"

    data = {
        "discordId" : discordId,
        "userMail" : userMail,
    }

    response = requests.post(url, data=data)

    value = int(response.text)

    if(value == 0):
        return 0
    elif(value == 2):
        return 2
    elif(value == 3):
        return 3

def checkUser(discordId):
    url = "websiteurl"
    data = {
    "discordId" : discordId,
    }
    response = requests.post(url, data=data)
    try:
        result = int(response.text)
    except:
        result = -1
        
    if result == 0:
        return True
    elif result == -1:
        return True
    elif result == 1:
        return False





def sendEmail(email_to, code):
    # E-posta gönderen ve alıcı bilgileri
    email_from = "email"
    email_password = "app_password"
    email_to = email_to
    subject = "subject"
    message = "message:"+code

    # E-posta sunucusuna bağlanma
    smtp_server = "smtp.mailserver.com"
    smtp_port = 587

    try:
        # Bağlantı oluşturma
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        
        # Giriş yapma
        server.login(email_from, email_password)
        
        # E-posta oluşturma
        msg = MIMEMultipart()
        msg['From'] = utils.formataddr(('Name', email_from))
        msg['To'] = email_to
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        
        # E-postayı gönderme
        server.sendmail(email_from, email_to, msg.as_string())
        print("Success Message")
        
    except Exception as e:
        print("Error Message: ", e)
        
    finally:
        # Bağlantıyı kapatma
        server.quit()

def checkUserEmail(userDiscordId):
    url = "websiteurl"

    data = {
        "discordId" : discordId,
    }

    response = requests.post(url, data=data)

    return response.text

load_dotenv()

intents = Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
client = discord.Client(intents=intents)

verification_codes = {}

user_types = {}
snf = Sinkaf(model = "bert_rec")
@client.event
async def on_ready():
    print(f"{client.user} started")
    guild_name = "Your Guild's name"
    channel_name = "Welcome Channel Name"
    message_content = "Your first message"

    #Sunucuyu bul
    guild = discord.utils.get(client.guilds, name=guild_name)

    if guild is not None:
        channel = discord.utils.get(guild.text_channels, name=channel_name)

        if channel is not None:
            async for message in channel.history(limit=None):
                await message.delete()
            sent_message = await channel.send(message_content)
            await sent_message.add_reaction("✅")
    
@client.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == "✅":
        message = f"{user.name}! => asking email for verificate account"
        userid = user.name
        await user.send(message)




def generate_verification_code():
    return str(random.randint(100000, 999999))


@client.event
async def on_message(message):
    global usermail
    if message.author != client.user:
        usercheck = checkUser(message.author.name)

        if usercheck:
            global usermail
            if message.author == client.user:
                return
            
            
            if message.author != client.user:
                cevap = message.content
                if cevap.endswith("email_ext"):
                    usermail = message.content
                    user_id = message.author.id
                    verification_code = generate_verification_code()
                    verification_codes[user_id] = verification_code
                    
                    if user_id in verification_codes:
                        sendEmail(cevap, verification_code)
                        await message.channel.send(f"what is the code")
                    else:
                        await message.channel.send(f"invalid")
                elif message.author.id in verification_codes:
                    expected_code = verification_codes[message.author.id]
                    if cevap == expected_code:
                        guild_name = "Guild name"
                        guild = discord.utils.get(client.guilds, name=guild_name)
                        if guild is not None:
                            auth_role = discord.utils.get(guild.roles, name="auth")
                            if auth_role is not None:
                                member = await guild.fetch_member(message.author.id)
                                if member is not None:
                                    sended = sendUser(message.author.name, usermail)

                                    if(sended == 0):
                                        await message.channel.send(f"Already verificated")
                                    elif(sended == 2):
                                        await message.channel.send(f"Email used")
                                    elif(sended == 3):
                                        await member.add_roles(role, auth_role)
                                        await message.channel.send(f"Success Message")
                                        await member.edit(nick=usermail)
                                    
                                    
                                    
                                else:
                                    await message.channel.send(f"User not in guild")
                            else:
                                await message.channel.send(f"'roles not found")
                        else:
                            await message.channel.send(f"guild not found")
                        
                    else:
                        await message.channel.send(f"wrong code")
                else:
                    await message.channel.send(f"wrong email ext.")
        else:
            
            content = message.content.lower()
            if snf.tahmin([content]):
                await message.delete()
                await message.channel.send(f"{message.author.mention}, warning message!")
            else:
                attachments = message.attachments
                if any(word in content for word in ['http', 'www.', '.png', '.jpg', '.gif', '.mp4', "https", ".com"]):
                    await message.delete()
                    await message.channel.send(f"{message.author.mention}, warning message")
                    return
                for attachment in attachments:
                    if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.gif', '.mp4']):
                        await message.delete()
                        await message.channel.send(f"{message.author.mention}, warning message")
                        return


client.run(token)
