import asyncio
import traceback
from typing import Callable, Coroutine

from app import Config, bot
from app.core import filters
from app.core.media_handler import MediaHandler
from app.core.message import Message, Msg


@bot.add_cmd(cmd="dl")
async def dl(bot: bot, message: Message):
    reply: Message = await bot.send_message(
        chat_id=message.chat.id, text="`trying to download...`"
    )
    coro: Coroutine = MediaHandler.process(message)
    task: asyncio.Task = asyncio.Task(coro, name=reply.task_id)
    media: MediaHandler = await task
    if media.exceptions:
        exceptions: str = "\n".join(media.exceptions)
        await bot.log(
            traceback=exceptions,
            func="DL",
            chat=message.chat.title or message.chat.first_name,
            name="traceback.txt",
        )
        return await reply.edit(f"Media Download Failed.")
    if media.media_objects:
        await message.delete()
    await reply.delete()


@bot.on_message(filters.user_filter)
@bot.on_edited_message(filters.user_filter)
async def cmd_dispatcher(bot: bot, message: Msg):
    message: Message = Message.parse_message(message)
    func: Callable = Config.CMD_DICT[message.cmd]
    coro: Coroutine = func(bot, message)
    try:
        task: asyncio.Task = asyncio.Task(coro, name=message.task_id)
        await task
    except asyncio.exceptions.CancelledError:
        await bot.log(text=f"<b>#Cancelled</b>:\n<code>{message.text}</code>")
    except BaseException:
        await bot.log(
            traceback=str(traceback.format_exc()),
            chat=message.chat.title or message.chat.first_name,
            func=func.__name__,
            name="traceback.txt",
        )


@bot.on_message(filters.convo_filter, group=0)
@bot.on_edited_message(filters.convo_filter, group=0)
async def convo_handler(bot: bot, message: Msg):
    conv_dict: dict = Config.CONVO_DICT[message.chat.id]
    conv_filters = conv_dict.get("filters")
    if conv_filters:
        check = await conv_filters(bot, message)
        if not check:
            message.continue_propagation()
        conv_dict["response"] = message
        message.continue_propagation()
    conv_dict["response"] = message
    message.continue_propagation()


@bot.on_message(filters.allowed_cmd_filter)
@bot.on_message(filters.chat_filter)
async def dl_dispatcher(bot: bot, message: Msg):
    message: Message = Message.parse_message(message)
    coro: Coroutine = dl(bot, message)
    try:
        task: asyncio.Task = asyncio.Task(coro, name=message.task_id)
        await task
    except asyncio.exceptions.CancelledError:
        await bot.log(text=f"<b>#Cancelled</b>:\n<code>{message.text}</code>")
    except BaseException:
        await bot.log(
            traceback=str(traceback.format_exc()),
            chat=message.chat.title or message.chat.first_name,
            func=dl.__name__,
            name="traceback.txt",
        )
