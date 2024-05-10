import asyncio
import random
import logging
import re

from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, executor, types, exceptions
from aiogram.utils import markdown
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from loguru import logger
from zodiac_sign import get_zodiac_sign
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboards import Markups
from bf_texts import bf_sending, SendingData
from texts import random_texts_year, study_menu_texts, welcome_text, to_connect, start_texts, study_text, astro_advices
from src.common import settings
from src.models import db, db_sendings

from data.skip_100_lead import skip_100_leads


class States(StatesGroup):
    get_user_date_for_horoscope_year = State()
    back_state = State()


storage = RedisStorage2(db=settings.redis_db, pool_size=40)
bot = Bot(settings.tg_token)
dp = Dispatcher(bot, storage=storage)
ADMIN_IDS = (1188441997, 791363343)
markups = Markups()

available_codes = list(range(15908, 531284))  # Коды для генерации заявки при окончании получения разбора гороскопа
# horoscopes_padejs = {'मेष': 'मेष', 'वृषभ': 'वृषभ', 'मिथुन': 'मिथुन', 'कर्क': 'कर्क',
#                     'लियो': 'लियो', 'कन्या': 'कन्या', 'तुला': 'तुला', 'वृश्चिक': 'वृश्चिक',
#                     'धनु': 'धनु', 'मकर': 'मकर', 'कुंभ': 'कुंभ', 'मीन': 'मीन'}

language = 'hindi_HINDI'

BF_PEOPLE = [791363343, 923202245, 1633990660, 1188441997, 627568042]


def get_value_of_arg(arg: str) -> str:
    """Получает значение из аргумент=значение"""
    return arg.split('=')[-1]


def generate_apply_code():
    code = ''.join(map(lambda num: str(num), [random.choice((4, 5, 6, 7, 8, 9)) for _ in range(6)]))
    return code


@dp.message_handler(lambda message: message.from_user.id == 1188441997, content_types=['photo'], state='*')
async def get_photo_from_me(message: types.Message, state: FSMContext):
    print(message.photo[-1].file_id)


@dp.message_handler(lambda message: message.from_user.id == 1188441997, content_types=['document'], state='*')
async def get_photo_from_me(message: types.Message, state: FSMContext):
    print(message.document.file_id)


@dp.message_handler(commands=['start'], state='*')
@logger.catch
async def start_mes(message: types.Message, state: FSMContext) -> None:
    await state.finish()
    await message.answer_photo(types.InputFile('data/photos/lune_horoscope_2.png'), welcome_text, reply_markup=markups.start_mrkup, parse_mode='html')
    await db.registrate_if_not_exists(message.from_user.id)


@dp.message_handler(lambda message: message.from_user.id in BF_PEOPLE, commands=['bf_stat'], state='*')
async def get_bf_stat(message: types.Message):
    stat = await db_sendings.get_bf_stat()
    await message.answer(stat)


@dp.callback_query_handler(lambda call: call.data == 'delete_msg', state='*')
async def del_msg(call: types.CallbackQuery, state: FSMContext):
    """
    Deletes the message as garbage
    """
    try:
        await call.message.delete()
    except exceptions.MessageCantBeDeleted:
        await call.message.delete_reply_markup()
        await call.answer('Unable to delete message')


@dp.message_handler(lambda message: message.text == '👈Обратно', state="*")
@logger.catch
async def back_from_getting_horoscope_year(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer_photo(types.InputFile('data/photos/lune_horoscope_2.png'), welcome_text, reply_markup=markups.start_mrkup, parse_mode='html')


@dp.message_handler(lambda message: message.text == '👈वापस', state='*')
@logger.catch
async def back_from_get_user_date_guide(message: types.Message, state: FSMContext):
    await message.answer(study_text, reply_markup=markups.study_mrkup)


@dp.message_handler(lambda message: message.text == '✨2024 के लिए निःशुल्क राशिफल प्राप्त करें', state='*')
@logger.catch
async def get_horoscope_on_2023_year(message: types.Message, state: FSMContext):
    user_date = await db.check_if_user_has_birth_date(message.from_user.id)
    if not bool(user_date):
        await bot.send_message(message.chat.id,
                               text='🙏वर्ष का राशिफल प्राप्त करने के लिए, कृपया अपनी जन्मतिथि dd.mm.yyyy फॉर्म में लिखें।',
                               reply_markup=markups.to_menu_mrkup, parse_mode='html')
        await state.set_state(States.get_user_date_for_horoscope_year.state)
    else:
        day, month = user_date.split('.')[:2]
        zodiac = get_zodiac_sign(day, month, language='hindi_HINDI')
        user_choose = await db.get_horoscope_text_index(message.from_user.id)
        await bot.send_message(message.chat.id, text=generate_beautiful_text('year', zodiac, user_date, user_choose),
                               reply_markup=markups.to_menu_mrkup,
                               parse_mode='html')
        await state.set_state(States.back_state.state)
        asyncio.create_task(send_text_with_inline_btn(message.chat.id))


@dp.message_handler(lambda message: message.text in start_texts, state='*')
@logger.catch
async def which_horoscope(message: types.Message, state) -> None:
    if message.text == '✨ निःशुल्क राशिफल प्राप्त करें':
        user_date = await db.check_if_user_has_birth_date(message.from_user.id)
        if not bool(user_date):
            await bot.send_message(message.chat.id,
                                   text='🙏वर्ष का राशिफल प्राप्त करने के लिए, कृपया अपनी जन्मतिथि dd.mm.yyyy फॉर्म में लिखें।',
                                   reply_markup=markups.to_menu_mrkup, parse_mode='html')
            await state.set_state(States.get_user_date_for_horoscope_year.state)
        else:
            day, month = user_date.split('.')[:2]
            zodiac = get_zodiac_sign(day, month, language='hindi_HINDI')
            user_choose = await db.get_horoscope_text_index(message.from_user.id)
            await message.answer_photo(types.InputFile('data/photos/year_horoscope_2.png'),
                                       caption=generate_beautiful_text('year', zodiac, user_date, user_choose),
                                       reply_markup=markups.to_menu_mrkup,
                                       parse_mode='html')
            await state.set_state(States.back_state.state)
            asyncio.create_task(send_text_with_inline_btn(message.chat.id))

    elif message.text == '📜शैक्षिक मेनू':
        await message.answer(study_text, reply_markup=markups.study_mrkup)


async def generate_astro_advice(user_id):
    start_of_text = '✨आज के लिए ज्योतिषीय सलाह:'
    advice = astro_advices[await db.get_user_advice_step(user_id)]
    now_time = datetime.now()
    tomorrow_time = (now_time + timedelta(days=1))
    necessary_time = datetime(year=tomorrow_time.year, month=tomorrow_time.month, day=tomorrow_time.day, hour=0,
                              minute=0, second=0)
    left_time_for_update = round(((necessary_time - now_time).total_seconds() / 60 / 60), 1)
    end_of_text = f"❤️नई ज्योतिषीय सलाह आने तक {left_time_for_update}घंटे शेष हैं।"
    main_text = f'{start_of_text}\n\n{advice}\n\n{end_of_text}'
    return main_text


@dp.message_handler(lambda message: message.text in study_menu_texts or message.text in ('🙏 निःशुल्क राशिफल प्राप्त करें', '✨वर्ष के लिए निःशुल्क राशिफल प्राप्त करें', '✨आज की ज्योतिषीय सलाह'), state='*' )
async def study_menu_dispatcher(message: types.Message, state: FSMContext):
    if message.text in ('🙏 निःशुल्क राशिफल प्राप्त करें', '✨वर्ष के लिए निःशुल्क राशिफल प्राप्त करें'):
        user_date = await db.check_if_user_has_birth_date(message.from_user.id)
        if not bool(user_date):
            await bot.send_message(message.chat.id,
                                   text='🙏वर्ष का राशिफल प्राप्त करने के लिए, कृपया अपनी जन्मतिथि dd.mm.yyyy फॉर्म में लिखें।',
                                   reply_markup=markups.to_menu_mrkup, parse_mode='html')
            await state.set_state(States.get_user_date_for_horoscope_year.state)
        else:
            day, month = user_date.split('.')[:2]
            zodiac = get_zodiac_sign(day, month, language='hindi_HINDI')
            user_choose = await db.get_horoscope_text_index(message.from_user.id)
            await message.answer_photo(photo=types.InputFile('data/photos/year_horoscope_2.png'),
                                       caption=generate_beautiful_text('year', zodiac, user_date, user_choose),
                                       reply_markup=markups.to_menu_mrkup,
                                       parse_mode='html')
            await state.set_state(States.back_state.state)
            asyncio.create_task(send_text_with_inline_btn(message.chat.id))

    elif message.text == '✨आज की ज्योतिषीय सलाह':
        text = await generate_astro_advice(message.from_user.id)
        await message.answer_photo(types.InputFile('data/photos/astro_advice.JPG'), text, reply_markup=markups.mrkup_for_every_study_btn)
    elif message.text == '✨ज्योतिष क्या है?':
        await message.answer_photo(types.InputFile('data/photos/astrology_is.JPG'), study_menu_texts[message.text],
                                   reply_markup=markups.mrkup_for_every_study_btn)
    else:
        text = study_menu_texts[message.text]
        await message.answer(text, reply_markup=markups.mrkup_for_every_study_btn)


@dp.message_handler(lambda message: message.from_user.id in ADMIN_IDS, state='*', commands=['admin'])
@logger.catch
async def admin_menu(message: types.Message, state: FSMContext) -> None:
    await bot.send_message(message.chat.id, text='Выберите действие', reply_markup=markups.admin_mrkup)


@dp.callback_query_handler(lambda call: call.from_user.id in ADMIN_IDS and call.data.startswith('Admin'), state='*')
@logger.catch
async def admin_calls(call: types.CallbackQuery, state: FSMContext) -> None:
    action = '_'.join(call.data.split('_')[1:])
    if action == 'Users_Total':
        await call.message.edit_text(text=f'Пользователей всего: {await db.get_count_all_users()}',
                                     reply_markup=markups.back_admin_mrkup)

    elif action == 'Users_For_TODAY':
        await call.message.edit_text(text=f'Пользователей за сегодня: {await db.users_for_today()}',
                                     reply_markup=markups.back_admin_mrkup)

    elif action == 'BACK':
        await call.message.edit_text(text='Выберите действие', reply_markup=markups.admin_mrkup)


def generate_beautiful_text(horoscope_type, zodiac, user_date, user_choose):
    main_text = '⭐️राशिफल '
    main_text += '2024'
    horoscope_text = random_texts_year[user_choose]
    main_text += f' के लिए {markdown.hbold(zodiac)} | जन्म की तारीख: {markdown.hbold(user_date)}\n\n{horoscope_text}' + to_connect
    return main_text


async def send_analyze_of_answers(chat_id, text_to_send):
    await asyncio.sleep(7)
    await bot.send_photo(chat_id, photo=types.InputFile('data/photos/year_horoscope_2.png'), caption=text_to_send, parse_mode='html')
    asyncio.create_task(send_text_with_inline_btn(chat_id))


async def send_text_with_inline_btn(chat_id):
    apply_code = await db.get_apply_code(chat_id)
    if apply_code is None:
        apply_code = generate_apply_code()
        await db.set_apply_code(chat_id, str(apply_code))
    await asyncio.sleep(2) #12106
    text = f"{markdown.hbold('🔆केवल आज')} प्रमाणित ज्योतिषी ब्रियाना {markdown.hbold('आपके लिए निःशुल्क तैयार करूंगा')} चालू वर्ष के लिए व्यक्तिगत राशिफल.\n\n📎आपका आवेदन कोड नंबर: {markdown .hcode(apply_code)}\n\nकृपया ज्योतिषी ब्रियाना को आवेदन कोड संख्या और जन्म स्थान अपने व्यक्तिगत खाते पर भेजें - @Your_soul_guide👈\n\n{markdown.hbold('❗️मुक्त स्थानों की संख्या सीमित है')}"
    await bot.send_message(chat_id, text, parse_mode='html',
                           reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(
                               text='किसी ज्योतिषी को लिखें', url=f'https://t.me/Your_soul_guide')]]))


@dp.message_handler(state=States.get_user_date_for_horoscope_year)
@logger.catch
async def choose_zodiac_year(message: types.Message, state: FSMContext) -> None:
    if re.fullmatch(r'\d{1,2}\.\d{1,2}\.\d{4}', message.text):
        day, month, year = message.text.split('.')
        if 0 < int(day) < 32 and 0 < int(month) < 13 and int(year) < 2023:
            await db.update_user_birth_date(message.from_user.id, message.text)
            zodiac = get_zodiac_sign(day, month, language='hindi_HINDI')
            user_choose_year = random.choice(range(3, len(random_texts_year)))
            await db.set_horoscope_text_index(message.from_user.id, user_choose_year)
            await message.answer('  प्रसंस्करण की जानकारी...', reply_markup=markups.to_menu_mrkup)
            await state.set_state(States.back_state.state)
            asyncio.create_task(send_analyze_of_answers(message.chat.id,
                                                        generate_beautiful_text('year', zodiac, message.text,
                                                                                user_choose_year)))
        else:
            await message.answer('अमान्य दिनांक!\n'
                                 '🙏वर्ष का राशिफल प्राप्त करने के लिए, कृपया अपनी जन्मतिथि dd.mm.yyyy फॉर्म में लिखें।',
                                 reply_markup=markups.to_menu_mrkup)
    else:
        await message.answer('अवैध प्रारूप.\n'
                             '🙏वर्ष का राशिफल प्राप्त करने के लिए, कृपया अपनी जन्मतिथि dd.mm.yyyy फॉर्म में लिखें।',
                             reply_markup=markups.to_menu_mrkup)


async def sending_messages_2h():
    while True:
        await asyncio.sleep(7)

        text_for_2h_autosending = f"{markdown.hbold('🙌मेरे प्रिय')}, मुझे इसकी घोषणा करने में जल्दबाजी है {markdown.hbold('केवल 6 खाली स्थान बचे हैं')} on {markdown.hbold('मुफ़्त संकलन')} चालू वर्ष के लिए व्यक्तिगत राशिफल\n\n{markdown.hbold('मत चूको')} तुम्हारी बारी, {markdown.hbold('ज्योतिषी को लिखें')} वचन पर विश्वास करो \"{markdown.hbold('ख़ुशी')}\" व्यक्तिगत संदेशों में - @Your_soul_guide👈\n\n🧚की मदद से {markdown.hbold('मुफ़्त व्यक्तिगत राशिफल')} हम कर सकते हैं {markdown.hbold('वर्तमान जीवन की समस्याओं को पहचानें')} सभी क्षेत्रों में और {markdown.hbold('सही तरीके खोजें')} उन्हें हल करने के लिए"
        mrkup = types.InlineKeyboardMarkup()
        mrkup.add(types.InlineKeyboardButton("खुशियों को ✨ में आने दो", url="https://t.me/Your_soul_guide"))

        users = await db_sendings.get_users_2h_autosending()
        for user in users:
            try:
                await bot.send_message(user, text_for_2h_autosending, parse_mode='html', reply_markup=mrkup)
                logger.info(f'ID: {user}. Got 2h_autosending')
                await db_sendings.mark_got_2h_autosending(user)
                await asyncio.sleep(0.2)
            except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.ChatNotFound):
                logger.error(f'ID: {user}. DELETED')
                await db.delete_user(user)
            except Exception as ex:
                logger.error(f'got error: {ex}')


async def sending_message_24_h():
    while True:
        await asyncio.sleep(12)

        text_autosending_24h = f"🌖नमस्कार, आज {markdown.hbold('चंद्रमा सबसे अनुकूल चरण में है')} है, जिसके दौरान आप जन्म कुंडली के अनुसार अधिकतम {markdown.hbold('सटीक व्यक्तिगत ज्योतिषीय विश्लेषण')} कर सकते हैं। - ज्योतिषी {markdown.hbold('वेरा आपके लिए एक निःशुल्क विश्लेषण तैयार करेगा।')}\n\n🧘‍♀️इसमें आप जानेंगे कि कौन सा {markdown.hbold('सितारे आपको रास्ता चुनने की सलाह देते हैं,' )} आप कैसे {markdown.hbold ('वर्तमान जीवन की समस्याएं')} को हल कर सकते हैं और उसके जीवन पथ में {markdown.hbold('आगे की असफलताओं')} से बच सकते हैं\n\nप्राप्त करने के लिए, आपको {markdown.hbold('write) की आवश्यकता है नोट्स')} और निजी संदेशों में {markdown.hbold('आपके जन्म का स्थान')} - @Your_soul_guide👈\n\n{markdown.hbold('🔮विज्ञापित स्थानों की संख्या सीमित है!')}"
        mrkup = types.InlineKeyboardMarkup()
        mrkup.add(types.InlineKeyboardButton("🔆निःशुल्क ज्योतिषीय विश्लेषण", url="https://t.me/Your_soul_guide"))

        users = await db_sendings.get_users_24h_autosending()
        for user in users:
            try:
                await bot.send_message(user, text_autosending_24h, parse_mode='html', reply_markup=mrkup)
                logger.info(f'ID: {user}. Got autosending_24h')
                await db_sendings.mark_got_24h_autosending(user)
                await asyncio.sleep(0.2)
            except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.ChatNotFound):
                logger.error(f'ID: {user}. DELETED')
                await db.delete_user(user)
            except Exception as ex:
                logger.error(f'got error: {ex}')


async def sending_message_48_h():
    while True:
        await asyncio.sleep(12)

        text_autosending_48h = f"🧚‍♂️नमस्कार, {markdown.hbold('यह अद्भुत दिन')} में मेरे {markdown.hbold('छात्र')} की संख्या जिन्होंने प्राप्त किया{markdown.hbold('ज्योतिषीय परामर्श')} इस वर्ष {markdown.hbold('1500 से अधिक लोग')}\n\nइसके सम्मान में {markdown.hbold('महत्वपूर्ण घटना')}, मैं {markdown.hbold('आपके लिए एक उपहार')} और {markdown.hbold( 'मुफ़्त ज्योतिषीय विश्लेषण🎉')} बनाना चाहता हूं\n\nग्रहण करना {markdown.hbold('मुफ़्त विश्लेषण')} - {markdown.hbold('लिखना')} मुझे निजी संदेश भेजें {markdown.hbold('जन्म की तारीख')} — @Your_soul_guide👈\n\n🪄{markdown.hbold('केवल लिखने वाले प्रथम 10 लोगों के लिए निःशुल्क विश्लेषण')}"
        mrkup = types.InlineKeyboardMarkup()
        mrkup.add(types.InlineKeyboardButton("एक उपहार उठाओ🎁", url="https://t.me/Your_soul_guide"))

        users_for_autosending_1 = await db_sendings.get_users_48h_autosending()
        for user in users_for_autosending_1:
            try:
                await bot.send_message(user, text_autosending_48h, parse_mode='html', reply_markup=mrkup)
                logger.info(f'ID: {user}. Got autosending_text_48h')
                await db_sendings.mark_got_48h_autosending(user)
                await asyncio.sleep(0.2)
            except (exceptions.BotBlocked, exceptions.UserDeactivated):
                logger.error(f'ID: {user}. DELETED')
                await db.delete_user(user)
            except Exception as ex:
                logger.error(f'got error: {ex}')


async def sending_message_72h():
    while True:
        await asyncio.sleep(12)

        text = f'🪐नमस्कार, मैं आपको इसके बाद सूचित करना चाहता हूं {markdown.hbold("आपकी अनगिनत विनती")} - और {markdown.hbold("दूसरी स्ट्रीम खोलें")} और {markdown.hbold("मैं 15 देना चाहता हूँ") } भाग्यशाली {markdown.hbold("निःशुल्क ज्योतिषीय विश्लेषण")}\n\n🙌अगर आप {markdown.hbold("अपने जीवन में सही रास्ता खोजने के लिए तैयार हैं")}, फिर लिखना {markdown.hbold("व्यक्तिगत संदेशों में मेरी जन्मतिथि - @Your_soul_guide👈")}'
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("विश्लेषण प्राप्त करें🔱", url="https://t.me/Your_soul_guide"))

        users_for_autosending_1 = await db_sendings.get_users_72h_autosending()
        for user in users_for_autosending_1:
            try:
                await bot.send_message(user, text, parse_mode='html', reply_markup=kb)
                logger.info(f'ID: {user}. Got autosending_text_72h')
                await db_sendings.mark_got_72h_autosending(user)
                await asyncio.sleep(0.2)
            except (exceptions.BotBlocked, exceptions.UserDeactivated):
                logger.exception(f'ID: {user}. DELETED')
                await db.delete_user(user)
            except Exception as ex:
                logger.error(f'got error: {ex}')


@dp.callback_query_handler(lambda call: call.data == 'black_friday?get_gift', state='*')
async def send_black_friday_gift(call: types.CallbackQuery, state: FSMContext):
    chat_member = await bot.get_chat_member(-1002059782974, call.from_user.id)
    if chat_member.is_chat_member():
        await call.message.answer_document('BQACAgIAAxkBAAFqLvZlShPPCzUoYZKx5RVGi3ibd2iT6wACHTUAAofGUUq9ksqFXr6WfjME')
    else:
        await call.answer("Войдите в марафон, чтобы получить подарок ❤️")


async def bf_task(id_: int, sending: SendingData, db_func, skip_if_chat_member: bool = False, only_for_chat_member: bool = False):
    try:

        if skip_if_chat_member or only_for_chat_member:
            chat_member = await bot.get_chat_member(-1002059782974, id_)
            if chat_member.is_chat_member() and skip_if_chat_member:
                return 'skip'
            elif not chat_member.is_chat_member() and only_for_chat_member:
                return 'skip'
            name = chat_member.user.first_name
        else:
            name = None

        if id_ in skip_100_leads:
            return 'skip'

        text = await sending.get_text(bot, id_, name)
        if sending.photo is not None:
            await bot.send_photo(id_, types.InputFile(sending.photo), caption=text, reply_markup=sending.kb,
                                 parse_mode='html', disable_notification=True)
        else:
            await bot.send_message(id_, text=text, reply_markup=sending.kb,
                                   parse_mode='html', disable_web_page_preview=True)
        await db_func(id_)
        sending.count += 1
        logger.success(f'{id_} sending_{sending.uid} text')

    except (exceptions.BotBlocked, exceptions.UserDeactivated, exceptions.ChatNotFound):
        logger.exception(f'ID: {id_}. DELETED')
        await db.delete_user(id_)
    except Exception as e:
        logger.error(f'BUG: {e}')
    else:
        return 'success'
    return 'false'


async def sending_newsletter():
    white_day = 4
    now_time = datetime.now()

    if now_time.day > white_day:
        return

    while True:
        await asyncio.sleep(2)
        if now_time.day == white_day and now_time.hour >= 7:
            try:
                tasks = []
                users = [1371617744] + list(await db_sendings.get_users_for_sending_newsletter())
                print(len(users))
                for user in users:
                    logger.info(f"Пытаюсь отправить сообщение рассылки - {user}")
                    try:
                        _s = bf_sending
                        # if _s.count >= 80000:
                        #     break
                        tasks.append(asyncio.create_task(bf_task(user, _s, db_sendings.set_newsletter)))
                        if len(tasks) > 40:
                            print(len(tasks))
                            r = await asyncio.gather(*tasks, return_exceptions=False)
                            await asyncio.wait(tasks)
                            await asyncio.sleep(0.4)
                            logger.info(f"{r.count('success')=}", f"{r.count('false')=}", f"{r.count('skip')=}")
                            tasks.clear()

                    except Exception as ex:
                        logger.error(f'Ошибка в малом блоке sending: {ex}')
                    finally:
                        await asyncio.sleep(0.03)
            except Exception as ex:
                logger.error(f"Ошибка в большом блоке sending - {ex}")
            finally:
                await bot.send_message(1371617744, f"ERROR рассылка стопнулась.")
                logger.info("Рассылка завершилась")


async def on_startup(_):
    asyncio.create_task(sending_newsletter())
    asyncio.create_task(sending_messages_2h())
    asyncio.create_task(sending_message_24_h())
    asyncio.create_task(sending_message_48_h())
    asyncio.create_task(sending_message_72h())


async def update_db_advices_step_func():
    await db.update_users_advice_step()


try:
    a_logger = logging.getLogger('apscheduler.scheduler')
    a_logger.setLevel(logging.DEBUG)
    scheduler = AsyncIOScheduler({'apscheduler.timezone': 'Europe/Moscow'})
    scheduler.add_job(trigger='cron', hour='00', minute='00', func=update_db_advices_step_func)
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup)
finally:
    stop = True
    logger.info("Бот закончил работу")
