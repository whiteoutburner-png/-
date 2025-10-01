import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from flask import Flask
from threading import Thread

# -----------------------------
# إعدادات Flask للحفاظ على البوت حي
# -----------------------------
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=8080)

t = Thread(target=run)
t.start()

# -----------------------------
# إعدادات البوت
# -----------------------------
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# -----------------------------
# ملفات حفظ الميلاد وقناة الترحيب
# -----------------------------
BIRTHDAY_FILE = "birthdays.json"
WELCOME_CHANNEL_FILE = "welcome_channel.json"

if os.path.exists(BIRTHDAY_FILE):
    with open(BIRTHDAY_FILE, "r", encoding="utf-8") as f:
        birthdays = json.load(f)
else:
    birthdays = {}

if os.path.exists(WELCOME_CHANNEL_FILE):
    with open(WELCOME_CHANNEL_FILE, "r", encoding="utf-8") as f:
        welcome_channels = json.load(f)
else:
    welcome_channels = {}

def save_birthdays():
    with open(BIRTHDAY_FILE, "w", encoding="utf-8") as f:
        json.dump(birthdays, f, ensure_ascii=False, indent=4)

def save_welcome_channels():
    with open(WELCOME_CHANNEL_FILE, "w", encoding="utf-8") as f:
        json.dump(welcome_channels, f, ensure_ascii=False, indent=4)

# -----------------------------
# حدث عند تشغيل البوت
# -----------------------------
@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ تم تسجيل الدخول كـ {bot.user}!")

# -----------------------------
# أدوار تلقائية عند الانضمام
# -----------------------------
@bot.event
async def on_member_join(member):
    role_names = ["أعضاء", "جديد"]
    for role_name in role_names:
        role = discord.utils.get(member.guild.roles, name=role_name)
        if role:
            await member.add_roles(role)

    channel_id = welcome_channels.get(str(member.guild.id))
    if channel_id:
        channel = member.guild.get_channel(channel_id)
        if channel:
            await channel.send(f"أهلاً {member.mention}! تم إعطاؤك الأدوار تلقائيًا.")

# -----------------------------
# أمر لتسجيل الميلاد
# -----------------------------
@tree.command(name="تسجيل_ميلاد", description="تسجيل تاريخ ميلادك")
@app_commands.describe(اليوم="يوم ميلادك", الشهر="شهر ميلادك")
async def تسجيل_ميلاد(interaction: discord.Interaction, اليوم: int, الشهر: int):
    if 1 <= اليوم <= 31 and 1 <= الشهر <= 12:
        birthdays[str(interaction.user.id)] = f"{اليوم}/{الشهر}"
        save_birthdays()
        await interaction.response.send_message(f"✅ تم تسجيل ميلادك: {اليوم}/{الشهر}")
    else:
        await interaction.response.send_message("❌ اليوم أو الشهر غير صحيح!", ephemeral=True)

# -----------------------------
# أمر لمعرفة ميلاد عضو
# -----------------------------
@tree.command(name="معرفة_ميلاد", description="معرفة ميلاد عضو")
@app_commands.describe(عضو="العضو الذي تريد معرفة ميلاده")
async def معرفة_ميلاد(interaction: discord.Interaction, عضو: discord.Member):
    birthday = birthdays.get(str(عضو.id))
    if birthday:
        await interaction.response.send_message(f"🎂 ميلاد {عضو.display_name}: {birthday}")
    else:
        await interaction.response.send_message(f"❌ لم يتم تسجيل ميلاد {عضو.display_name}", ephemeral=True)

# -----------------------------
# أمر لتعيين قناة الترحيب
# -----------------------------
@tree.command(name="تعيين_قناة_ترحيب", description="تعيين قناة الترحيب")
@app_commands.describe(channel="اختر القناة")
async def تعيين_قناة_ترحيب(interaction: discord.Interaction, channel: discord.TextChannel):
    welcome_channels[str(interaction.guild.id)] = channel.id
    save_welcome_channels()
    await interaction.response.send_message(f"✅ تم تعيين قناة الترحيب إلى {channel.mention}")

# -----------------------------
# أمر لعرض الأدوار التلقائية
# -----------------------------
@tree.command(name="الأدوار_التلقائية", description="عرض الأدوار التلقائية عند الانضمام")
async def الأدوار_التلقائية(interaction: discord.Interaction):
    role_names = ["أعضاء", "جديد"]
    await interaction.response.send_message(f"الأدوار التلقائية هي: {', '.join(role_names)}")

# -----------------------------
# تشغيل البوت
# -----------------------------
bot.run(os.environ['DISCORD_TOKEN'])
