import datetime
from discord.ext import commands,tasks
import discord
import asyncio
import aiosqlite
import random
import requests
import praw

CHANNEL_ID=('1271180861949349911')
#MTMzMDExNjA5OTk3ODY5MDYxMQ.G0EuJp.0qNwP0a73KWc9sYbEwXakfCTwRH5op9ApsmmC8

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


# Function to initialize the database
async def init_db():
    conn = await aiosqlite.connect('bot_data.db')
    c = await conn.cursor()
    await c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            guild_id INTEGER PRIMARY KEY,
            welcome_channel_id INTEGER
        )
    ''')
    await conn.commit()
    await conn.close()
 
reddit = praw.Reddit(
    client_id='-6EDwE2Vqm6Qxg_DSe2oMA',
    client_secret='_TxTl28UsAF0L2FtaVHcetQzojPmfw',
    user_agent='discord:my_meme_bot:v1.0'
)

@bot.event
async def on_ready():
    print("Bot is ready!")
    await init_db()
    async with aiosqlite.connect('bot_data.db') as db:
        async with db.execute('SELECT guild_id, welcome_channel_id FROM settings') as cursor:
            async for row in cursor:
                guild_id, channel_id = row
                guild = bot.get_guild(guild_id)
                if guild:
                    global welcome_channel_id
                    welcome_channel_id = channel_id
    print("Welcome channels loaded from the database.")

@bot.command()
async def ping(ctx):
		channel = await bot.fetch_channel(CHANNEL_ID)
		await ctx.send('Pong!')
		print(f'Sent by {ctx.author}')
		

@bot.command()
async def sum(ctx,  *arr):
		result=0
		for i in arr:
			result += int(i)
		await ctx.send(f"Result: {result}")
		print(f'Sent by {ctx.author}')
		
@bot.command()
@commands.has_role('Administrator')  # Ensure only users with "Moderator" role can use this
async def assign_role(ctx, member: discord.Member, role: discord.Role):
    # Check if the role is higher than the bot's role
    if role.position >= ctx.guild.me.top_role.position:
        await ctx.send("I cannot assign a role that is higher than my own.")
        return
    
    try:
        await member.add_roles(role)
        await ctx.send(f"Successfully assigned {role.name} to {member.name}.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

@bot.command()
@commands.has_role('Administrator')                
async def remove_role(ctx, member: discord.Member, role: discord.Role):
    # Check if the role is higher than the bot's role
    if role.position >= ctx.guild.me.top_role.position:
        await ctx.send("I cannot remove a role that is higher than my own.")
        return
    
    try:
        await member.remove_roles(role)
        await ctx.send(f"Successfully removed {role.name} from {member.name}.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

# Error handling for permission issues
@assign_role.error
async def assign_role_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You need the Moderator role to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify a member and a role.")
    else:
        await ctx.send("An error occurred while assigning the role.")

@bot.command()
@commands.has_permissions(administrator=True)
async def set_welcome_channel(ctx, channel: discord.TextChannel):
    guild_id = ctx.guild.id
    channel_id = channel.id
    
    async with aiosqlite.connect('bot_data.db') as db:
        await db.execute('REPLACE INTO settings (guild_id, welcome_channel_id) VALUES (?, ?)', (guild_id, channel_id))
        await db.commit()
    
    await ctx.send(f'Welcome channel has been set to {channel.mention}')


@bot.event
async def on_member_join(member):
    global welcome_channel_id
    if welcome_channel_id:
        channel = bot.get_channel(welcome_channel_id)
        if channel:
            emb = discord.Embed(
                title="NEW MEMBER",
                description=f"Thanks {member.mention} for joining!",
                colour=discord.Colour.blue()
            )
            emb.set_image(url='https://example.com/image.jpg')
            emb.add_field(name="Getting Started", value="Check out the rules channel to get familiar with our community!", inline=False)
            await channel.send(embed=emb)


@bot.command(name='kick', pass_context=True)
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'User {member} has been kicked.')

@bot.command(name='ban', pass_context=True)
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'User {member} has been banned.')

@bot.command(name='unban', pass_context=True)
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split('#')

    for ban_entry in banned_users:
        user = ban_entry.user
        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'User {user} has been unbanned.')
            return

@bot.command(name='mute', pass_context=True)
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: int = 0, *, reason=None):
    muted_role = discord.utils.get(ctx.guild.roles, name='Muted')
    if not muted_role:
        muted_role = await ctx.guild.create_role(name='Muted')
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)
    
    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f'User {member} has been muted.')

    if duration > 0:
        await ctx.send(f'User {member} will be unmuted in {duration} minutes.')
        await asyncio.sleep(duration * 60)
        await member.remove_roles(muted_role)
        await ctx.send(f'User {member} has been unmuted.')


@bot.command(name='unmute', pass_context=True)
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name='Muted')
    await member.remove_roles(muted_role)
    await ctx.send(f'User {member} has been unmuted.')

@kick.error
@ban.error
@unban.error
@mute.error
@unmute.error
async def command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have the required permissions to run this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify the user and reason (if applicable).")
    else:
        await ctx.send("An error occurred.")
        
@bot.command()
async def dm(ctx, user: discord.User, *, message: str):
    """Sends a DM to the specified user. Restricted to user groov21."""
    if ctx.author.id == 1270322401560891463:
        try:
            await user.send(message)
            await ctx.send(f"Message sent to {user.name}")
        except discord.Forbidden:
            await ctx.send("I cannot send a message to this user.")
    else:
        await ctx.send("You are not authorized to use this command.")

@bot.event
async def on_message(message):
    # Check if the message is a DM
    if isinstance(message.channel, discord.DMChannel) and not message.author.bot:
        print(f"Received a DM from {message.author} (ID: {message.author.id}): {message.content}")
        
    
    # Process other commands if any
    await bot.process_commands(message)


@bot.command()
async def meme(ctx):
    subreddit = reddit.subreddit('memes')
    posts = list(subreddit.hot(limit=100))  # Fetch the top 50 hot posts
    post = random.choice(posts)  # Choose a random post

    if not post.over_18:  # Check if the post is not NSFW
        embed = discord.Embed(title=post.title, color=discord.Color.blue())
        embed.set_image(url=post.url)
        embed.set_footer(text=f"👍 {post.score} | 💬 {post.num_comments} comments")
        await ctx.send(embed=embed)
    else:
        await ctx.send("Sorry, this meme is NSFW!")

bot.run('MTMzMDExNjA5OTk3ODY5MDYxMQ.G0EuJp.0qNwP0a73KWc9sYbEwXakfCTwRH5op9ApsmmC8')