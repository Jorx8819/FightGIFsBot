import discord
import os
import random 
from discord.ext import commands

# --- VARIABLES GLOBALES DEL JUEGO ---
SESIONES_DE_LUCHA = {}

# Base de Datos de Ataques con sus GIFs y rango de daño (mínimo, máximo)
ATAQUES = {
    'puño': {
        'daño': (10, 15),
        'gifs': [
            'https://media.giphy.com/media/l41JKwO5xX86i5yY8/giphy.gif', 
            'https://media.giphy.com/media/d2YWtoqQd7c6oGk8/giphy.gif', 
        ]
    },
    'patada': {
        'daño': (15, 25),
        'gifs': [
            'https://media.giphy.com/media/l0HlCqV3gYqjVq3sA/giphy.gif', 
            'https://media.giphy.com/media/l2JdVRH7iB0jB8mFG/giphy.gif', 
        ]
    },
}

# --- CONFIGURACIÓN DEL BOT ---

TOKEN = os.environ['DISCORD_TOKEN']

intents = discord.Intents.default()
intents.message_content = True 
intents.members = True 

bot = commands.Bot(command_prefix='!', intents=intents)

# --- EVENTOS ---

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    print('¡Listo para la pelea!')

# --- COMANDOS DEL JUEGO ---

@bot.command(name='pelea')
async def iniciar_pelea(ctx, oponente: discord.Member):
    canal_id = str(ctx.channel.id)

    if canal_id in SESIONES_DE_LUCHA:
        await ctx.send("Ya hay una pelea activa en este canal. ¡Termina esa primero!")
        return

    if oponente.bot or oponente == ctx.author:
        await ctx.send("No puedes pelear contra ti mismo ni contra un bot, ¡busca un rival digno!")
        return

    jugador_A = ctx.author
    jugador_B = oponente

    SESIONES_DE_LUCHA[canal_id] = {
        'jugador_A': jugador_A.id,
        'jugador_B': jugador_B.id,
        'turno': jugador_A.id, 
        'hp_A': 100,
        'hp_B': 100,
    }

    mensaje = (
        f"**¡COMIENZA LA LUCHA!** ⚔️\n"
        f"{jugador_A.mention} vs {jugador_B.mention}\n"
        f"Ambos inician con **100 HP**.\n"
        f"Es el turno de {jugador_A.mention}. Usa un ataque: `!puño` o `!patada`."
    )
    await ctx.send(mensaje)

@bot.command(name='puño')
@bot.command(name='patada')
async def ataque(ctx):
    canal_id = str(ctx.channel.id)
    jugador_actual_id = ctx.author.id

    if canal_id not in SESIONES_DE_LUCHA:
        await ctx.send("No hay ninguna pelea activa en este canal. Usa `!pelea @usuario` para comenzar.")
        return

    sesion = SESIONES_DE_LUCHA[canal_id]

    if jugador_actual_id == sesion['jugador_A']:
        oponente_key = 'B'
        jugador_oponente = bot.get_user(sesion['jugador_B'])
    elif jugador_actual_id == sesion['jugador_B']:
        oponente_key = 'A'
        jugador_oponente = bot.get_user(sesion['jugador_A'])
    else:
        await ctx.send("No estás participando en esta pelea.")
        return

    if jugador_actual_id != sesion['turno']:
        await ctx.send(f"¡Espera tu turno, {ctx.author.mention}! No puedes atacar ahora.")
        return

    tipo_ataque = ctx.invoked_with.lower() 
    datos_ataque = ATAQUES.get(tipo_ataque)

    if not datos_ataque:
        return 

    min_dmg, max_dmg = datos_ataque['daño']
    daño_infligido = random.randint(min_dmg, max_dmg)
    gif_ataque = random.choice(datos_ataque['gifs'])

    hp_oponente_key = f'hp_{oponente_key}'
    sesion[hp_oponente_key] -= daño_infligido

    if sesion[hp_oponente_key] <= 0:
        await ctx.send(gif_ataque) 
        mensaje_final = (
            f"**¡KO!** 🏆\n"
            f"{ctx.author.mention} golpea con un **{tipo_ataque.upper()}** por **{daño_infligido} HP**.\n"
            f"La salud de {jugador_oponente.mention} cae a **0 HP**.\n"
            f"**¡{ctx.author.mention} ES EL GANADOR!**"
        )
        await ctx.send(mensaje_final)

        del SESIONES_DE_LUCHA[canal_id]
        return

    mensaje_ataque = (
        f"**{ctx.author.mention}** usa **{tipo_ataque.upper()}** y golpea a {jugador_oponente.mention} por **{daño_infligido} HP**.\n"
        f"HP restante de {jugador_oponente.mention}: **{sesion[hp_oponente_key]} HP**."
    )

    await ctx.send(gif_ataque) 
    await ctx.send(mensaje_ataque)

    sesion['turno'] = jugador_oponente.id
    await ctx.send(f"Es el turno de {jugador_oponente.mention}. ¡Responde!")

bot.run(TOKEN)
