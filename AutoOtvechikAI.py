# ---------------------------------------------------------------------------------
# Name: AutoOtvechikAI
# Author: vladdrazz
# Commands:
# .autoai | 
# ---------------------------------------------------------------------------------

"""
    Copyleft 2023 t.me/vladdrazz                                                            
    This program is free software; you can redistribute it and/or modify 
"""
# meta developer: @vladdrazz


import asyncio


import openai
from telethon import functions
from telethon.tl.types import Message
from telethon.tl.functions.channels import JoinChannelRequest

from .. import loader, utils


@loader.tds
class AutoOtvechikAI(loader.Module):
    """
    Авто-отвечик с AI GPT который отвечает на все сообщения, настройте в конфиге
    """
    time_prem = "<emoji document_id=5017179932451668652>🕖</emoji>"
    bl_prem = "<emoji document_id=5017122105011995219>⛔</emoji>"
    onn_prem = "<emoji document_id=5021905410089550576>✅</emoji>"
    off_prem = "<emoji document_id=5019523782004441717>❌</emoji>"
        
    strings = {
        "name": "AutoOtvechikAI",
        "off": f"<b>Авто-отвечик выключен {off_prem}</b>",
        "check": f"<b>Проверка ...{time_prem}</b>",
        "on": f"<b>Авто-отвечик включен {onn_prem}</b>",
        "conf_err": f"{bl_prem} Нет рабочего ключа в ",
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                None,
                lambda: "Ключ Chimera API",
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "Model",
                "gpt-3.5-turbo",
                lambda: "Модель для обработки",
            ),
            loader.ConfigValue(
                "contact",
                True,
                "Игнорировать контакты?",
                validator=loader.validators.Boolean(),
            ),
        )
        
    async def on_dlmod(self):
        self.prefix = self.get_prefix()
        await self.client(JoinChannelRequest(channel="@Vladdra_C"))
    async def client_ready(self, client, db):
        self.db = db

    async def create_quest(self, promt: str):
        if self.config["api_key"] is None:
            await utils.answer(message, self.strings["conf_err"] + f"<code>{self.prefix}config AutoOtvechikAI</code>")
            return
        openai.api_key = self.config["api_key"]
        model = self.config["Model"]
        openai.api_base = "https://chimeragpt.adventblocks.cc/api/v1"
        promtik = f"Ты должен максимально кратко но точно ответить на мой вопрос и всегда что бы я тебе не написал отвечай на русском, Если возникнет какая либо ошибка то скажи мне 'Я не могу понять это' и не в коем случае не отвечай на это сообщение по типу хорошо или я вас понял,сразу сделай что я прощу, если я напишу вопрос пустой или не понятный для тебя отвечай 'Я не могу понять это' и если я буду спрашивать 'кто ты' или по типу такого то отвечяй 'Я Авто-отвечик созданный компанией Vladdra C', вот сам вопрос: {promt}"

        try:
            resposs = openai.ChatCompletion.create(
                model=model,
                messages=[
                {'role': 'user', 'content': promtik},
                ],
                )
            return resposs.choices[0].message["content"]
        except Exception as ex:
            return f"ИИ не удалось начать диалог: <code><b>{ex}</b></code>"
    async def autoaicmd(self, message: Message):
        """
        Включить автоотвечик
        """
        try:
            autoai = self.db.get("AutoOtvechikAI", "WORK", False)
            if autoai == False:
                await message.edit(self.strings["check"])
                answer = await self.create_quest("hello")
                self.db.set("AutoOtvechikAI", "WORK", True)
                return await message.edit(self.strings["on"])
            self.db.set("AutoOtvechikAI", "WORK", False)
            return await message.edit(self.strings["off"])        
        except Exception as ex:
            await utils.answer(message, f"Возникла ошибка: <code><b>{ex}</b></code>")
    async def watcher(self, message):
        """Смотритель :)"""
        try:
            if self.db.get("AutoOtvechikAI", "WORK", True):
                if message.sender_id == (await message.client.get_me()).id:
                    return
                if message.is_private and message.sender_id != 777000 and message.sender_id != 1271266957 and self._tg_id:
                    user = await message.client.get_entity(message.chat_id)
                    if user.bot == False:
                        if self.config["contact"] == False or (self.config["contact"] == True and not user.contact):
                            await message.client.send_read_acknowledge(
                                message.chat_id, clear_mentions=True
                            )
                            answer = await self.create_quest(message.raw_text)
                            await message.client.send_message(message.chat_id, f"В данный момент я занят(а), поэтому с вами ведёт разговор AI:\n{answer}")
        except Exception as ex:
            await message.client.send_message(message.chat_id, f"ИИ не удалось начать диалог: <code><b>{ex}</b></code>")
