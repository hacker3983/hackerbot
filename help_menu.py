import discord

def get_help_menu():
    embed = discord.Embed(title="Hackerbot's commands",
                description="Use `hackerbot {command}` format inorder to utalize each command\n**Commands:**",
                color=discord.Color.random())
    embed.add_field(name="crypto `<optional argument>`", value="Utalize available cryptography functions", inline=False)
    embed.add_field(name="osint `<optional argument>`", value="Utalize available osint (open source intelligence) functionality", inline=False)
    embed.add_field(name="revshell", value="Reverse shell generator", inline=False)
    embed.add_field(name="ctf `<optional argument>`",
                        value="Play ctf challenges using `play` option and submit using `submit` option", inline=False)
    embed.add_field(name="whoami", value="Display who you are your user profile", inline=False)
    embed.add_field(name="todo `<optional argument>`", value="Todo list", inline=False)
    embed.set_image(url="https://f.hubspotusercontent40.net/hubfs/4650993/New_Avast_Academy/Hackers/Hacker-Thumb-a1.png")
    return embed

