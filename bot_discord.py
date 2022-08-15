import discord
import asyncio
import os
from dotenv import load_dotenv
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle
from subprocess import Popen

from table_sales_ping import read_db

PREFIX = '/'

bot = commands.Bot(command_prefix=PREFIX)
load_dotenv('token_bot_discord.env')
id_channel = int(os.getenv('DISCORD_GUILD'))
token = os.getenv('DISCORD_TOKEN')


def output_results(results):
    result = f'{results[2][0]} - {results[2][1]}\n' \
             f'{results[1][0]} - {results[1][1]}\n' \
             f'{results[0][0]} - {results[0][1]}'
    return result


@bot.event
async def on_ready():
    DiscordComponents(bot)
    await bot.change_presence(status=discord.Status.online)
    while True:
        # проверяет лог по работе сайтов...
        channel = bot.get_channel(id_channel)
        # file = open('stat/stat.txt', 'rb')
        # file.seek(-4, 2)
        # last_massege = file.read(2).decode('UTF-8')
        sites = ['ping', 'ping_wlosk', 'ping_stargun', 'ping_chap']
        for site in sites:
            results = read_db(db='sales', table=site)
            last_massege = results[0][1]
            if last_massege != 'OK':
                if site == 'ping': site_name = 'SHELL_SALES'
                if site == 'ping_wlosk': site_name = 'STAR_WLOSK'
                if site == 'ping_stargun': site_name = 'STARGUN'
                if site == 'ping_chap': site_name = 'CHAP'
                await channel.send(f':name_badge: Не работает сайт {site_name} !!! :name_badge:')
        await asyncio.sleep(60)  # ...каждые 60 секунд


@bot.command()
async def clear(ctx, amount=10):
    await ctx.channel.purge(limit=amount)


@bot.command()
async def command(ctx):
    while True:
        channel = bot.get_channel(id_channel)
        await ctx.send(embed=discord.Embed(title='Список команд', colour=65535),
                       components=[[
                           Button(style=ButtonStyle.green, label='Status SALES', emoji='📡'),
                           Button(style=ButtonStyle.red, label='Status WLOSK', emoji='📡'),
                           Button(style=ButtonStyle.gray, label='Status STARGUN', emoji='📡'),
                           Button(style=ButtonStyle.green, label='Status CHAP', emoji='📡')
                       ],
                           [
                               Button(style=ButtonStyle.blue, label='Ping', emoji='🔥')
                           ]]
                       )
        response = await bot.wait_for('button_click')
        if response.channel == ctx.channel:
            if response.component.label == 'Status SALES':
                results = read_db(db='sales', table='ping')
                result = output_results(results)
                # file = open('stat/stat.txt', 'rb')
                # file.seek(-73, 2)
                # last_massege = file.read(71).decode('UTF-8')  # выводит последние 3 записи
                await ctx.send(result)

            if response.component.label == 'Status WLOSK':
                results = read_db(db='sales', table='ping_wlosk')
                result = output_results(results)
                await ctx.send(result)

            if response.component.label == 'Status STARGUN':
                results = read_db(db='sales', table='ping_stargun')
                result = output_results(results)
                await ctx.send(result)

            if response.component.label == 'Status CHAP':
                results = read_db(db='sales', table='ping_chap')
                result = output_results(results)
                await ctx.send(result)

            if response.component.label == 'Ping':
                Popen('D:/Python/_bat/sales_ping.bat')
                await channel.send('OK. Wait 1 minute.')

            await response.edit_origin()
            await asyncio.sleep(5)
            await ctx.channel.purge(limit=10)
        await response.edit_origin()


bot.run(token)
