from aiogram import types


class Markups:
    start_mrkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_mrkup.add(types.KeyboardButton(text='✨ निःशुल्क राशिफल प्राप्त करें'))
    start_mrkup.add(types.KeyboardButton(text='📜शैक्षिक मेनू'))

    study_mrkup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    study_btns_titles = ['✨ज्योतिष क्या है?', '✨कुंडली क्या है?',
                          '✨पहला राशिफल कैसे सामने आया?', '✨आज की ज्योतिषीय सलाह',
                          '✨ज्योतिष में वे क्या अध्ययन करते हैं?', '✨ज्योतिष में 12 घर कौन से हैं?',
                          '✨कौन सा घर काम के लिए जिम्मेदार है?', '✨कौन सा घर परिवार के लिए जिम्मेदार है?',
                          '🙏 निःशुल्क राशिफल प्राप्त करें']

    study_mrkup.add(types.KeyboardButton('✨ज्योतिष क्या है?'), types.KeyboardButton('✨कुंडली क्या है?'))
    study_mrkup.add(types.KeyboardButton('✨पहली कुंडली कैसे प्रकट हुई?'), types.KeyboardButton('✨आज की ज्योतिषीय सलाह'))
    study_mrkup.add(types.KeyboardButton('✨वे ज्योतिष में क्या पढ़ते हैं?'), types.KeyboardButton('✨ज्योतिष में 12 घर कौन से हैं?'))
    study_mrkup.add(types.KeyboardButton('✨कौन सा घर काम के लिए जिम्मेदार है?'), types.KeyboardButton('✨कौन सा घर परिवार के लिए जिम्मेदार है?'))
    study_mrkup.add(types.KeyboardButton('🙏 निःशुल्क राशिफल प्राप्त करें'))

    mrkup_for_every_study_btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mrkup_for_every_study_btn.add(types.KeyboardButton('✨वर्ष के लिए निःशुल्क राशिफल प्राप्त करें'))
    mrkup_for_every_study_btn.add(types.KeyboardButton('👈वापस'))

    to_menu_mrkup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    to_menu_mrkup.add(types.KeyboardButton('📜शैक्षिक मेनू'))

    kb_if_how_to_get_know_zodiac = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb_if_how_to_get_know_zodiac.add(types.KeyboardButton(text='✨2024 के लिए निःशुल्क राशिफल प्राप्त करें'))
    kb_if_how_to_get_know_zodiac.add(types.KeyboardButton(text='👈वापस'))

    admin_mrkup = types.InlineKeyboardMarkup()
    admin_mrkup.add(types.InlineKeyboardButton(text='Пользователей всего', callback_data='Admin_Users_Total'))
    admin_mrkup.add(types.InlineKeyboardButton(text='Пользователей за сегодня', callback_data='Admin_Users_For_TODAY'))
    admin_mrkup.add(types.InlineKeyboardButton(text='Ввели дату за сегодня', callback_data='Admin_Dates_For_TODAY'))
    admin_mrkup.add(types.InlineKeyboardButton(text='Зашли после рассылки 17ого марта 19:15', callback_data='Admin_17_march_sending'))
    admin_mrkup.add(types.InlineKeyboardButton(text='Рассылка', callback_data='Admin_Send_Messages'))  # Рассылка по любым
    admin_mrkup.add(types.InlineKeyboardButton(text='Рассылка тем, кто еще не перешёл', callback_data='Admin_Special_Send_Msgs'))  # Раcсылка только по тем, кто не перешёл на наш аккаунт
    admin_mrkup.add(types.InlineKeyboardButton(text='Перешедших по реф ссылкам', callback_data='Admin_Referal_Users'))
    back_admin_mrkup = types.InlineKeyboardMarkup()
    back_admin_mrkup.add(types.InlineKeyboardButton(text='⬅️ В меню админа', callback_data='Admin_BACK'))

    @staticmethod
    def generate_send_msgs_step(sending_type: str) -> types.InlineKeyboardMarkup:
        send_messages_step_mrkup = types.InlineKeyboardMarkup()
        send_messages_step_mrkup.add(types.InlineKeyboardButton(text='Первая ступень', callback_data=f'Sending?Step=0&type={sending_type}'),
                                     types.InlineKeyboardButton(text='Вторая ступень', callback_data=f'Sending?Step=1&type={sending_type}'))
        send_messages_step_mrkup.add(types.InlineKeyboardButton(text='Третья ступень', callback_data=f'Sending?Step=2&type={sending_type}'),
                                     types.InlineKeyboardButton(text='Четвёртая ступень', callback_data=f'Sending?Step=3&type={sending_type}'))
        send_messages_step_mrkup.add(types.InlineKeyboardButton(text='Отправить всем', callback_data=f'Sending?Step=ALL&type={sending_type}'))
        send_messages_step_mrkup.add(types.InlineKeyboardButton(text='⬅️ В меню админа', callback_data='Admin_BACK'))
        return send_messages_step_mrkup

    back_to_steps = types.InlineKeyboardMarkup()
    back_to_steps.add(types.InlineKeyboardButton(text='⬅️ Назад', callback_data='Admin_Send_Messages'))

    cancel_sending = types.InlineKeyboardMarkup()
    cancel_sending.add(types.InlineKeyboardButton(text='Отмена!', callback_data='Cancel_Getting_Msg_For_Sending'))

    to_our_tg_mrkup = types.InlineKeyboardMarkup()
    to_our_tg_mrkup.add(types.InlineKeyboardButton(text='राशिफल प्राप्त करें', url=f'https://t.me/Your_soul_guide'))

    @staticmethod
    def generate_delete_msg_mrkup(arg=None):
        mrkup_to_del_msg = types.InlineKeyboardMarkup()
        mrkup_to_del_msg.add(types.InlineKeyboardButton('बंद करना', callback_data=f'delete_msg{arg if arg else ""}'))
        return mrkup_to_del_msg

    mrkup_referal_program = types.InlineKeyboardMarkup()
    mrkup_referal_program.add(types.InlineKeyboardButton(text='✨जांचें कि शर्तें पूरी हुई हैं या नहीं', callback_data='ref_program?check_reqs'))
    mrkup_referal_program.add(types.InlineKeyboardButton(text='✨समीक्षाएँ देखें', callback_data='ref_program?reviews'))
    mrkup_referal_program.add(types.InlineKeyboardButton(text='✨दोस्तों को सही तरीके से कैसे आमंत्रित करें', callback_data='ref_program?guide'))
