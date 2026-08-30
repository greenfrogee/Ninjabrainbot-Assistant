import os
import discord
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)


async def check_settings(file):
    ninjabrainbot_settings = json.loads(await file.read())

    description = ""
    issues = 0

    mc_version = ninjabrainbot_settings.get("mc_version")
    crosshair_correction = ninjabrainbot_settings.get("crosshair_correction")
    pixel_adjustment_type = ninjabrainbot_settings.get("angle_adjustment_type")
    resolution_height = ninjabrainbot_settings.get("resolution_height")
    sensitivity = ninjabrainbot_settings.get("sensitivity")
    default_boat_mode = ninjabrainbot_settings.get("default_boat_type")
    boat_error = ninjabrainbot_settings.get("boat_error")
    standard_deviation_for_boat_throws = ninjabrainbot_settings.get("sigma_boat")

    if mc_version is not None and mc_version != "0":
        issues += 1
        description += "\n- Your `Minecraft version` in `Ninjabrainbot ➔ Basic` is not set to `1.9-1.18`. Change it if you aren't playing on 1.19+."

    if crosshair_correction is not None and crosshair_correction != "0.0":
        issues += 1
        description += "\n- Your `Crosshair correction` in `Ninjabrainbot ➔ Advanced` is not set to `0`."

    if pixel_adjustment_type is None and pixel_adjustment_type != "1":
        issues += 1
        description += "\n- Your `Pixel adjustment type` in `Ninjabrainbot ➔ Optional Features ➔ Angle Adjustment` is not set to `Tall Resolution`."

    if resolution_height is not None and resolution_height != "16384.0":
        issues += 1
        description += "\n- Your `Resolution height` in `Ninjabrainbot ➔ Optional features ➔ Angle Adjustment` is not set to `16384`."

    if sensitivity is None and sensitivity != "0.02291165" and sensitivity != "0.022911649":
        issues += 1
        description += "\n- Your `Sensitivity 1.13+` in `Ninjabrainbot ➔ Optional features ➔ Boat measurements` is not set to `0.02291165`."

    if default_boat_mode is None and default_boat_mode != "2":
        issues += 1
        description += "\n- Your `Default boat mode` in `Ninjabrainbot ➔ Optional features ➔ Boat measurements` is not set to `Green boat`. *Note: you will need to restart Ninjabrainbot and click Reset on the main screen for this setting to properly apply.*"

    if boat_error is not None and boat_error != "0.03":
        issues += 1
        description += "\n- Your `Allowable boat angle error` in `Ninjabrainbot ➔ Optional features ➔ Boat measurements` is not set to `0.03`."

    if standard_deviation_for_boat_throws is None and standard_deviation_for_boat_throws != "7.0/E-4":
        issues += 1
        description += "\n- Your `Standard deviation for boat throws` in `Ninjabrainbot ➔ Optional features ➔ Boat measurements` is not set to `0.0007`."

    return issues, description


async def check_options(file):
    data = (await file.read()).decode("utf-8")

    description = ""
    issues = 0
    options_sensitivity = None

    for line in data.splitlines():
        if line.startswith("mouseSensitivity:"):
            options_sensitivity = line.split(":", 1)[1]

    if (
        options_sensitivity is not None
        and options_sensitivity != "0.02291165"
        and options_sensitivity != "0.02291164919734001"
    ):
        issues += 1
        description += f"\n - Your mouseSensitivity, `{options_sensitivity}`, in `options.txt` is not set to `0.02291165`. Change it and use Ctrl + S to save."

    return issues, description


async def check_standardsettings(file):
    standardsettings = json.loads(await file.read())

    description = ""
    issues = 0

    standardsettings_sensitivity = standardsettings.get("mouseSensitivity")

    if (
        standardsettings_sensitivity is not None
        and standardsettings_sensitivity != 0.02291165
        and standardsettings_sensitivity != 0.02291164919734001
    ):
        issues += 1
        description += f"\n - Your mouseSensitivity, `{standardsettings_sensitivity}`, in `standardsettings.json` is not set to `0.02291165`. Change it and use Ctrl + S to save."

    return issues, description


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    issues = 0
    description = ""
    settings_files = 0
    standardsettings_files = 0
    options_files = 0

    filenames = [attachment.filename for attachment in message.attachments]

    content = message.content.lower()
    check_1 = "100%" in content and "wrong" in content
    check_2 = "boateye" in content and "not" in content and "working" in content

    if check_1 or check_2:
        missing_stronghold = discord.Embed(
            title="Missing the Stronghold?",
            color=discord.Color.green(),
            description="Use `/nbbdebug` to begin debugging!"
        )
        await message.reply(embed=missing_stronghold)

    if (
        "ninjabrainbot_settings_send_to_discord.json" in filenames
        or "standardsettings.json" in filenames
        or "options.txt" in filenames
    ):
        for attachment in message.attachments:
            if attachment.filename == "ninjabrainbot_settings_send_to_discord.json":
                new_issues, new_description = await check_settings(attachment)
                settings_files += 1
                issues += new_issues
                description += new_description

            if attachment.filename == "options.txt":
                new_issues, new_description = await check_options(attachment)
                options_files += 1
                issues += new_issues
                description += new_description

            if attachment.filename == "standardsettings.json":
                new_issues, new_description = await check_standardsettings(attachment)
                standardsettings_files += 1
                issues += new_issues
                description += new_description

        if issues == 0:
            title = "0 issues found"
            color = discord.Color.green()
            description += "You should be able to measure correctly!"

        else:
            title = f"{issues} issue{'s' if issues != 1 else ''} found:"
            color = discord.Color.from_str("#FF0000")

        if options_files == 0 or standardsettings_files == 0 or settings_files == 0:
            description += "\n\n\n-# *You may want to send other config files to verify all boateye settings.*"

        description += "\n-# *Still missing the Stronghold? Check `/stillmissing` for more solutions.*"

        embed = discord.Embed(
            title=title,
            color=color,
            description=description
        )

        await message.reply(embed=embed)


@tree.command(
    name="nbbdebug",
    description="Explains how to automatically debug Ninjabrainbot issues."
)
async def nbbdebug(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Ninjabrainbot Debugging",
        color=discord.Color.green(),
        description="To fix Ninjabrainbot not working, please complete the following to allow me to check them:\n- Run [this file](https://github.com/greenfrogee/Ninjabrainbot-Assistant/releases/download/exporter/export_ninjabrainbot_settings.vbs) to export your Ninjabrainbot settings. Then drag and drop the file that creates into Discord.\n - Drag and drop these files from your instance folder into Discord: `minecraft/config/mcsr/standardsettings.json` and `minecraft/options.txt`\n - It is recommended that you send all of these in **one message**."
    )
    await interaction.response.send_message(embed=embed)


@tree.command(
    name="greenboat",
    description="Explains why and how green boat is used."
)
async def greenboat(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Green Boat Explanation",
        color=discord.Color.green(),
        description="Green boat allows you to measure without having to get into a boat. This is helpful in some rare cases where you lost your boat if you didn't have one from the start. Though, this doesn't mean you should skip using a boat every time - if you turned left or right in a boat at any point of the run, you'll need to get in and out of a boat. For this reason, many players overlap this with going through a Nether Portal"
    )
    await interaction.response.send_message(embed=embed)


@tree.command(
    name="stillmissing",
    description="Gives other debugging solutions."
)
async def stillmissing(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Still Missing",
        color=discord.Color.green(),
        description="If you're still missing after changing your settings to the correct values, make sure:\n- You are measuring in accordance to [this image](https://iili.io/Cpir6n2.jpg)\n- Your +1 and -1 hotkeys are not swapped\n - You are accounting for desync ([see here](https://www.youtube.com/watch?v=uBqAeZMlEFQ) for more information)\n - You are accounting for eye wiggle ([see here](https://frontcage.com/t/what-to-do-about-eye-wiggle/14) for more information)"
    )
    await interaction.response.send_message(embed=embed)


client.run(TOKEN)