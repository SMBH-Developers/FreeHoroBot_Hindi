from dataclasses import dataclass, field
from string import Template

from aiogram import types, Bot
from aiogram.utils import markdown as m


@dataclass
class SendingData:
    uid: str
    text: str | Template
    url: str
    btn_title: str
    photo: str | None = None

    kb: types.InlineKeyboardMarkup = field(init=False)
    count: int = field(init=False)

    async def get_text(self, bot: Bot, user_id: int, name: str = None):
        if isinstance(self.text, str):
            return self.text
        else:
            if name is None:
                chat_member = await bot.get_chat_member(user_id, user_id)
                name = chat_member.user.first_name
            name = m.quote_html(name)
            return self.text.substitute(name=name)

    def __post_init__(self):
        self.kb = types.InlineKeyboardMarkup()
        self.kb.add(types.InlineKeyboardButton(self.btn_title, url=self.url))
        # self.kb.add(types.InlineKeyboardButton('🎁 Получить подарок', url=self.url))
        # self.kb.add(types.InlineKeyboardButton('🎁 Получить подарок', callback_data="black_friday?get_gift"))
        self.count = 0


bf_sending = SendingData("sending_4_april",
                         Template(f'Я РАССКАЖУ КАК ОБРЕСТИ УСПЕХ УЖЕ СЕГОДНЯ ⬇️\nСегодня самый мощный день, Магический День Четверок 04.04.\nС его помощью Вы сможете забыть о бедности и обрести богатство\nКак ? 👇\n\n💎Пишите мне в личные сообщение слово " Богатство " \n➡️  @soulful_advisor\nНачало счастливой жизни сегодня'),
                         url="https://t.me/your_mentorship",
                         btn_title="ИЗМЕНИТЬ СВОЮ ЖИЗНЬ",
                         photo='data/photos/horo_sending.png'
                         )
