import datetime
from discord.ext import commands,tasks
import discord
from dataclasses import dataclass

CHANNEL_ID=('1271180861949349911')
#MTMzMDExNjA5OTk3ODY5MDYxMQ.G0EuJp.0qNwP0a73KWc9sYbEwXakfCTwRH5op9ApsmmC8

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Hello!")
    channel = await bot.fetch_channel(CHANNEL_ID)
    await channel.send("Hello!")

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
        
@bot.event 
async def on_member_join(member):
     channel= await bot.fetch_channel(CHANNEL_ID)
     
     emb=discord.Embed(title="NEW MEMBER",
     description=f"Thanks {member.mention} for joining!",
     colour=discord.Colour.blue()
     )
     emb.set_image(url='https://cdn.discordapp.com/attachments/1271180861949349911/1330337606990565539/image0.jpg?ex=678d9cf1&is=678c4b71&hm=d46ab07d37f0b1550f7593c670228ec36916ed2769340ca2e822cd5b1a818d43&')
     await channel.send(embed=emb)
     
bot.run('MTMzMDExNjA5OTk3ODY5MDYxMQ.G0EuJp.0qNwP0a73KWc9sYbEwXakfCTwRH5op9ApsmmC8')