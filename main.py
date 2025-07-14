import time
import requests
import discord
from discord.ext import tasks, commands
import os

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])
UNIVERSE_ID = os.environ['UNIVERSE_ID']
THRESHOLD = 1500000  # change if you want a different CCU
COOLDOWN_SECONDS = 30 * 60  # 30 minutes
last_alert_time = 0

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

def get_ccu():
    url = f"https://games.roblox.com/v1/games?universeIds={UNIVERSE_ID}"
    try:
        r = requests.get(url)
        data = r.json()
        return data['data'][0]['playing']
    except Exception as e:
        print("Error fetching CCU:", e)
        return 0

@tasks.loop(minutes=1)
async def check_game():
    global last_alert_time

    ccu = get_ccu()
    print(f"[{time.strftime('%H:%M:%S')}] Current CCU: {ccu}")

    current_time = time.time()
    time_since_last_alert = current_time - last_alert_time

    if ccu >= THRESHOLD and time_since_last_alert >= COOLDOWN_SECONDS:
        channel = bot.get_channel(CHANNEL_ID)
        await channel.send(f"@everyone ⚠️ Game hit **{ccu:,}** CCU! Possible admin abuse happening 👀")
        last_alert_time = current_time  # start cooldown
    else:
        print("No alert sent. On cooldown or under threshold.")

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    check_game.start()

bot.run(DISCORD_TOKEN)
