import os
import discord
from discord.ext import commands

from myserver import server_on

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

# === ตั้งค่าพื้นฐาน ===
INTRO_CHANNEL_ID = 1429102212352835644  # ช่องให้เริ่มกรอกแบบฟอร์ม (#แนะนำตัว)
SHOWCASE_CHANNEL_ID = 1429125581391396914  # ช่องโชว์ใบแนะนำตัว (#ใบแนะนำตัว)
ROLE_ID = 1429125868529258607  # Role ที่จะมอบหลังกรอกเสร็จ

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ----- เมื่อบอทออนไลน์ -----
@bot.event
async def on_ready():
    print(f"✅ บอทออนไลน์แล้ว: {bot.user}")

# ----- เมื่อมีคนพิมพ์ในช่องแนะนำตัว -----
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == INTRO_CHANNEL_ID:
        # ลบข้อความเพื่อให้ช่องสะอาด
        await message.delete()

        # สร้างปุ่มให้กดเพื่อกรอกฟอร์ม
        button = discord.ui.Button(label="📋 กรอกแบบฟอร์มแนะนำตัว", style=discord.ButtonStyle.primary)

        async def button_callback(interaction: discord.Interaction):
            # สร้าง Modal (ฟอร์ม)
            class IntroModal(discord.ui.Modal, title="แบบฟอร์มแนะนำตัว"):
                nickname = discord.ui.TextInput(label="ชื่อเล่น", placeholder="เช่น มิน, โบว์, เอก", required=True)
                ign = discord.ui.TextInput(label="ชื่อในเกม", placeholder="เช่น LonaE123", required=True)
                about = discord.ui.TextInput(label="เกี่ยวกับตัวเอง", style=discord.TextStyle.paragraph, placeholder="เล่าหน่อยว่าเป็นใคร สนใจอะไร", required=False)

                async def on_submit(self, interaction: discord.Interaction):
                    nickname_val = self.nickname.value
                    ign_val = self.ign.value
                    about_val = self.about.value or "—"

                    # สร้าง embed สวย ๆ ไปโชว์ในช่องใบแนะนำตัว
                    embed = discord.Embed(
                        title=f"ใบแนะนำตัวของ {interaction.user.display_name}",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="ชื่อเล่น", value=nickname_val, inline=False)
                    embed.add_field(name="ชื่อในเกม", value=ign_val, inline=False)
                    embed.add_field(name="เกี่ยวกับตัวเอง", value=about_val, inline=False)
                    embed.set_thumbnail(url=interaction.user.display_avatar.url)
                    embed.set_footer(text=f"User ID: {interaction.user.id}")

                    showcase_channel = bot.get_channel(SHOWCASE_CHANNEL_ID)
                    await showcase_channel.send(embed=embed)

                    # มอบ Role ให้
                    role = interaction.guild.get_role(ROLE_ID)
                    await interaction.user.add_roles(role)

                    # ตอบกลับส่วนตัว (มองเห็นคนเดียว)
                    await interaction.response.send_message(
                        "✅ ขอบคุณที่กรอกแบบฟอร์ม! คุณได้รับสิทธิ์เข้าช่องอื่นแล้ว 🎉",
                        ephemeral=True
                    )

            # แสดง Modal ฟอร์ม
            await interaction.response.send_modal(IntroModal())

        button.callback = button_callback

        view = discord.ui.View()
        view.add_item(button)

        # ส่งปุ่มให้คนที่พิมพ์เห็นคนเดียว (ephemeral)
        await message.channel.send(
            f"{message.author.mention} กดปุ่มด้านล่างเพื่อกรอกแบบฟอร์มของคุณ 📝",
            view=view,
            delete_after=30
        )
        
server_on()

bot.run(os.getenv('TOKEN'))
