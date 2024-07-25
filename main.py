import discord
from discord import app_commands
from discord.ext import commands
from googleapiclient.discovery import build
import json

with open('stuff.json') as f:
    config = json.load(f)

youtube_api_key = config['youtubeAK']
discord_token = config['discordT']

youtube = build('youtube', 'v3', developerKey=youtube_api_key)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

def get_video_details(video_id):
    request = youtube.videos().list(
        part='snippet,statistics',
        id=video_id
    )
    response = request.execute()
    video = response['items'][0]

    title = video['snippet']['title']
    description = video['snippet']['description'][:150] + '...' if len(video['snippet']['description']) > 150 else video['snippet']['description']
    views = video['statistics'].get('viewCount', 'N/A')
    likes = video['statistics'].get('likeCount', 'N/A')
    thumbnail = video['snippet']['thumbnails']['high']['url']
    url = f"https://www.youtube.com/watch?v={video_id}"

    title = title[:256] if len(title) > 256 else title

    return title, description, views, likes, thumbnail, url

@bot.event
async def on_ready():
    print(f'{bot.user}')
    await bot.tree.sync()

@bot.tree.command(name="video", description="Get details")
@app_commands.describe(video_id="Example: /video video_id:zzzzwtvRZJ0 get it from the video url.")
async def video(interaction: discord.Interaction, video_id: str):
    try:
        title, description, views, likes, thumbnail, url = get_video_details(video_id)
        
        embed = discord.Embed(description=description, color=0x00ff00)
        embed.set_author(name=title, url=url, icon_url=thumbnail)
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(name='Views', value=views, inline=False)
        embed.add_field(name='Likes', value=likes, inline=False)
        
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"An error occurred: {e}")

bot.run(discord_token)
