import discord
from discord import app_commands
from discord.ext import commands
import json
import os
from datetime import datetime, UTC, timedelta
import asyncio
from keep_alive import keep_alive
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# إعدادات البوت
TOKEN = os.getenv('TOKEN')
POINTS_FILE = 'points.json'
ROLES_FILE = 'points_roles.json'
ROLE_POINTS_FILE = 'role_points.json'  # ملف جديد لتخزين نقاط الرتب
MUTED_ROLE_NAME = "Muted"  # اسم رتبة الميوت

# تهيئة البوت مع الصلاحيات المطلوبة
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# دوال نظام النقاط
def load_points():
    """تحميل النقاط من الملف"""
    if os.path.exists(POINTS_FILE):
        with open(POINTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_points(points_data):
    """حفظ النقاط في الملف"""
    with open(POINTS_FILE, 'w') as f:
        json.dump(points_data, f, indent=4)

def get_user_points(user_id):
    """الحصول على نقاط المستخدم"""
    points_data = load_points()
    return points_data.get(str(user_id), 0)

def add_points(user_id, amount):
    """إضافة نقاط للمستخدم"""
    points_data = load_points()
    user_id = str(user_id)
    points_data[user_id] = points_data.get(user_id, 0) + amount
    save_points(points_data)

def remove_points(user_id, amount):
    """سحب نقاط من المستخدم"""
    points_data = load_points()
    user_id = str(user_id)
    current_points = points_data.get(user_id, 0)
    new_points = max(0, current_points - amount)
    points_data[user_id] = new_points
    save_points(points_data)
    return new_points

# دوال نظام الرتب
def load_points_roles():
    """تحميل رتب النقاط من الملف"""
    if os.path.exists(ROLES_FILE):
        with open(ROLES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_points_roles(roles_data):
    """حفظ رتب النقاط في الملف"""
    with open(ROLES_FILE, 'w') as f:
        json.dump(roles_data, f, indent=4)

# دوال نظام نقاط الرتب
def load_role_points():
    """تحميل نقاط الرتب من الملف"""
    if os.path.exists(ROLE_POINTS_FILE):
        with open(ROLE_POINTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_role_points(role_points_data):
    """حفظ نقاط الرتب في الملف"""
    with open(ROLE_POINTS_FILE, 'w') as f:
        json.dump(role_points_data, f, indent=4)

# دوال نظام الحماية
async def get_or_create_muted_role(guild):
    """الحصول على رتبة الميوت أو إنشائها إذا لم تكن موجودة"""
    muted_role = discord.utils.get(guild.roles, name=MUTED_ROLE_NAME)
    if not muted_role:
        muted_role = await guild.create_role(
            name=MUTED_ROLE_NAME,
            reason="إنشاء رتبة الميوت"
        )

# حدث: البوت جاهز
@bot.event
async def on_ready():
    print(f'البوت جاهز! تم تسجيل الدخول باسم {bot.user.name}')
    try:
        synced = await bot.tree.sync()
        print(f"تم مزامنة {len(synced)} أمر")
    except Exception as e:
        print(f"فشل في مزامنة الأوامر: {e}")

# أوامر الحماية
@bot.tree.command(name="mute", description="إسكات عضو (للمشرفين فقط)")
@app_commands.checks.has_permissions(moderate_members=True)
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = "لم يتم تحديد سبب"):
    try:
        await member.timeout(timedelta(minutes=duration), reason=reason)
        embed = discord.Embed(
            title="تم إسكات العضو",
            description=f"تم إسكات {member.mention} لمدة {duration} دقيقة\nالسبب: {reason}",
            color=discord.Color.red(),
            timestamp=datetime.now(UTC)
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"حدث خطأ: {str(e)}", ephemeral=True)

@bot.tree.command(name="unmute", description="إلغاء إسكات عضو (للمشرفين فقط)")
@app_commands.checks.has_permissions(moderate_members=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    try:
        await member.timeout(None)
        embed = discord.Embed(
            title="تم إلغاء إسكات العضو",
            description=f"تم إلغاء إسكات {member.mention}",
            color=discord.Color.green(),
            timestamp=datetime.now(UTC)
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"حدث خطأ: {str(e)}", ephemeral=True)

@bot.tree.command(name="ban", description="حظر عضو (للمشرفين فقط)")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد سبب"):
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="تم حظر العضو",
            description=f"تم حظر {member.mention}\nالسبب: {reason}",
            color=discord.Color.red(),
            timestamp=datetime.now(UTC)
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"حدث خطأ: {str(e)}", ephemeral=True)

@bot.tree.command(name="kick", description="طرد عضو (للمشرفين فقط)")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "لم يتم تحديد سبب"):
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="تم طرد العضو",
            description=f"تم طرد {member.mention}\nالسبب: {reason}",
            color=discord.Color.orange(),
            timestamp=datetime.now(UTC)
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"حدث خطأ: {str(e)}", ephemeral=True)

@bot.tree.command(name="clear", description="مسح رسائل (للمشرفين فقط)")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):
    try:
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        embed = discord.Embed(
            title="تم مسح الرسائل",
            description=f"تم مسح {len(deleted)} رسالة",
            color=discord.Color.blue(),
            timestamp=datetime.now(UTC)
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"حدث خطأ: {str(e)}", ephemeral=True)

# أوامر إنشاء الإمبيد
@bot.tree.command(name="createembed", description="إنشاء إمبيد مخصص")
@app_commands.checks.has_permissions(manage_messages=True)
async def createembed(
    interaction: discord.Interaction,
    title: str,
    description: str,
    color: str = "blue",
    thumbnail: str = None,
    image: str = None,
    footer: str = None
):
    # تحويل اللون من النص إلى كائن Color
    color_map = {
        "blue": discord.Color.blue(),
        "red": discord.Color.red(),
        "green": discord.Color.green(),
        "yellow": discord.Color.yellow(),
        "purple": discord.Color.purple(),
        "orange": discord.Color.orange(),
        "gold": discord.Color.gold()
    }
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=color_map.get(color.lower(), discord.Color.blue()),
        timestamp=datetime.now(UTC)
    )
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    if footer:
        embed.set_footer(text=footer)
    
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="addembedfield", description="إضافة حقل للإمبيد")
@app_commands.checks.has_permissions(manage_messages=True)
async def addembedfield(
    interaction: discord.Interaction,
    message_id: str,
    name: str,
    value: str,
    inline: bool = False
):
    try:
        message = await interaction.channel.fetch_message(int(message_id))
        if not message.embeds:
            await interaction.response.send_message("لم يتم العثور على إمبيد في هذه الرسالة", ephemeral=True)
            return
        
        embed = message.embeds[0]
        embed.add_field(name=name, value=value, inline=inline)
        
        await message.edit(embed=embed)
        await interaction.response.send_message("تم إضافة الحقل بنجاح!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"حدث خطأ: {str(e)}", ephemeral=True)

# أوامر النقاط السابقة
@bot.tree.command(name="points", description="عرض رصيد نقاطك")
async def points(interaction: discord.Interaction):
    user_points = get_user_points(interaction.user.id)
    embed = discord.Embed(
        title="رصيد النقاط",
        description=f"لديك {user_points} نقطة!",
        color=discord.Color.blue(),
        timestamp=datetime.now(UTC)
    )
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="addpoints", description="إضافة نقاط لمستخدم (للمشرفين فقط)")
@app_commands.checks.has_permissions(administrator=True)
async def addpoints(interaction: discord.Interaction, user: discord.Member, amount: int):
    # التحقق من صلاحية المشرف
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("عذراً، هذا الأمر متاح فقط للمشرفين!", ephemeral=True)
        return
        
    if amount <= 0:
        await interaction.response.send_message("يجب أن تكون النقاط أكبر من صفر!", ephemeral=True)
        return
    
    add_points(user.id, amount)
    embed = discord.Embed(
        title="تمت إضافة النقاط",
        description=f"تمت إضافة {amount} نقطة لـ {user.mention}",
        color=discord.Color.green(),
        timestamp=datetime.now(UTC)
    )
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="removepoints", description="سحب نقاط من مستخدم (للمشرفين فقط)")
@app_commands.checks.has_permissions(administrator=True)
async def removepoints(interaction: discord.Interaction, user: discord.Member, amount: int):
    # التحقق من صلاحية المشرف
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("عذراً، هذا الأمر متاح فقط للمشرفين!", ephemeral=True)
        return
        
    if amount <= 0:
        await interaction.response.send_message("يجب أن تكون النقاط أكبر من صفر!", ephemeral=True)
        return
    
    new_points = remove_points(user.id, amount)
    embed = discord.Embed(
        title="تم سحب النقاط",
        description=f"تم سحب {amount} نقطة من {user.mention}\nالرصيد الجديد: {new_points} نقطة",
        color=discord.Color.red(),
        timestamp=datetime.now(UTC)
    )
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="addpointsrole", description="إضافة رتبة للنقاط (للمشرفين فقط)")
@app_commands.checks.has_permissions(administrator=True)
async def addpointsrole(interaction: discord.Interaction, role: discord.Role, points_required: int):
    roles_data = load_points_roles()
    roles_data[str(role.id)] = points_required
    save_points_roles(roles_data)
    
    embed = discord.Embed(
        title="تمت إضافة رتبة النقاط",
        description=f"تم إضافة رتبة {role.mention} مع {points_required} نقطة مطلوبة",
        color=discord.Color.green(),
        timestamp=datetime.now(UTC)
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="pointsroles", description="عرض رتب النقاط المتاحة")
async def pointsroles(interaction: discord.Interaction):
    roles_data = load_points_roles()
    if not roles_data:
        await interaction.response.send_message("لا توجد رتب نقاط مضافة حالياً", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="رتب النقاط المتاحة",
        color=discord.Color.blue(),
        timestamp=datetime.now(UTC)
    )
    
    for role_id, points in roles_data.items():
        role = interaction.guild.get_role(int(role_id))
        if role:
            embed.add_field(
                name=role.name,
                value=f"النقاط المطلوبة: {points}",
                inline=False
            )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="leaderboard", description="عرض لوحة المتصدرين")
async def leaderboard(interaction: discord.Interaction):
    points_data = load_points()
    sorted_users = sorted(points_data.items(), key=lambda x: x[1], reverse=True)
    
    embed = discord.Embed(
        title="لوحة المتصدرين",
        color=discord.Color.gold(),
        timestamp=datetime.now(UTC)
    )
    
    for i, (user_id, points) in enumerate(sorted_users[:10], 1):
        user = await bot.fetch_user(int(user_id))
        embed.add_field(
            name=f"{i}. {user.name}",
            value=f"{points} نقطة",
            inline=False
        )
    
    await interaction.response.send_message(embed=embed)

# إضافة أمر جديد لإعداد نقاط الرتب
@bot.tree.command(name="setrolepoints", description="تعيين نقاط للرتبة (للمشرفين فقط)")
@app_commands.checks.has_permissions(administrator=True)
async def setrolepoints(interaction: discord.Interaction, role: discord.Role, points: int):
    role_points = load_role_points()
    role_points[str(role.id)] = points
    save_role_points(role_points)
    
    embed = discord.Embed(
        title="تم تعيين نقاط الرتبة",
        description=f"تم تعيين {points} نقطة لرتبة {role.mention}",
        color=discord.Color.green(),
        timestamp=datetime.now(UTC)
    )
    await interaction.response.send_message(embed=embed)

# إضافة أمر لعرض نقاط الرتب
@bot.tree.command(name="rolepoints", description="عرض نقاط الرتب")
async def rolepoints(interaction: discord.Interaction):
    role_points = load_role_points()
    if not role_points:
        await interaction.response.send_message("لا توجد رتب مخصصة للنقاط حالياً", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="نقاط الرتب",
        color=discord.Color.blue(),
        timestamp=datetime.now(UTC)
    )
    
    for role_id, points in role_points.items():
        role = interaction.guild.get_role(int(role_id))
        if role:
            embed.add_field(
                name=role.name,
                value=f"النقاط: {points}",
                inline=False
            )
    
    await interaction.response.send_message(embed=embed)

# إضافة حدث لتحديث النقاط عند إضافة رتبة
@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        role_points = load_role_points()
        added_roles = set(after.roles) - set(before.roles)
        
        for role in added_roles:
            if str(role.id) in role_points:
                points = role_points[str(role.id)]
                add_points(after.id, points)
                
                # إرسال رسالة تأكيد
                try:
                    embed = discord.Embed(
                        title="تم إضافة نقاط",
                        description=f"تم إضافة {points} نقطة بسبب رتبة {role.mention}",
                        color=discord.Color.green(),
                        timestamp=datetime.now(UTC)
                    )
                    await after.send(embed=embed)
                except:
                    pass  # تجاهل إذا لم نتمكن من إرسال الرسالة

# تشغيل البوت
if __name__ == "__main__":
    try:
        print("جاري تشغيل البوت...")
        keep_alive()
        bot.run(TOKEN)
    except discord.LoginFailure:
        print("خطأ: التوكن غير صحيح أو منتهي الصلاحية. يرجى تحديث التوكن.")
    except Exception as e:
        print(f"حدث خطأ: {e}")
