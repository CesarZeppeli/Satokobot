import discord
from discord.ext import commands, tasks
import youtube_dl
from discord.utils import get
from random import choice
from discord.voice_client import VoiceClient
import os
import json



if os.path.exists(os.getcwd() + "/config.json"):
    
    with open("./config.json") as f:
        configData = json.load(f)

else:
    configTemplate = {"Token": "", "Prefix": "!"}

    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f) 

token = configData["Token"]
prefix = configData["Prefixo"]



#Começo do codigo yt

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

#FIM DO CODIGO YT


#Prefixo do bot
client = commands.Bot(command_prefix='!')

#Status do bot
status = ['Humilhando pessoas', 'Criando armadilhas', 'Sendo gay', 'Chorando']
queue = []




#Mensagem online
@client.event
async def on_ready():
	change_status.start()
	print('Eu estou online, tolinho!')

#Comando ping
@client.command(name='ping', help='É a latência')
async def ping(ctx):
	await ctx.send(f'**Pong!** Latência: {round(client.latency * 1000)}ms')


#Comando oi
@client.command(name='oi', help='Retorna uma mensagem')
async def hello(ctx):
	await ctx.send(f'Ara ara! Por que está me incomodando, {ctx.author.mention}?')


#Comando creditos
@client.command(name='cred', help='Créditos do bot')
async def cred(ctx):
	await ctx.send('Feito por #CésarZeppeli#8640 cópia não comedia')


#Comando join
@client.command(name='join')
async def join(ctx):
	if not ctx.message.author.voice:
		await ctx.send('Você não está conectado em um canal de voz, idiota!')
		return

	else:
		channel = ctx.message.author.voice.channel

		await channel.connect()


#Comando parar
@client.command(name='sair', help='Para a música')
async def sair(ctx):
	voice_client = ctx.message.guild.voice_client
	await voice_client.disconnect()


#Comando play
@client.command(name='toca', help='Toca música')
async def toca(ctx):
	global queue

	server = ctx.message.guild
	voice_channel = server.voice_client

	async with ctx.typing():
		player = await YTDLSource.from_url(queue[0], loop=client.loop)
		voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)
			

	await ctx.send('**Tocando:** {}'.format(player.title))
	del(queue[0])


#Comando pause
@client.command(name='pausa', help='Obviamente **pausa** a música, idiota.')
async def pausa(ctx):
	server = ctx.message.guild
	voice_channel = server.voice_client

	voice_channel.pause()


#Comando resume
@client.command(name='resume', help='Obviamente **resume** a música, idiota.')
async def pausa(ctx):
	server = ctx.message.guild
	voice_channel = server.voice_client

	voice_channel.resume()


#Comando queue
@client.command(name='queue')
async def queue_(ctx, url):
	global queue

	queue.append(url)
	await ctx.send(f'`{url}` Adicionado à lista!')


@client.command(name='remove', help='Remove música')
async def remove(ctx, number):
	global queue

	try:
		del(queue[int(number)])
		await ctx.send('**Apagou** {}'.format(player.title))

	except:
		await ctx.send('Sua lista está vazia!')
		number += 0


#Comando ver queue
@client.command(name='lista', help='Mostra a playlist')
async def lista_(ctx):
	await ctx.send(f'Sua lista agora é `{queue}!`')



#Muda status
@tasks.loop(seconds=60)
async def change_status():
	await client.change_presence(activity=discord.Game(choice(status)))





client.run(token)