import shutil, psutil
import signal
import os
import asyncio

from pyrogram import idle
from sys import executable
from datetime import datetime
import pytz
import time

from telegram import ParseMode
from telegram.ext import CommandHandler
from telegram.error import BadRequest, Unauthorized
from wserver import start_server_async
from bot import bot, dispatcher, updater, botStartTime, IGNORE_PENDING_REQUESTS, IS_VPS, PORT, TIMEZONE, AUTHORIZED_CHATS, web, app, alive
from bot.helper.ext_utils import fs_utils
from bot.helper.telegram_helper.bot_commands import BotCommands
from bot.helper.telegram_helper.message_utils import *
from .helper.ext_utils.bot_utils import get_readable_file_size, get_readable_time
from .helper.telegram_helper.filters import CustomFilters
from bot.helper.telegram_helper import button_build
from .modules import authorize, list, cancel_mirror, mirror_status, mirror, clone, watch, shell, eval, torrent_search, delete, speedtest, count, reboot, imdb
now=datetime.now(pytz.timezone(f'{TIMEZONE}'))

def stats(update, context):
    currentTime = get_readable_time(time.time() - botStartTime)
    total, used, free = shutil.disk_usage('.')
    total = get_readable_file_size(total)
    used = get_readable_file_size(used)
    free = get_readable_file_size(free)
    sent = get_readable_file_size(psutil.net_io_counters().bytes_sent)
    recv = get_readable_file_size(psutil.net_io_counters().bytes_recv)
    cpuUsage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    stats = f'╭───『🦾 𝑩𝒐𝒕 𝑺𝒕𝒂𝒕𝒊𝒄𝒔 🦾』\n├─🤖<b>Bot Uptime:</b> {currentTime}\n' \
            f'├─💽<b>Total Disk Space:</b> {total}\n' \
            f'├─💻<b>Used:</b> {used} │ ' \
            f'├─💾<b>Free:</b> {free}\n│\n' \
            f'├─🛰️Data Usage\n├─📤<b>Upload:</b> {sent}\n' \
            f'├─📥<b>Download:</b> {recv}\n│\n' \
            f'├─🖥️<b>CPU:</b> {cpuUsage}%\n' \
            f'├─📏<b>RAM:</b> {memory}%\n' \
            f'╰─💿<b>DISK:</b> {disk}%'
    sendMessage(stats, context.bot, update)


def start(update, context):
    buttons = button_build.ButtonMaker()
    buttons.buildbutton("Channel", "https://t.me/+SpnPh2Gc8kHwwAAF")
    reply_markup = InlineKeyboardMarkup(buttons.build_menu(2))
    if CustomFilters.authorized_user(update) or CustomFilters.authorized_chat(update):
        start_string = f'''
This bot can mirror all your links to Google Drive!
Type /{BotCommands.HelpCommand} to get a list of available commands
'''
        sendMarkup(start_string, context.bot, update, reply_markup)
    else:
        sendMarkup(
            '🤬<b>Chalaja BSDK</b>🤬.',
            context.bot,
            update,
            reply_markup,
        )


def restart(update, context):
    restart_message = sendMessage("Restarting, Please wait!", context.bot, update)
    # Save restart message object in order to reply to it after restarting
    with open(".restartmsg", "w") as f:
        f.truncate(0)
        f.write(f"{restart_message.chat.id}\n{restart_message.message_id}\n")
    fs_utils.clean_all()
    alive.terminate()
    web.terminate()
    os.execl(executable, executable, "-m", "bot")


def ping(update, context):
    start_time = int(round(time.time() * 1000))
    reply = sendMessage("Starting Ping", context.bot, update)
    end_time = int(round(time.time() * 1000))
    editMessage(f'{end_time - start_time} ms', reply)


def log(update, context):
    sendLogFile(context.bot, update)


def bot_help(update, context):
    help_string_adm = f'''
/{BotCommands.HelpCommand}: To get this message

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Start mirroring the link to Google Drive. Use /{BotCommands.MirrorCommand} qb to mirror with qBittorrent, and use /{BotCommands.MirrorCommand} qbs to select files before downloading

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Start mirroring and upload the archived (.tar) version of the download

/{BotCommands.ZipMirrorCommand} [download_url][magnet_link]: Start mirroring and upload the archived (.zip) version of the download

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Starts mirroring and if downloaded file is any archive, extracts it to Google Drive

/{BotCommands.CloneCommand} [drive_url]: Copy file/folder to Google Drive

/{BotCommands.CountCommand} [drive_url]: Count file/folder of Google Drive Links

/{BotCommands.DeleteCommand} [drive_url]: Delete file from Google Drive (Only Owner & Sudo)

/{BotCommands.WatchCommand} [yt-dlp supported link]: Mirror through yt-dlp. Click /{BotCommands.WatchCommand} for more help

/{BotCommands.TarWatchCommand} [yt-dlp supported link]: Mirror through yt-dlp and tar before uploading

/{BotCommands.CancelMirror}: Reply to the message by which the download was initiated and that download will be cancelled

/{BotCommands.CancelAllCommand}: Cancel all running tasks

/{BotCommands.ListCommand} [search term]: Searches the search term in the Google Drive, If found replies with the link

/{BotCommands.StatusCommand}: Shows a status of all the downloads

/{BotCommands.StatsCommand}: Show Stats of the machine the bot is hosted on

/{BotCommands.PingCommand}: Check how long it takes to Ping the Bot

/{BotCommands.AuthorizeCommand}: Authorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.UnAuthorizeCommand}: Unauthorize a chat or a user to use the bot (Can only be invoked by Owner & Sudo of the bot)

/{BotCommands.AuthorizedUsersCommand}: Show authorized users (Only Owner & Sudo)

/{BotCommands.AddSudoCommand}: Add sudo user (Only Owner)

/{BotCommands.RmSudoCommand}: Remove sudo users (Only Owner)

/{BotCommands.RestartCommand}: Restart the bot

/{BotCommands.LogCommand}: Get a log file of the bot. Handy for getting crash reports

/{BotCommands.SpeedCommand}: Check Internet Speed of the Host

/{BotCommands.ShellCommand}: Run commands in Shell (Terminal)

/{BotCommands.ExecHelpCommand}: Get help for Executor module (Only Owner)

/{BotCommands.TsHelpCommand}: Get help for Torrent search module
'''

    help_string = f'''
/{BotCommands.HelpCommand}: To get this message

/{BotCommands.MirrorCommand} [download_url][magnet_link]: Start mirroring the link to Google Drive. Use /{BotCommands.MirrorCommand} qb to mirror with qBittorrent, and use /{BotCommands.MirrorCommand} qbs to select files before downloading

/{BotCommands.TarMirrorCommand} [download_url][magnet_link]: Start mirroring and upload the archived (.tar) version of the download

/{BotCommands.ZipMirrorCommand} [download_url][magnet_link]: Start mirroring and upload the archived (.zip) version of the download

/{BotCommands.UnzipMirrorCommand} [download_url][magnet_link]: Starts mirroring and if downloaded file is any archive, extracts it to Google Drive

/{BotCommands.CloneCommand} [drive_url]: Copy file/folder to Google Drive

/{BotCommands.CountCommand} [drive_url]: Count file/folder of Google Drive Links

/{BotCommands.WatchCommand} [yt-dlp supported link]: Mirror through yt-dlp. Click /{BotCommands.WatchCommand} for more help

/{BotCommands.TarWatchCommand} [yt-dlp supported link]: Mirror through yt-dlp and tar before uploading

/{BotCommands.CancelMirror}: Reply to the message by which the download was initiated and that download will be cancelled

/{BotCommands.ListCommand} [search term]: Searches the search term in the Google Drive, If found replies with the link

/{BotCommands.StatusCommand}: Shows a status of all the downloads

/{BotCommands.StatsCommand}: Show Stats of the machine the bot is hosted on

/{BotCommands.PingCommand}: Check how long it takes to Ping the Bot

/{BotCommands.TsHelpCommand}: Get help for Torrent search module
'''

    if CustomFilters.sudo_user(update) or CustomFilters.owner_filter(update):
        sendMessage(help_string_adm, context.bot, update)
    else:
        sendMessage(help_string, context.bot, update)


botcmds = [
        (f'{BotCommands.HelpCommand}','Get Detailed Help'),
        (f'{BotCommands.MirrorCommand}', 'Start Mirroring'),
        (f'{BotCommands.TarMirrorCommand}','Start mirroring and upload as .tar'),
        (f'{BotCommands.ZipMirrorCommand}','Start mirroring and upload as .zip'),
        (f'{BotCommands.UnzipMirrorCommand}','Extract files'),
        (f'{BotCommands.CloneCommand}','Copy file/folder to Drive'),
        (f'{BotCommands.CountCommand}','Count file/folder of Drive link'),
        (f'{BotCommands.DeleteCommand}','Delete file from Drive'),
        (f'{BotCommands.WatchCommand}','Mirror yt-dlp support link'),
        (f'{BotCommands.TarWatchCommand}','Mirror Youtube playlist link as .tar'),
        (f'{BotCommands.CancelMirror}','Cancel a task'),
        (f'{BotCommands.CancelAllCommand}','Cancel all tasks'),
        (f'{BotCommands.ListCommand}','Searches files in Drive'),
        (f'{BotCommands.StatusCommand}','Get Mirror Status message'),
        (f'{BotCommands.StatsCommand}','Bot Usage Stats'),
        (f'{BotCommands.PingCommand}','Ping the Bot'),
        (f'{BotCommands.RestartCommand}','Restart the bot [owner/sudo only]'),
        (f'{BotCommands.LogCommand}','Get the Bot Log [owner/sudo only]'),
        (f'{BotCommands.TsHelpCommand}','Get help for Torrent search module')
    ]


def main():
    # Heroku restarted
    GROUP_ID = os.environ.get("AUTHORIZED_CHATS")
    kie = datetime.now(pytz.timezone(f'{TIMEZONE}'))
    jam = kie.strftime('\n📅 Date: %d/%m/%Y\n⏲️ Time: %I:%M%P')
    if GROUP_ID is not None and isinstance(GROUP_ID, str):        
        try:
            dispatcher.bot.sendMessage(f"{GROUP_ID}", f"♻️ Rebooted ♻️\n{jam}\n\nPlease Re-Download again \n\n#Restarted")
        except Unauthorized:
            LOGGER.warning(
                "Bot isnt able to send message to support_chat, go and check!"
            )
        except BadRequest as e:
            LOGGER.warning(e.message)
    
    fs_utils.start_cleanup()

    if IS_VPS:
        asyncio.get_event_loop().run_until_complete(start_server_async(PORT))

    # Check if the bot is restarting
    if os.path.isfile(".restartmsg"):
        with open(".restartmsg") as f:
            chat_id, msg_id = map(int, f)
        bot.edit_message_text("Restarted successfully!", chat_id, msg_id)
        os.remove(".restartmsg")
    bot.set_my_commands(botcmds)

    start_handler = CommandHandler(BotCommands.StartCommand, start, run_async=True)
    ping_handler = CommandHandler(BotCommands.PingCommand, ping,
                                  filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    restart_handler = CommandHandler(BotCommands.RestartCommand, restart,
                                     filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    help_handler = CommandHandler(BotCommands.HelpCommand,
                                  bot_help, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    stats_handler = CommandHandler(BotCommands.StatsCommand,
                                   stats, filters=CustomFilters.authorized_chat | CustomFilters.authorized_user, run_async=True)
    log_handler = CommandHandler(BotCommands.LogCommand, log, filters=CustomFilters.owner_filter | CustomFilters.sudo_user, run_async=True)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(ping_handler)
    dispatcher.add_handler(restart_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(stats_handler)
    dispatcher.add_handler(log_handler)
    updater.start_polling(drop_pending_updates=IGNORE_PENDING_REQUESTS)
    LOGGER.info("Bot Started!")
    signal.signal(signal.SIGINT, fs_utils.exit_clean_up)

app.start()
main()
idle()