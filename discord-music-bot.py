import discord
from discord.ext import commands
from pytube import YouTube
import youtube_dl
import os
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

bot = commands.Bot(command_prefix='/')

# Codigo para tocar música e gerenciar 

@bot.command()
async def play(ctx, url: str):
    """Inicia a reprodução de uma música a partir de uma URL do YouTube"""
    try:
        voice_channel = ctx.author.voice.channel
        if bot.voice_clients:
            await bot.voice_clients[0].disconnect()
        voice_client = await voice_channel.connect()
        video = YouTube(url)
        audio_stream = video.streams.filter(only_audio=True).first()
        audio_filename = audio_stream.default_filename
        if not os.path.exists(audio_filename):
            audio_stream.download()
        source = discord.FFmpegPCMAudio(audio_filename)
        voice_client.play(source)
        await ctx.send(f"Tocando {video.title}")
    except Exception as e:
        await ctx.send("Ocorreu um erro ao tentar reproduzir a música.")
        print(e)

@bot.command()
async def pause(ctx):
    """Pausa a reprodução da música atual"""
    voice_client = ctx.voice_client
    if voice_client.is_playing():
        voice_client.pause()

@bot.command()
async def resume(ctx):
    """Continua a reprodução da música que estava pausada"""
    voice_client = ctx.voice_client
    if voice_client.is_paused():
        voice_client.resume()

@bot.command()
async def stop(ctx):
    """Encerra a reprodução da música e remove o arquivo baixado"""
    voice_client = ctx.voice_client
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()
        audio_filename = voice_client.source._source
        os.remove(audio_filename)

@bot.command()
async def mute(ctx):
    """Muta o bot no canal de voz"""
    voice_client = ctx.voice_client
    if voice_client.is_playing() or voice_client.is_paused():
        if not voice_client.is_muted():
            await voice_client.guild.voice_client.main_ws.voice_state(str(voice_client.channel.id), mute=True)
        else:
            await ctx.send("O bot já está mutado.")

@bot.command()
async def unmute(ctx):
    """Desmuta o bot no canal de voz"""
    voice_client = ctx.voice_client
    if voice_client.is_playing() or voice_client.is_paused():
        if voice_client.is_muted():
            await voice_client.guild.voice_client.main_ws.voice_state(str(voice_client.channel.id), mute=False)
        else:
            await ctx.send("O bot já está desmutado.")

@bot.command()
async def volume(ctx, vol: float):
    """Altera o volume da música que está sendo reproduzida"""
    voice_client = ctx.voice_client
    if voice_client.is_playing() or voice_client.is_paused():
        if 0 <= vol <= 100:
            voice_client.source.volume = vol / 100
        else:
            await ctx.send("O valor do volume deve estar entre 0 e 100.")

@bot.event
async def on_voice_state_update(member, before, after):
    """Evento disparado quando um usuário entra ou sai do canal de voz"""
    voice_client = member.guild.voice_client

    if voice_client is None:
        return

    if voice_client.channel != before.channel and voice_client.channel == after.channel:
        # Bot entrou no canal de voz
        pass
    elif voice_client.channel == before.channel and voice_client.channel != after.channel:
        # Bot saiu do canal de voz
        if voice_client.source and isinstance(voice_client.source, discord.PCMVolumeTransformer):
            voice_client.stop()
            if os.path.exists(voice_client.source.filename):
                os.remove(voice_client.source.filename)
        await voice_client.disconnect()

bot.run('TOKEN')
