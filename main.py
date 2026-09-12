import discord
from discord.ext import commands
from discord import app_commands
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class AnnouncementModal(discord.ui.Modal, title="📢 Create Announcement"):
    message_content = discord.ui.TextInput(
        label="Announcement Message",
        style=discord.TextStyle.paragraph,
        placeholder="Type what you want to announce here...",
        required=True,
        max_length=2000
    )

    def __init__(self, target_channel: discord.TextChannel):
        super().__init__()
        self.target_channel = target_channel

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📢 ┃ System Announcement",
            description=self.message_content.value,
            color=discord.Color.from_rgb(15, 82, 186)
        )
        embed.set_footer(text=f"Announcement by {interaction.user.display_name}")
        
        try:
            await self.target_channel.send(embed=embed)
            await interaction.response.send_message(f"✅ Announcement successfully sent to {self.target_channel.mention}!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to send announcement: {e}", ephemeral=True)

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Account Verify", description="Open a ticket for account verification help", emoji="🔐", value="verify"),
            discord.SelectOption(label="Phone Number", description="Open a ticket regarding phone number support", emoji="📱", value="phone"),
            discord.SelectOption(label="Partnership", description="Open a ticket to discuss server partnerships", emoji="🤝", value="partnership")
        ]
        super().__init__(placeholder="📌 Select a support category...", min_values=1, max_values=1, options=options, custom_id="ticket_dropdown_select")

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category_name = self.values[0]
        
        existing_channel = discord.utils.get(guild.text_channels, name=f"{interaction.user.name.lower()}-{category_name}")
        if existing_channel:
            return await interaction.response.send_message(f"❌ You already have an active ticket open here: {existing_channel.mention}", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)
        }

        ticket_channel = await guild.create_text_channel(name=f"{interaction.user.name}-{category_name}", overwrites=overwrites)
        
        embed = discord.Embed(
            title=f"🎫 ┃ Support Ticket: {category_name.capitalize()}",
            description=f"✨ Hello {interaction.user.mention}, staff will be with you shortly.\nPlease describe your inquiry regarding **{category_name}**.\n\n*If you need help logging into the website, use `/help`.*",
            color=discord.Color.from_rgb(15, 82, 186)
        )
        embed.set_footer(text="Support System • Secure Delivery")
        
        await ticket_channel.send(content=interaction.user.mention, embed=embed, view=TicketCloseView())
        await interaction.response.send_message(f"✅ Ticket created successfully: {ticket_channel.mention}", ephemeral=True)

class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Closing ticket in 5 seconds...", ephemeral=True)
        await asyncio.sleep(5)
        try:
            await interaction.channel.delete()
        except Exception:
            pass

class TicketDropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

@bot.event
async def on_ready():
    bot.add_view(TicketDropdownView())
    bot.add_view(TicketCloseView())
    await bot.tree.sync()
    print(f"✨ Ticket & Announcement Bot Logged in as {bot.user} successfully!")

@bot.tree.command(name="setup", description="Deploy the ticket dropdown support menu.")
async def setup_ticket_menu(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Admin only.", ephemeral=True)
    
    embed = discord.Embed(
        title="🎫 ┃ Support Ticket Center",
        description="✨ **Need assistance? Select an option from the dropdown menu below to open a private support ticket:**\n\n• 🔐 **Account Verify**\n• 📱 **Phone Number**\n• 🤝 **Partnership**",
        color=discord.Color.from_rgb(15, 82, 186)
    )
    embed.set_footer(text="Support System • Secure Delivery")
    await interaction.channel.send(embed=embed, view=TicketDropdownView())
    await interaction.response.send_message("✅ Ticket dropdown menu successfully deployed in this channel.", ephemeral=True)

@bot.tree.command(name="announcement", description="Send a professional announcement to a specific channel using a pop-up menu.")
@app_commands.describe(channel="The channel where you want the announcement to be sent")
async def announcement_command(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Admin only.", ephemeral=True)
    
    await interaction.response.send_modal(AnnouncementModal(target_channel=channel))

@bot.tree.command(name="help", description="Help menu & website login guide.")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📖 ┃ HELP & WEBSITE LOGIN GUIDE",
        description=(
            "✨ **Welcome! Follow these steps to get started:**\n\n"
            "1️⃣ Type `/generate` in the generator Discord server to receive your account credentials in your Direct Messages.\n"
            "2️⃣ Copy the **email** and **password** sent by the bot.\n"
            "3️⃣ Head over to the website: https://mail.madsnod.lol/\n"
            "4️⃣ Log in using the exact same password provided by `/generate`.\n"
            "5️⃣ Once logged in, **always refresh the page** to see and press the verification prompt.\n\n"
            "📌 **Need extra help?** Use the `/setup` ticket menu in the support channel to open a ticket for **Account Verify**, **Phone Number**, or **Partnership**!"
        ),
        color=discord.Color.from_rgb(15, 82, 186)
    )
    embed.set_footer(text="Support System • Secure Delivery")
    await interaction.response.send_message(embed=embed, ephemeral=True)

bot.run("")

