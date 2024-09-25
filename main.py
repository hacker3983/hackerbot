import discord
import rotlib
import base64
import random
import hashlib
import json
import hash_decrypt as hd
from help_menu import get_help_menu
import webserver
import os
import requests
import re

if not os.path.isfile("rockyou.txt"):
    print("Downloading \u001b[31mrockyou.txt\u001b[0m wordlist...");
    r = requests.get("https://www.mediafire.com/file/mw9lhg82jtziocv/rockyou.txt/file")
    rockyou_downloadlink = re.search("href=\"https://.*download.*media.*txt", r.text).group()[6:]
    os.system(f"curl -s {rockyou_downloadlink} -o rockyou.txt")

md5_dict = hd.md5load_dictionary("rockyou.txt")
print(md5_dict[0].decode().strip())

if not os.path.isfile("token.txt"):
    print("Please create the token.txt file before executing the bot")
    exit(-1)
with open("token.txt") as f:
    token = f.read()

todo_list = {}
if os.path.isfile("todolist-data.json"):
    with open("todolist-data.json", "r") as f:
        users_data = f.read()
        todo_list = json.loads(users_data)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = discord.Client(intents=intents)
author = None
with open("flags.txt") as f:
    flags = f.readlines()


def todo_add(author, data):
    global todo_list
    if author in todo_list:
        todo_list[author].append(data)
    else:
        todo_list[author] = [data]
    with open("todolist-data.json", "w") as f:
        f.write(json.dumps(todo_list))


def todo_remove(author, task):
    global todo_list
    todo_list[author].pop(task)
    with open("todolist-data.json", "w") as f:
        f.write(json.dumps(todo_list))


def todo_clear(author):
    global todo_list
    todo_list[author] = []
    with open("todolist-data.json", "w") as f:
        f.write(json.dumps(todo_list))


@client.event
async def on_ready():
    global author
    await client.change_presence(
        activity=discord.Game('hackerbot / hackerbot help'))
    print("Logged in successfully as", client.user)


rot_interr = "`CommandError: command execution failure expected argument \"rot algorithm\" to be an integer`"
rot_strerr = "`CommandError: command execution failure missing argument \"text\"`"


async def bruteforce_hash(message, hash, algorithm):
    passwd = None
    await message.channel.send(
        f"Bruteforcing {algorithm}...\nPlease wait until the process completes you will be notified when it is done."
    )
    if algorithm == "md5":
        passwd = hd.md5brute_force(hash, md5_dict)
        if passwd == None:
            await message.channel.send(
                "No password matches found in my database.")
        else:
            await message.channel.send(
                f"Password found: {passwd.decode().strip()}")


async def send_error(error_message, message):
    await message.channel.send(
        f"CommandError: `command execution failure {error_message}`")


@client.event
async def on_message(message):
    user = message.author.name + "#" + message.author.discriminator
    print(message.content)
    msg = message.content
    command = message.content.split()
    cmd_len = len(command)
    if cmd_len > 0:
        if command[0] == "hackerbot" and cmd_len > 1:
            if command[1] == "help":
                embed = get_help_menu()
                await message.channel.send(embed=embed)
            elif command[1] == "crypto":
                if cmd_len > 2:
                    if command[2] == "rot":
                        if cmd_len > 4:
                            if command[3] == "bruteforce":
                                try:
                                    msg_index = msg.find("bruteforce") + 10
                                    msg_index += count_spacef(msg[msg_index:])
                                    msg = msg[msg_index:].replace("`", "")
                                    output = "```"
                                    for i in range(1, 27):
                                        output += f"Rot {i}: {rotlib.encode(i, msg)}\n"
                                    output += "```"
                                    embed = discord.Embed(
                                        title="Rot Algorithm's result:",
                                        description=f"{output}",
                                        color=discord.Color.random())
                                    await message.channel.send(embed=embed)
                                except:
                                    await message.channel.send(rot_strerr)
                            else:
                                try:
                                    rot = int(command[3])
                                    if not (rot >= 1 and rot <= 26):
                                        await message.channel.send(
                                            "Sorry but the rot algorithm you select should be in the range of 1-26 inclusively"
                                        )
                                    else:
                                        msg_index = msg.find("rot") + 4 + len(
                                            command[3])
                                        msg_index += count_spacef(
                                            msg[msg_index:])
                                        msg = msg[msg_index:].replace(
                                            "```", "")
                                        enc_msg = rotlib.encode(rot, msg)
                                        embed = discord.Embed(
                                            title=
                                            f"Rot {rot} encoded / decoded text",
                                            description=f"```{enc_msg}```",
                                            color=discord.Color.random())
                                        await message.channel.send(embed=embed)
                                except:
                                    await message.channel.send(rot_interr)
                        elif cmd_len == 4:
                            await message.channel.send(rot_strerr)
                        else:
                            embed = discord.Embed(
                                title="Rot command options",
                                description=
                                """Example of using rot command: `hackerbot crypto rot 13 Hello`
List of rot command options:
""",
                                color=discord.Color.random())
                            embed.add_field(name="`<1-26>`",
                                            value="Rot algorithm",
                                            inline=False)
                            embed.add_field(name="`<text>`",
                                            value="Text",
                                            inline=False)
                            embed.add_field(
                                name="bruteforce `<text>`",
                                value=
                                "Try every combination or rot algorithm on the given text",
                                inline=False)
                            await message.channel.send(embed=embed)
                    elif command[2] == "base64":
                        if cmd_len == 4:
                            await message.channel.send(
                                "`CommandError: command execution failure missing argument \"text\"`"
                            )
                        elif cmd_len > 4:
                            try:
                                opt_type = "Base64 encoded text"
                                if command[3] == "encode":
                                    msg_index = msg.find("encode") + 6
                                    msg_index += count_spacef(msg[msg_index:])
                                    msg = msg[msg_index:].replace("```", "")
                                    result = base64.b64encode(
                                        msg.encode()).decode()
                                elif command[3] == "decode":
                                    opt_type = "Base64 decoded text"
                                    msg_index = msg.find("decode") + 6
                                    msg_index += count_spacef(msg[msg_index:])
                                    msg = msg[msg_index:].replace("```", "")
                                    result = base64.b64decode(
                                        msg).decode().replace("```", "")
                                else:
                                    await send_error(
                                        f"Unknown option \"{command[3]}\"")
                                if command[3] == "encode" or command[
                                        3] == "decode":
                                    embed = discord.Embed(
                                        title=f"{opt_type}",
                                        description=f"```{result}```")
                                    await message.channel.send(embed=embed)
                            except:
                                await message.channel.send(
                                    "`CommandError: command execution failure failed to decode given base64 text`"
                                )
                        else:
                            embed = discord.Embed(
                                title="Base64 Encoder / Decoder",
                                description=
                                "Encode or decode the given text in base64")
                            embed.add_field(name="encode `<text>`",
                                            value="encode the given text")
                            embed.add_field(
                                name="decode `<text>`",
                                value="decode the given base64 text")
                            await message.channel.send(embed=embed)
                    elif command[2] == "random":
                        if cmd_len == 4:
                            try:
                                n = int(command[3])
                                await message.channel.send(
                                    f"Your randomly generated number is: `{random.randint(0, n)}`"
                                )
                            except:
                                await message.channel.send(
                                    "`CommandError: command execution failure expected argument \"n\" to be an integer`"
                                )
                        else:
                            embed = discord.Embed(
                                title="Random",
                                description=
                                "Generates a random number base on the given number n. The number generated is from `0-n`"
                            )
                            embed.add_field(
                                name="`<n>`",
                                value=
                                "A integer which is used to generate the random number from `0-n`"
                            )
                            await message.channel.send(embed=embed)
                    elif command[2] == "md5":
                        # hackerbot crypto md5 encode <text>
                        if cmd_len == 4:
                            await send_error("Missing argument \"text\"",
                                             message)
                        elif cmd_len > 4:
                            result = ""
                            if command[3] == "encrypt":
                                msg_index = msg.find("encrypt") + 7
                                msg_index += count_spacef(msg[msg_index:])
                                msg = msg[msg_index:]
                                result = hashlib.md5(msg.encode()).hexdigest()
                            elif command[3] == "bdecrypt":
                                msg_index = msg.find("decrypt") + 8
                                msg_index += count_spacef(msg[msg_index:])
                                msg = msg[msg_index:]
                                await bruteforce_hash(message, msg, "md5")
                            else:
                                await send_error(
                                    f"Unknown option \"{command[3]}\"")
                            if command[3] == "encrypt":
                                embed = discord.Embed(
                                    title=f"MD5 {command[3]}",
                                    description=f"`{result}`")
                                await message.channel.send(embed=embed)
                        else:
                            embed = discord.Embed(
                                title="MD5 (Message digest algorithm 5)",
                                description=
                                "Encrypt or decrypt md5 (bdecrypt option is used to try to bruteforce the given hash or decrypt)"
                            )
                            embed.add_field(name="encrypt `<text>`",
                                            value="Encrypt the given text")
                            embed.add_field(
                                name="bdecrypt `<text>`",
                                value="Decrypt the given text by bruteforcing")
                            await message.channel.send(embed=embed)
                    elif command[2] == "vigenere":
                        pass
                    elif command[2] == "hex":
                        if cmd_len == 4:
                            await send_error("Missing argument \"text\"",
                                             message)
                        elif cmd_len > 4:
                            try:
                                if command[3] == "encode":
                                    msg_index = msg.find("encode") + 6
                                    msg_index += count_spacef(msg[msg_index:])
                                    msg = msg[msg_index:].replace("```", "")
                                    result = msg.encode().hex()
                                elif command[3] == "decode":
                                    msg_index = msg.find("decode") + 6
                                    msg_index += count_spacef(msg[msg_index:])
                                    msg = msg[msg_index:].replace("```", "")
                                    result = b"".fromhex(msg).decode()
                                else:
                                    await send_error(
                                        f"Unknown option \"{command[3]}\"",
                                        message)
                                if command[3] == "encode" or command[
                                        3] == "decode":
                                    embed = discord.Embed(
                                        title=
                                        "Hexadecimal encoded / decoded result:",
                                        description=f"```{result}```")
                                    await message.channel.send(embed=embed)
                            except:
                                await send_error(
                                    "failed to decode the given text", message)
                        else:
                            embed = discord.Embed(
                                title="Hexadecimal Encoder and Decoder",
                                description=
                                "Encode or Decode the given text or hexadecimal text",
                                color=discord.Color.random())
                            embed.add_field(
                                name="encode `<text>`",
                                value="encodes the given text into hexadecimal"
                            )
                            embed.add_field(
                                name="decode `<hex text>`",
                                value=
                                "decodes the given hexadecimal text into text")
                            await message.channel.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="Cryptography commands",
                        description=
                        "List of cryptography functions to use. inorder to utalize the cryptography functions below use the command format `hackerbot crypto {function}`",
                        color=discord.Color.random())
                    embed.add_field(
                        name="rot `<1-26>` `text`",
                        value=
                        "Encode or decode the given text in a given rot algorithm supported rot algorithms are rot 1-26",
                        inline=False)
                    embed.add_field(
                        name="random `<n>`",
                        value=
                        "Generates a random number based on the given number `n`",
                        inline=False)
                    embed.add_field(
                        name="base64 `<encode or decode option>` `<text>`",
                        value="Base64 encoder and decoder",
                        inline=False)
                    embed.add_field(
                        name="vigenere `<text>` `<key>`",
                        value="Vigenere cipher encoder and decoder",
                        inline=False)
                    embed.add_field(
                        name="md5 `<encrypt or bdecrypt option>` `<text>`",
                        value=
                        "Encrypt or bruteforce the given text or hash based on the hash option"
                    )
                    embed.add_field(
                        name="hex `<encode or decode option> <text>`",
                        value="Hexadecimal encoder and decoder",
                        inline=False)
                    embed.set_image(
                        url=
                        "https://www.qinetiq.com/-/media/3e96ea63659b438f94eb2a368602a4dd.ashx?h=500&optimize=0&w=1110&la=en&hash=403B4FFA08D7698B3A1B49AA8375FF5C"
                    )
                    await message.channel.send(embed=embed)
            elif command[1] == "osint":
                await message.channel.send(
                    "The command has not been implemented yet")
            elif command[1] == "revshell":
                await message.channel.send(
                    "The command has not been implemented yet")
            elif command[1] == "ctf":
                if cmd_len > 2:
                    if command[2] == "play":
                        await message.channel.send(
                            "You can play our ctf challenges by visiting the link https://challenges.shadowbrokers.repl.co/"
                        )
                    elif command[2] == "submit":
                        try:
                            if command[3] + "\n" in flags:
                                await message.channel.send("Good Job!")
                            else:
                                await message.channel.send(
                                    "Sorry but that flag isn't correct")
                        except:
                            await message.channel.send(
                                "Please specify the flag")
                else:
                    embed = discord.Embed(
                        title="CTF",
                        description=
                        "Play and Submit flags for our ctf challenges")
                    embed.add_field(
                        name="play",
                        value="Show the link inorder to play our ctf challenges"
                    )
                    embed.add_field(
                        name="submit `<FLAG>`",
                        value=
                        "Submit a flag you found for one of our ctf challenges"
                    )
                    await message.channel.send(embed=embed)
            elif command[1] == "whoami":
                embed = discord.Embed(title=message.author,
                                      color=discord.Color.random())
                embed.add_field(name="ID", value=f"{message.author.id}")
                embed.add_field(name="Account Created",
                                value=message.author.created_at)
                embed.add_field(name="Joined Server At",
                                value=message.author.joined_at)
                embed.set_thumbnail(url=message.author.avatar_url)
                await message.channel.send(embed=embed)
            elif command[1] == "todo":
                # hackerbot todo add <text>
                if cmd_len == 3:
                    if command[2] == "show":
                        if user in todo_list:
                            result = "```\n"
                            tasks = todo_list[user]
                            for i in range(0, len(tasks)):
                                result += f"{i+1}.{tasks[i]}\n"
                            result += "```"
                            await message.channel.send(result)
                        else:
                            await send_error(
                                "sorry but your username isn't in the database",
                                message)
                    elif command[2] == "clear":
                        if user in todo_list:
                            todo_clear(user)
                            await message.channel.send(
                                "Successfully cleared all tasks from the todo list"
                            )
                        else:
                            await send_error(
                                "sorry but your username isn't in the database",
                                message)
                    else:
                        await message.channel.send(
                            "Please specify the task or task number to add or remove (remove and mark the task as done in the todo list)"
                        )
                elif cmd_len > 3:
                    if command[2] == "add":
                        msg_index = msg.find("add") + 3
                        msg_index += count_spacef(msg[msg_index:])
                        msg = msg[msg_index:].replace("```", "")
                        todo_add(user, msg)
                        await message.channel.send(
                            "Your task has been added to the todo list")
                    elif command[2] == "remove":
                        msg_index = msg.find("remove") + 6
                        msg_index += count_spacef(msg[msg_index:])
                        msg = msg[msg_index:].replace("```", "")
                        if user in todo_list:
                            try:
                                task = int(msg) - 1
                                todo_remove(user, task)
                                await message.channel.send(
                                    "Successfully removed your task from the todo list"
                                )
                            except IndexError:
                                await send_error(
                                    f"the given task number is invalid based on your number of tasks",
                                    message)
                            except ValueError:
                                await send_error(
                                    "the task number should be an integer",
                                    message)
                        else:
                            await send_error(
                                "sorry but your username isn't in the database",
                                message)
                else:
                    embed = discord.Embed(title="TODO",
                                          description="Todo list")
                    embed.add_field(
                        name="add `<text>`",
                        value="Add the given task to the todo lists database")
                    embed.add_field(
                        name="remove `<number>`",
                        value=
                        "Remove the given task number associated with the task in the todo list"
                    )
                    embed.add_field(
                        name="clear",
                        value="Clears all tasks from the todo list")
                    embed.add_field(name="show",
                                    value="Shows the tasks in the todo list")
                    await message.channel.send(embed=embed)
        elif command[0] == "hackerbot":
            embed = get_help_menu()
            await message.channel.send(embed=embed)


# counts the spaces at the front of a given text
def count_spacef(text):
    count = 0
    for char in text:
        if char != " ":
            break
        count += 1
    return count


webserver.keep_alive()
client.run(token)

