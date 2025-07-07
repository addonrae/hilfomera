import discord
import asyncio
import requests
import random

BOT_TOKEN = "8043331214:AAHDVSwrNVAK2UGh1UwPHbLFt7wBgPKHbZA"
CHAT_ID = "6931323094"
MY_USER_ID = 1163516997489930281  # Your Discord user ID as int

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

client = discord.Client(intents=intents)

last_ping_message = None

def send_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    return response

@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")

@client.event
async def on_message(message):
    global last_ping_message

    # Ignore messages from yourself
    if message.author.id == client.user.id:
        # Check if !reply command in DM or guild
        if message.content.strip().lower() == "!reply":
            if last_ping_message is None:
                await message.channel.send("No ping message to reply to.")
            else:
                replies = ["what?", "wut?", "?"]
                reply_text = random.choice(replies)
                try:
                    await last_ping_message.reply(reply_text)
                    await message.channel.send(f"Replied to ping with: {reply_text}")
                except Exception as e:
                    await message.channel.send(f"Failed to reply: {e}")
        return

    # Check if you are mentioned in this message
    if MY_USER_ID in [user.id for user in message.mentions]:
        last_ping_message = message  # Save message for reply

        # Build Telegram message
        server_name = message.guild.name if message.guild else "DM"
        channel_name = message.channel.name if hasattr(message.channel, 'name') else "DM"
        author_name = f"{message.author.name}#{message.author.discriminator}"
        content = message.content

        telegram_text = (
            f"🚨 <b>PING ALERT!</b> 🚨\n"
            f"<b>Server:</b> {server_name}\n"
            f"<b>Channel:</b> #{channel_name}\n"
            f"<b>From:</b> {author_name}\n"
            f"<b>User ID:</b> {message.author.id}\n"
            f"<b>Message:</b>\n<code>{content}</code>\n"
            f"<b>Message ID:</b> {message.id}\n"
            f"<b>Channel ID:</b> {message.channel.id}"
        )
        send_telegram(telegram_text)

client.run('MTE2MzUxNjk5NzQ4OTkzMDI4MQ.GBNU4w.R7rDFIBNYQLHI04v6EcUXQScfZeScemSGbe7i8', bot=False)
