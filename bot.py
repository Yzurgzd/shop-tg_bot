import logging

from aiogram import Bot, Dispatcher, executor, types
import aiogram.utils.markdown as md
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, message
from aiogram.utils import executor

import sqlite3
import requests
import uuid
import random
import functions
import config
import keyboard
import statesGroup


# Настройка logging
logging.basicConfig(level=logging.INFO)

# Инициализация бота и dispatcher
bot = Bot(token=config.token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
print("| Бот инициализирован.")


# Создание баз данных
conn_u = sqlite3.connect('udb.sqlite3')
cursor_u = conn_u.cursor()

try:
    cursor_u.execute(
        '''CREATE TABLE udb (uid text, current_item text, current_price text, current_IDpay text)''')
except:
    pass

conn_a = sqlite3.connect('admin.sqlite3')
cursor_a = conn_a.cursor()

try:
    cursor_a.execute('''CREATE TABLE admin (name text, value text)''')
except:
    pass

conn_b = sqlite3.connect('buttons.sqlite3')
cursor_b = conn_b.cursor()

try:
    cursor_b.execute(
        '''CREATE TABLE buttons (button text, button_text text)''')
except:
    pass

conn_us = sqlite3.connect('users.sqlite3')
cursor_us = conn_us.cursor()

try:
    cursor_us.execute(
        '''CREATE TABLE users (id integer, chat_id integer, username text, sum_pay integer, reg_time integer, referer text)''')
except:
    pass

conn_i = sqlite3.connect('items.sqlite3')
cursor_i = conn_i.cursor()

try:
    cursor_i.execute(
        '''CREATE TABLE items (index_item text, name text, price text, category text, description text)''')
except:
    pass

conn_c = sqlite3.connect('categories.sqlite3')
cursor_c = conn_c.cursor()

try:
    cursor_c.execute(
        '''CREATE TABLE categories (category text)''')
except:
    pass

conn_m = sqlite3.connect('messages.sqlite3')
cursor_m = conn_m.cursor()

try:
    cursor_m.execute('''CREATE TABLE messages(name text, message_text text)''')
except:
    pass

conn_w = sqlite3.connect('wallets.sqlite3')
cursor_w = conn_w.cursor()

try:
    cursor_w.execute('''CREATE TABLE wallets(acc_number text, token text)''')
except:
    pass


# Отправка уведомления в группу или админу
async def send_in_group(text):
    if config.group_id != "None":
        await bot.send_message(config.group_id, text)
    else:
        await bot.send_message(config.admin_id, text)


# Команда старт
@dp.message_handler(commands=['start'])
async def start_answer(message):
    try:
        conn_u = sqlite3.connect('udb.sqlite3')
        cursor_u = conn_u.cursor()
        conn_c = sqlite3.connect('categories.sqlite3')
        cursor_c = conn_c.cursor()
        conn_m = sqlite3.connect('messages.sqlite3')
        cursor_m = conn_m.cursor()
        cursor_u.execute("DELETE FROM udb WHERE uid='" +
                         str(message.from_user.id)+"'")
        cursor_u.execute("INSERT INTO udb VALUES ('" +
                         str(message.from_user.id)+"', 'none', 'none', 'none')")
        conn_u.commit()
        start_message_text = cursor_m.execute(
            "SELECT * FROM messages WHERE name='start_message'").fetchall()[0][1]
        keyCat = types.ReplyKeyboardMarkup(True)
        all_categories = cursor_c.execute(
            "SELECT * FROM categories").fetchall()

        users = functions.DataBase()
        # Добавление юзера
        if users.search_user(message.chat.id) == False:
            refka = message.text[7:]
            user_from_worker = str(message.from_user.username)

            # Без реффки
            if refka == "":
                await send_in_group("👥 Новый айди юзера - @{}".format(user_from_worker))
                users.new_user(message.chat.id, message.from_user.username)

            # С реффкой
            else:
                await send_in_group("👥 Новый юзер от работника @{}, айди юзера - @{}".format(refka, user_from_worker))
                users.new_user(message.chat.id,
                               message.from_user.username, referer=refka)
                with open("baza.txt", "a", encoding="utf-8") as f:
                    f.write("@{} | @{}".format(refka, user_from_worker))

        users.close()

        try:
            # Вывод главного меню
            if message.from_user.id == config.admin_id:
                await bot.send_message(message.from_user.id, str(start_message_text), parse_mode='HTML', reply_markup=keyboard.keyMainAd)
            else:
                await bot.send_message(message.from_user.id, str(start_message_text), parse_mode='HTML', reply_markup=keyboard.keyMain)
        except:
            await send_in_group("💢 У пользователя возникла проблема с выводом главного меню")
            txtKeyMngr = cursor_b.execute(
                "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
            await bot.send_message(message.from_user.id, '💢 Error #CMNDSxSm\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))
    except:
        await send_in_group("💢 У пользователя возникла проблема с командой start")
        txtKeyMngr = cursor_b.execute(
            "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
        await bot.send_message(message.from_user.id, '💢 Error #CMNDSxS\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))


# Команда админ
@dp.message_handler(commands=['admin'])
async def admin_panel(message):
    # Условие делает дочтупной только для админа
    if message.from_user.id == config.admin_id:
        # Вывод кнопок категорий админ панели
        await bot.send_message(message.from_user.id, "⚙ Панель администратора",
                               parse_mode='HTML', reply_markup=keyboard.keyAdmin)
        await bot.send_message(message.from_user.id, "❗ ВО ВСЕХ СООБЩЕНИЯХ МОЖНО ИСПОЛЬЗОВАТЬ HTML-тэги, например <b>text</b>, <i>text</i>, <code>text</code>, <a href=\"http://\"></a>")


# Реагирование на сообщения от пользователя
@dp.message_handler(content_types=['text'])
async def text_answer(message):
    try:
        conn_u = sqlite3.connect('udb.sqlite3')
        cursor_u = conn_u.cursor()
        conn_i = sqlite3.connect('items.sqlite3')
        cursor_i = conn_i.cursor()
        conn_c = sqlite3.connect('categories.sqlite3')
        cursor_c = conn_c.cursor()
        conn_m = sqlite3.connect('messages.sqlite3')
        cursor_m = conn_m.cursor()
        conn_w = sqlite3.connect('wallets.sqlite3')
        cursor_w = conn_w.cursor()
        all_items = cursor_i.execute("SELECT * FROM items").fetchall()
        all_categories = cursor_c.execute(
            "SELECT * FROM categories").fetchall()

        try:
            if message.text == keyboard.txtKeyItems:
                itemMenu_message = cursor_m.execute(
                    "SELECT * FROM messages WHERE name='itemMenu_message'").fetchall()[0][1]
                itemsMiss_text = cursor_m.execute(
                    "SELECT * FROM messages WHERE name='itemsMiss_message'").fetchall()[0][1]
                keyCat = types.ReplyKeyboardMarkup(True)
                if all_categories:
                    for category in all_categories:
                        keyCat.row(str(category[0]))
                    keyCat.row(keyboard.txtKeyMainMenu)
                    await bot.send_message(message.from_user.id, str(itemMenu_message), parse_mode='HTML', reply_markup=keyCat)
                else:
                    await bot.send_message(message.from_user.id, str(itemsMiss_text), parse_mode='HTML')
        except:
            await send_in_group("💢 У пользователя возникла проблема с выводом категорий")
            txtKeyMngr = cursor_b.execute(
                "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
            await bot.send_message(message.from_user.id, '💢 Error #CNTxTXTctgr\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))

        try:
            if all_categories:
                for category in all_categories:
                    if message.text == category[0]:
                        category_message_text = cursor_m.execute(
                            "SELECT * FROM messages WHERE name='category_message'").fetchall()[0][1]
                        itemsMiss_text = cursor_m.execute(
                            "SELECT * FROM messages WHERE name='itemsMiss_message'").fetchall()[0][1]
                        keyItems = types.ReplyKeyboardMarkup(True)
                        all_items = cursor_i.execute(
                            "SELECT * FROM items WHERE category='{}'".format(category[0])).fetchall()
                        if all_items:
                            for item in all_items:
                                keyItems.row(str(item[1])+' | '+str(item[2]))
                            keyItems.row(keyboard.txtKeyItemsCat)
                            await bot.send_message(message.from_user.id, str(category_message_text).format(category[0]), parse_mode='HTML', reply_markup=keyItems)
                        else:
                            keyItems.row(keyboard.txtKeyItemsCat)
                            await bot.send_message(message.from_user.id, str(category_message_text).format(category[0]), parse_mode='HTML', reply_markup=keyItems)
                            await bot.send_message(message.from_user.id, str(itemsMiss_text), parse_mode='HTML')
        except:
            await send_in_group("💢 У пользователя возникла проблема с выводом товаров")
            txtKeyMngr = cursor_b.execute(
                "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
            await bot.send_message(message.from_user.id, '💢 Error #CNTxTXTits\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))

        try:
            if all_items:
                for item in all_items:
                    if message.text.startswith(str(item[1])+' | '+str(item[2])):
                        id_pay = uuid.uuid4()
                        cursor_u.execute("UPDATE udb SET current_item='"+str(
                            message.text.split(' | ')[0])+"' WHERE uid="+str(message.from_user.id))
                        current_price_RUB = str(message.text.split(' | ')[1])
                        cursor_u.execute("UPDATE udb SET current_price='"+str(
                            current_price_RUB[:-2])+"' WHERE uid="+str(message.from_user.id))
                        cursor_u.execute("UPDATE udb SET current_IDpay='" +
                                         str(id_pay)+"' WHERE uid="+str(message.from_user.id))
                        conn_u.commit()

                        name_wallets = str(cursor_w.execute(
                            "SELECT * FROM wallets").fetchall()[0][0])
                        chat_id = message.chat.id
                        pay_message = str(cursor_m.execute(
                            "SELECT * FROM messages WHERE name='pay_message'").fetchall()[0][1])
                        current_item = str(cursor_u.execute(
                            "SELECT * FROM udb WHERE uid='"+str(message.from_user.id)+"'").fetchall()[0][1])
                        current_price = str(cursor_u.execute(
                            "SELECT * FROM udb WHERE uid='"+str(message.from_user.id)+"'").fetchall()[0][2])
                        current_IDpay = str(cursor_u.execute(
                            "SELECT * FROM udb WHERE uid='"+str(message.from_user.id)+"'").fetchall()[0][3])
                        current_wallet = config.qiwi_number

                        conn_i = sqlite3.connect('items.sqlite3')
                        cursor_i = conn_i.cursor()
                        description_item = str(cursor_i.execute(
                            "SELECT description FROM items WHERE name='"+str(current_item)+"'").fetchall()[0][0])

                        link = functions.get_payment_link(
                            config.qiwi_number, current_price, current_IDpay)

                        keyPay = types.InlineKeyboardMarkup(row_width=1)
                        goPay = types.InlineKeyboardButton(
                            text=keyboard.txtKeyGoPay, callback_data='payment', url=link)
                        checkPay = types.InlineKeyboardButton(
                            text=keyboard.txtKeyCheckPay, callback_data='check')
                        keyPay.row(goPay)
                        keyPay.row(checkPay)
                        await bot.send_message(message.from_user.id, pay_message.format(current_item, description_item, current_wallet, current_price_RUB, current_IDpay), parse_mode='HTML', reply_markup=keyPay)
        except:
            await send_in_group("💢 У пользователя возникла проблема с выводом оплаты товара")
            txtKeyMngr = cursor_b.execute(
                "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
            await bot.send_message(message.from_user.id, '💢 Error #CNTxTXTpIts\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))

        try:
            if message.text == keyboard.txtKeyTest:
                id_testPay = uuid.uuid4()
                cursor_u.execute("UPDATE udb SET current_item='" +
                                 str(message.text)+"' WHERE uid="+str(message.from_user.id))
                current_price_RUB = '1 ₽'
                cursor_u.execute("UPDATE udb SET current_price='" +
                                 str(1)+"' WHERE uid="+str(message.from_user.id))
                cursor_u.execute("UPDATE udb SET current_IDpay='" +
                                 str(id_testPay)+"' WHERE uid="+str(message.from_user.id))
                conn_u.commit()

                name_wallets = str(cursor_w.execute(
                    "SELECT * FROM wallets").fetchall()[0][0])
                chat_id = message.chat.id
                payTest_message = str(cursor_m.execute(
                    "SELECT * FROM messages WHERE name='payTest_message'").fetchall()[0][1])
                current_item = str(cursor_u.execute(
                    "SELECT * FROM udb WHERE uid='"+str(message.from_user.id)+"'").fetchall()[0][1])
                current_price = str(cursor_u.execute(
                    "SELECT * FROM udb WHERE uid='"+str(message.from_user.id)+"'").fetchall()[0][2])
                current_IDpay = str(cursor_u.execute(
                    "SELECT * FROM udb WHERE uid='"+str(message.from_user.id)+"'").fetchall()[0][3])
                current_wallet = config.qiwi_number

                link = functions.get_payment_link(
                    config.qiwi_number, current_price, current_IDpay)

                keyPayTest = types.InlineKeyboardMarkup(row_width=1)
                goPayTest = types.InlineKeyboardButton(
                    text=keyboard.txtKeyGoPay, callback_data='payment', url=link)
                checkPayTest = types.InlineKeyboardButton(
                    text=keyboard.txtKeyCheckPay, callback_data='check_test')
                keyPayTest.row(goPayTest)
                keyPayTest.row(checkPayTest)
                await bot.send_message(message.from_user.id, payTest_message.format(current_item, current_wallet, current_price_RUB, current_IDpay), parse_mode='HTML', reply_markup=keyPayTest)
        except:
            await send_in_group("💢 У пользователя возникла проблема с тестовой оплатой")
            txtKeyMngr = cursor_b.execute(
                "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
            await bot.send_message(message.from_user.id, '💢 Error #CNTxTXTtstPy\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))

        try:
            if message.text == keyboard.txtKeyMainMenu:
                mainMenu_message = cursor_m.execute(
                    "SELECT * FROM messages WHERE name='mainMenu_message'").fetchall()[0][1]
                if message.from_user.id == config.admin_id:
                    await bot.send_message(message.from_user.id, str(mainMenu_message), parse_mode='HTML', reply_markup=keyboard.keyMainAd)
                else:
                    await bot.send_message(message.from_user.id, str(mainMenu_message), parse_mode='HTML', reply_markup=keyboard.keyMain)
        except:
            await send_in_group("💢 У пользователя возникла проблема с выходом в главное меню")
            txtKeyMngr = cursor_b.execute(
                "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
            await bot.send_message(message.from_user.id, '💢 Error #CNTxTXTm\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))

        try:
            if message.text == keyboard.txtKeyItemsCat:
                if all_categories:
                    conn_m = sqlite3.connect('messages.sqlite3')
                    cursor_m = conn_m.cursor()
                    itemMenu_message = cursor_m.execute(
                        "SELECT * FROM messages WHERE name='itemMenu_message'").fetchall()[0][1]
                    keyCat = types.ReplyKeyboardMarkup(True)

                    for category in all_categories:
                        keyCat.row(str(category[0]))
                    keyCat.row(keyboard.txtKeyMainMenu)
                    await bot.send_message(message.from_user.id, str(itemMenu_message), parse_mode='HTML', reply_markup=keyCat)
                else:
                    keyCat.row(keyboard.txtKeyItems_Miss)
                    await bot.send_message(message.from_user.id, str(itemMenu_message), parse_mode='HTML', reply_markup=keyCat)
        except:
            await send_in_group("💢 У пользователя возникла проблема с выходом в категории")
            txtKeyMngr = cursor_b.execute(
                "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
            await bot.send_message(message.from_user.id, '💢 Error #CNTxTXTm-ctgr\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))

        try:
            if message.text == keyboard.txtKeyMngr:
                manager_message = cursor_m.execute(
                    "SELECT * FROM messages WHERE name='manager_message'").fetchall()[0][1]
                keyMngr = types.InlineKeyboardMarkup()
                txtKeyMngr = types.InlineKeyboardButton(
                    text=keyboard.txtKeySendMngr, url="t.me/{}".format(config.manager))
                keyMngr.row(txtKeyMngr)
                await bot.send_message(message.from_user.id, str(manager_message), parse_mode='HTML', reply_markup=keyMngr)
        except:
            await send_in_group("💢 У пользователя возникла проблема с вывовом мененджера")
            txtKeyMngr = cursor_b.execute(
                "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
            await bot.send_message(message.from_user.id, '💢 Error #CNTxTXTmngr\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))

        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyAnswersAd:
                await bot.send_message(message.from_user.id, "✏ Выберите пунк для изменения",
                                       parse_mode='HTML', reply_markup=keyboard.keyAnswersAd)

            elif message.text == keyboard.txtKeyBtnAd:
                await bot.send_message(message.from_user.id, "✏ Выберите пунк для изменения",
                                       parse_mode='HTML', reply_markup=keyboard.keyBtnAd)

            elif message.text == keyboard.txtKeyCatItemAd:
                await bot.send_message(message.from_user.id, "✏ Выберите пунк для изменения",
                                       parse_mode='HTML', reply_markup=keyboard.keyCatItemAd)

            elif message.text == keyboard.txtKeyWalAd:
                await bot.send_message(message.from_user.id, "✏ Выберите пунк для изменения",
                                       parse_mode='HTML', reply_markup=keyboard.keyWalAd)

            elif message.text == keyboard.txtKeyAdminAd:
                await bot.send_message(message.from_user.id, "✏ Выберите пунк для изменения",
                                       parse_mode='HTML', reply_markup=keyboard.keyAdminAd)

            elif message.text == keyboard.txtKeySendAd:
                await statesGroup.Form.txtSend.set()
                await bot.send_message(message.from_user.id, "💬 Введите текст вообщения",
                                       parse_mode='HTML', reply_markup=keyboard.keyCancel)

            elif message.text == keyboard.txtKeyBackAdmin:
                await bot.send_message(message.from_user.id, "⚙ Панель администратора",
                                       parse_mode='HTML', reply_markup=keyboard.keyAdmin)

            elif message.text == keyboard.txtKeyOpenAdmin:
                await bot.send_message(message.from_user.id, "⚙ Панель администратора",
                                       parse_mode='HTML', reply_markup=keyboard.keyAdmin)
                await bot.send_message(message.from_user.id, "❗ ВО ВСЕХ СООБЩЕНИЯХ МОЖНО ИСПОЛЬЗОВАТЬ HTML-тэги, например <b>text</b>, <i>text</i>, <code>text</code>, <a href=\"http://\"></a>")

            elif message.text == keyboard.txtKeyStart:
                await statesGroup.Form.txtStart.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст приветствия', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyPay:
                await statesGroup.Form.txtPay.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст оплаты', reply_markup=keyboard.keyCancel, parse_mode='HTML')
                await bot.send_message(message.from_user.id, '❗ Параметры для этого сообщения:\n{0} - Название товара выбранного пользователем\n{1} - Описание товара, выбранного пользователем\n{2} - Номер кошелька для этой платежной системы\n{3} - Цена товара, выбранного пользователем\n{4} - Код для оплаты(генерируется рандомно)', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyPayTest:
                await statesGroup.Form.txtPayTest.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст тестовой оплаты', reply_markup=keyboard.keyCancel, parse_mode='HTML')
                await bot.send_message(message.from_user.id, '❗ Параметры для этого сообщения:\n{0} - Название товара выбранного пользователем\n{1} - Номер кошелька для этой платежной системы\n{2} - Цена товара, выбранного пользователем\n{3} - Код для оплаты(генерируется рандомно)', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyCheck:
                await statesGroup.Form.txtCheck.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст успешной оплаты оплаты', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyCheckFail:
                await statesGroup.Form.txtCheckFail.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст безуспешной оплаты оплаты', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyMain:
                await statesGroup.Form.txtMain.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст главного меню', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyCatalog:
                await statesGroup.Form.txtCatalog.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст входа в каталог', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyManager:
                await statesGroup.Form.txtManager.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст менеджера', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyCat:
                await statesGroup.Form.txtCat.set()
                await bot.send_message(message.from_user.id, '💬 Введите ответ категории', reply_markup=keyboard.keyCancel, parse_mode='HTML')
                await bot.send_message(message.from_user.id, '❗ Параметры для этого сообщения:\n{0} - Название категории выбранного пользователем', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyItemsMiss:
                await statesGroup.Form.txtItemsMiss.set()
                await bot.send_message(message.from_user.id, '💬 Введите ответ отсутствия товаров', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyEdItems:
                await statesGroup.Form.txtBtnItems.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст для кнопки открывающий все категории товаров', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyEdTestPay:
                await statesGroup.Form.txtBtnTestPay.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст для кнопки тестовой оплаты', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyEdMngr:
                await statesGroup.Form.txtBtnMngr.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст для кнопки открывающий менеджера', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyEdMain:
                await statesGroup.Form.txtBtnMain.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст для кнопки открывающий шлавное меню', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyEdCatalog:
                await statesGroup.Form.txtBtnCatalog.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст для кнопки открывающий каталог', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyEdSendMngr:
                await statesGroup.Form.txtBtnSendMngr.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст для кнопки связаться с менеджером', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyEdGoPay:
                await statesGroup.Form.txtBtnGoPay.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст для кнопки перехода к оплате', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyEdCheckPay:
                await statesGroup.Form.txtBtnCheckPay.set()
                await bot.send_message(message.from_user.id, '💬 Введите текст для кнопки проверки оплаты', reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyAdd:
                keyAddItem = types.ReplyKeyboardMarkup(True)
                if all_categories:
                    await statesGroup.Form.txtCatItem.set()
                    for category in all_categories:
                        keyAddItem.row(str(category[0]))
                    keyAddItem.row(keyboard.txtKeyCancel)
                    await bot.send_message(message.from_user.id, "✏ Выберите категорию", parse_mode='HTML', reply_markup=keyAddItem)
                else:
                    await bot.send_message(message.from_user.id, "💢 Категории отсутствуют...\nСначало нужно добавить категорию", parse_mode='HTML', reply_markup=keyboard.keyCatItemAd)

            elif message.text == keyboard.txtKeyDel:
                keyDelItem = types.ReplyKeyboardMarkup(True)
                if all_items:
                    await statesGroup.Form.txtDel.set()
                    for item in all_items:
                        keyDelItem.row(str(item[1]))
                    keyDelItem.row(keyboard.txtKeyCancel)
                    await bot.send_message(message.from_user.id, "✏ Выберите товар для удаления", reply_markup=keyDelItem)
                else:
                    await bot.send_message(message.from_user.id, "💢 Товары отсутствуют...", parse_mode='HTML', reply_markup=keyboard.keyCatItemAd)

            elif message.text == keyboard.txtKeyDelAll:
                if all_items:
                    keyDelAll = types.InlineKeyboardMarkup(row_width=2)
                    yesDelAll = types.InlineKeyboardButton(
                        '✔ Да', callback_data='delAllItems_Yes')
                    noDelAll = types.InlineKeyboardButton(
                        '✖ Нет', callback_data='delAllItems_No')
                    keyDelAll.row(yesDelAll, noDelAll)
                    await bot.send_message(message.from_user.id, "✏ Вы действительно хотите удалить все товары?", reply_markup=keyDelAll)
                else:
                    await bot.send_message(message.from_user.id, "💢 Товары отсутствуют...", parse_mode='HTML', reply_markup=keyboard.keyCatItemAd)

            elif message.text == keyboard.txtKeyAddCat:
                await statesGroup.Form.txtAddCat.set()
                await bot.send_message(message.from_user.id, "💬 Введите название категории", reply_markup=keyboard.keyCancel, parse_mode='HTML')

            elif message.text == keyboard.txtKeyDelCat:
                keyDelCat = types.ReplyKeyboardMarkup(True)
                if all_categories:
                    await statesGroup.Form.txtDelCat.set()
                    for category in all_categories:
                        keyDelCat.row(str(category[0]))
                    keyDelCat.row(keyboard.txtKeyCancel)
                    await bot.send_message(message.from_user.id, "✏ Выберите категорию", reply_markup=keyDelCat)
                else:
                    await bot.send_message(message.from_user.id, "💢 Категории отсутствуют...", parse_mode='HTML', reply_markup=keyboard.keyCatItemAd)

            elif message.text == keyboard.txtKeyWal:
                await statesGroup.Form.txtWal.set()
                await bot.send_message(message.from_user.id, "💬 Введите номер QIWI", reply_markup=keyboard.keyCancel)

            elif message.text == keyboard.txtKeyWalToken:
                await statesGroup.Form.txtWalToken.set()
                await bot.send_message(message.from_user.id, "💬 Введите QIWI токен", reply_markup=keyboard.keyCancel)

            elif message.text == keyboard.txtKeyAdminId:
                await statesGroup.Form.txtAdminId.set()
                await bot.send_message(message.from_user.id, "💬 Введите ID администратора", reply_markup=keyboard.keyCancel)

            elif message.text == keyboard.txtKeyGroupId:
                await statesGroup.Form.txtGroupId.set()
                await bot.send_message(message.from_user.id, "💬 Введите ID группы", reply_markup=keyboard.keyCancel)

            elif message.text == keyboard.txtKeyGroupIdDel:
                if config.group_id == 'None':
                    await bot.send_message(message.from_user.id, "✨ Рассылка уже отключена")
                else:
                    keyGroupDel = types.InlineKeyboardMarkup(row_width=2)
                    yesGroupDel = types.InlineKeyboardButton(
                        '✔ Да', callback_data='groupDel_Yes')
                    noGroupDel = types.InlineKeyboardButton(
                        '✖ Нет', callback_data='groupDel_No')
                    keyGroupDel.row(yesGroupDel, noGroupDel)
                    await bot.send_message(message.from_user.id, "✏ Вы действительно хотите отключить рассылку в группу?", reply_markup=keyGroupDel)

            elif message.text == keyboard.txtKeyMngrId:
                await statesGroup.Form.txtMngrId.set()
                await bot.send_message(message.from_user.id, "💬 Введите Username менеджера", reply_markup=keyboard.keyCancel)

            elif message.text == keyboard.txtKeyUsersAd:
                DB = functions.DataBase()
                users = DB.get_all_users()
                DB.close()

                for mes in users:
                    await bot.send_message(message.chat.id, mes)
    except:
        await send_in_group("💢 У пользователя возникла проблема с регированием на сообщения")
        txtKeyMngr = cursor_b.execute(
            "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
        await bot.send_message(message.from_user.id, '💢 Error #CNTxTXT\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))


# Отправка сообщения
@dp.message_handler(state=statesGroup.Form.txtSend)
async def start_message_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAdmin)
            else:
                async with state.proxy() as data:
                    data['txtSend'] = message.text
                    txtSend = data['txtSend']
                    DB = functions.DataBase()
                    users = DB.get_chat_id_users()
                    DB.close()
                    for mesId in users:
                        await bot.send_message(mesId, str(txtSend), parse_mode='HTML')
                    await bot.send_message(message.from_user.id, '✨ Сообщения отправлены', reply_markup=keyboard.keyAdmin)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при отправки сообщения пользователям')


# Изменение приветственного сообщения
@dp.message_handler(state=statesGroup.Form.txtStart)
async def start_message_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAnswersAd)
            else:
                async with state.proxy() as data:
                    data['txtStart'] = message.text
                    txtStart = data['txtStart']
                    conn_m = sqlite3.connect('messages.sqlite3')
                    cursor_m = conn_m.cursor()
                    cursor_m.execute("UPDATE messages SET message_text='" +
                                     str(txtStart)+"' WHERE name='start_message'")
                    conn_m.commit()
                    await bot.send_message(message.from_user.id,
                                           '✨ Текст приветсвенного сообщения изменен', reply_markup=keyboard.keyAnswersAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении приветственного сообщения')


# Изменение текста оплаты
@dp.message_handler(state=statesGroup.Form.txtPay)
async def pay_message_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAnswersAd)
            else:
                async with state.proxy() as data:
                    data['txtPay'] = message.text
                    txtPay = data['txtPay']
                    conn_m = sqlite3.connect('messages.sqlite3')
                    cursor_m = conn_m.cursor()
                    cursor_m.execute(
                        "UPDATE messages SET message_text='"+str(txtPay)+"' WHERE name='pay_message'")
                    conn_m.commit()
                    await bot.send_message(message.from_user.id, '✨ Текст сообщения об оплате изменен', reply_markup=keyboard.keyAnswersAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста оплаты')


# Изменение текста тестовой оплаты
@dp.message_handler(state=statesGroup.Form.txtPayTest)
async def payTest_message_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAnswersAd)
            else:
                async with state.proxy() as data:
                    data['txtPayTest'] = message.text
                    txtPayTest = data['txtPayTest']
                    conn_m = sqlite3.connect('messages.sqlite3')
                    cursor_m = conn_m.cursor()
                    cursor_m.execute("UPDATE messages SET message_text='" +
                                     str(txtPayTest)+"' WHERE name='payTest_message'")
                    conn_m.commit()
                    await bot.send_message(message.from_user.id, '✨ Текст сообщения об тестовой оплате изменен', reply_markup=keyboard.keyAnswersAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста тестовой оплаты')


# Изменение текста проверки УСПЕШНОЙ оплаты
@dp.message_handler(state=statesGroup.Form.txtCheck)
async def check_message_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAnswersAd)
            else:
                async with state.proxy() as data:
                    data['txtCheck'] = message.text
                    txtCheck = data['txtCheck']
                    conn_m = sqlite3.connect('messages.sqlite3')
                    cursor_m = conn_m.cursor()
                    cursor_m.execute(
                        "UPDATE messages SET message_text='"+str(txtCheck)+"' WHERE name='check_message'")
                    conn_m.commit()
                    await bot.send_message(message.from_user.id, '✨ Текст сообщения проверки оплаты изменен', reply_markup=keyboard.keyAnswersAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста проверки успешной оплаты')


# Изменение текста НЕУДАЧНОЙ оплаты
@dp.message_handler(state=statesGroup.Form.txtCheckFail)
async def check_fail_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAnswersAd)
            else:
                async with state.proxy() as data:
                    data['txtCheckFail'] = message.text
                    txtCheckFail = data['txtCheckFail']
                    conn_m = sqlite3.connect('messages.sqlite3')
                    cursor_m = conn_m.cursor()
                    cursor_m.execute("UPDATE messages SET message_text='" +
                                     str(txtCheckFail)+"' WHERE name='check_fail_message'")
                    conn_m.commit()
                    await bot.send_message(message.from_user.id, '✨ Текст сообщения неудачной оплаты изменен', reply_markup=keyboard.keyAnswersAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста неудачной оплаты')


# Изменение текста сообщения главного меню
@dp.message_handler(state=statesGroup.Form.txtMain)
async def back_message_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAnswersAd)
            else:
                async with state.proxy() as data:
                    data['txtMain'] = message.text
                    txtMain = data['txtMain']
                    conn_m = sqlite3.connect('messages.sqlite3')
                    cursor_m = conn_m.cursor()
                    cursor_m.execute("UPDATE messages SET message_text='" +
                                     str(txtMain)+"' WHERE name='mainMenu_message'")
                    conn_m.commit()
                    await bot.send_message(message.from_user.id, '✨ Текст сообщения главного меню изменен', reply_markup=keyboard.keyAnswersAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста сообщения главного меню')


# Изменение текста сообщения входа в каталог
@dp.message_handler(state=statesGroup.Form.txtCatalog)
async def back_message_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAnswersAd)
            else:
                async with state.proxy() as data:
                    data['txtCatalog'] = message.text
                    txtCatalog = data['txtCatalog']
                    conn_m = sqlite3.connect('messages.sqlite3')
                    cursor_m = conn_m.cursor()
                    cursor_m.execute("UPDATE messages SET message_text='" +
                                     str(txtCatalog)+"' WHERE name='itemMenu_message'")
                    conn_m.commit()
                    await bot.send_message(message.from_user.id, '✨ Текст сообщения входа в каталог изменен', reply_markup=keyboard.keyAnswersAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста сообщения в каталог')


# Изменение текста сообщения менеджера
@dp.message_handler(state=statesGroup.Form.txtManager)
async def back_message_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAnswersAd)
            else:
                async with state.proxy() as data:
                    data['txtManager'] = message.text
                    txtManager = data['txtManager']
                    conn_m = sqlite3.connect('messages.sqlite3')
                    cursor_m = conn_m.cursor()
                    cursor_m.execute("UPDATE messages SET message_text='" +
                                     str(txtManager)+"' WHERE name='manager_message'")
                    conn_m.commit()
                    await bot.send_message(message.from_user.id, '✨ Текст сообщения менеджера изменен', reply_markup=keyboard.keyAnswersAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста сообщения менеджера')


# Изменение текста сообщения категории
@dp.message_handler(state=statesGroup.Form.txtCat)
async def category_message_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAnswersAd)
            else:
                async with state.proxy() as data:
                    data['txtCat'] = message.text
                    txtCat = data['txtCat']
                    conn_m = sqlite3.connect('messages.sqlite3')
                    cursor_m = conn_m.cursor()
                    cursor_m.execute("UPDATE messages SET message_text='" +
                                     str(txtCat)+"' WHERE name='category_message'")
                    conn_m.commit()
                    await bot.send_message(message.from_user.id, '✨ Текст сообщения категории изменен', reply_markup=keyboard.keyAnswersAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошбка при изменении текста сообщения категории')


# Изменение текста при отсутствии товаров
@dp.message_handler(state=statesGroup.Form.txtItemsMiss)
async def itemsMiss_message_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAnswersAd)
            else:
                async with state.proxy() as data:
                    data['txtItemsMiss'] = message.text
                    txtItemsMiss = data['txtItemsMiss']
                    conn_m = sqlite3.connect('messages.sqlite3')
                    cursor_m = conn_m.cursor()
                    cursor_m.execute("UPDATE messages SET message_text='" +
                                     str(txtItemsMiss)+"' WHERE name='itemsMiss_message'")
                    conn_m.commit()
                    await bot.send_message(message.from_user.id, '✨ Текст отсутствия товаров изменен', reply_markup=keyboard.keyAnswersAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста при отсутствии товаров')


# Изменение текста кнопки товаров
@dp.message_handler(state=statesGroup.Form.txtBtnItems)
async def items_button_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyBtnAd)
            else:
                async with state.proxy() as data:
                    data['txtBtnItems'] = message.text
                    txtBtnItems = data['txtBtnItems']
                    conn_b = sqlite3.connect('buttons.sqlite3')
                    cursor_b = conn_b.cursor()
                    cursor_b.execute(
                        "UPDATE buttons SET button_text='"+str(txtBtnItems)+"' WHERE button='items'")
                    conn_b.commit()

                    # Кнопки главного меню
                    keyMain = types.ReplyKeyboardMarkup(True)
                    txtKeyItems = str(cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='items'").fetchall()[0][1])
                    txtKeyMngr = cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
                    txtKeyTest = cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='testPay'").fetchall()[0][1]

                    keyboard.txtKeyItems = txtKeyItems
                    keyboard.txtKeyMngr = txtKeyMngr
                    keyboard.txtKeyTest = txtKeyTest

                    keyMain.row(txtKeyItems)
                    keyMain.row(txtKeyMngr)
                    keyMain.row(txtKeyTest)

                    keyboard.keyMain = keyMain

                    # Кнопки главного меню для администратора
                    keyMainAd = types.ReplyKeyboardMarkup(True)
                    keyMainAd.row(txtKeyItems)
                    keyMainAd.row(txtKeyMngr)
                    keyMainAd.row(txtKeyTest)
                    keyMainAd.row(keyboard.txtKeyOpenAdmin)

                    keyboard.keyMainAd = keyMainAd
                    await bot.send_message(message.from_user.id, '✨ Текст кнопки товаров изменен', reply_markup=keyboard.keyBtnAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста кнопки товаров')


# Изменение текста кнопки тестовой оплаты
@dp.message_handler(state=statesGroup.Form.txtBtnTestPay)
async def items_button_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyBtnAd)
            else:
                async with state.proxy() as data:
                    data['txtBtnTestPay'] = message.text
                    txtBtnTestPay = data['txtBtnTestPay']
                    conn_b = sqlite3.connect('buttons.sqlite3')
                    cursor_b = conn_b.cursor()
                    cursor_b.execute(
                        "UPDATE buttons SET button_text='"+str(txtBtnTestPay)+"' WHERE button='testPay'")
                    conn_b.commit()

                    # Кнопки главного меню
                    keyMain = types.ReplyKeyboardMarkup(True)
                    txtKeyItems = str(cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='items'").fetchall()[0][1])
                    txtKeyMngr = cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
                    txtKeyTest = cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='testPay'").fetchall()[0][1]

                    keyboard.txtKeyItems = txtKeyItems
                    keyboard.txtKeyMngr = txtKeyMngr
                    keyboard.txtKeyTest = txtKeyTest

                    keyMain.row(txtKeyItems)
                    keyMain.row(txtKeyMngr)
                    keyMain.row(txtKeyTest)

                    keyboard.keyMain = keyMain

                    # Кнопки главного меню для администратора
                    keyMainAd = types.ReplyKeyboardMarkup(True)
                    keyMainAd.row(txtKeyItems)
                    keyMainAd.row(txtKeyMngr)
                    keyMainAd.row(txtKeyTest)
                    keyMainAd.row(keyboard.txtKeyOpenAdmin)

                    keyboard.keyMainAd = keyMainAd
                    await bot.send_message(message.from_user.id, '✨ Текст кнопки тестовой оплаты изменен', reply_markup=keyboard.keyBtnAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста кнопки тестовой оплаты')


# Изменение текста кнопки менеджера
@dp.message_handler(state=statesGroup.Form.txtBtnMngr)
async def mngr_button_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyBtnAd)
            else:
                async with state.proxy() as data:
                    data['txtBtnMngr'] = message.text
                    txtBtnMngr = data['txtBtnMngr']
                    conn_b = sqlite3.connect('buttons.sqlite3')
                    cursor_b = conn_b.cursor()
                    cursor_b.execute(
                        "UPDATE buttons SET button_text='"+str(txtBtnMngr)+"' WHERE button='manager'")
                    conn_b.commit()

                    # Кнопки главного меню
                    keyMain = types.ReplyKeyboardMarkup(True)
                    txtKeyItems = str(cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='items'").fetchall()[0][1])
                    txtKeyMngr = cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
                    txtKeyTest = cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='testPay'").fetchall()[0][1]

                    keyboard.txtKeyItems = txtKeyItems
                    keyboard.txtKeyMngr = txtKeyMngr
                    keyboard.txtKeyTest = txtKeyTest

                    keyMain.row(txtKeyItems)
                    keyMain.row(txtKeyMngr)
                    keyMain.row(txtKeyTest)

                    keyboard.keyMain = keyMain

                    # Кнопки главного меню для администратора
                    keyMainAd = types.ReplyKeyboardMarkup(True)
                    keyMainAd.row(txtKeyItems)
                    keyMainAd.row(txtKeyMngr)
                    keyMainAd.row(txtKeyTest)
                    keyMainAd.row(keyboard.txtKeyOpenAdmin)

                    keyboard.keyMainAd = keyMainAd
                    await bot.send_message(message.from_user.id, '✨ Текст кнопки менеджера изменен', reply_markup=keyboard.keyBtnAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста кнопки менеджера')


# Изменение текста кнопки главного меню
@dp.message_handler(state=statesGroup.Form.txtBtnMain)
async def main_button_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyBtnAd)
            else:
                async with state.proxy() as data:
                    data['txtBtnMain'] = message.text
                    txtBtnMain = data['txtBtnMain']
                    conn_b = sqlite3.connect('buttons.sqlite3')
                    cursor_b = conn_b.cursor()
                    cursor_b.execute(
                        "UPDATE buttons SET button_text='"+str(txtBtnMain)+"' WHERE button='main'")
                    conn_b.commit()

                    txtKeyMainMenu = cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='main'").fetchall()[0][1]

                    # Кнопки администратора
                    keyAdmin = types.ReplyKeyboardMarkup(True)
                    txtKeySendAd = keyboard.txtKeySendAd
                    txtKeyAnswersAd = keyboard.txtKeyAnswersAd
                    txtKeyBtnAd = keyboard.txtKeyBtnAd
                    txtKeyCatItemAd = keyboard.txtKeyCatItemAd
                    txtKeyWalAd = keyboard.txtKeyWalAd
                    txtKeyAdminAd = keyboard.txtKeyAdminAd
                    txtKeyUsersAd = keyboard.txtKeyUsersAd

                    keyboard.txtKeyMainMenu = txtKeyMainMenu

                    keyAdmin.row(txtKeySendAd)
                    keyAdmin.row(txtKeyAnswersAd)
                    keyAdmin.row(txtKeyBtnAd)
                    keyAdmin.row(txtKeyCatItemAd)
                    keyAdmin.row(txtKeyWalAd)
                    keyAdmin.row(txtKeyAdminAd)
                    keyAdmin.row(txtKeyUsersAd)
                    keyAdmin.row(txtKeyMainMenu)

                    keyboard.keyAdmin = keyAdmin
                    await bot.send_message(message.from_user.id, '✨ Текст кнопки главного меню изменен', reply_markup=keyboard.keyBtnAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста кнопки главного меню')


# Изменение текста кнопки каталога
@dp.message_handler(state=statesGroup.Form.txtBtnCatalog)
async def catalog_button_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyBtnAd)
            else:
                async with state.proxy() as data:
                    data['txtBtnCatalog'] = message.text
                    txtBtnCatalog = data['txtBtnCatalog']
                    conn_b = sqlite3.connect('buttons.sqlite3')
                    cursor_b = conn_b.cursor()
                    cursor_b.execute(
                        "UPDATE buttons SET button_text='"+str(txtBtnCatalog)+"' WHERE button='catalog'")
                    conn_b.commit()

                    txtKeyItemsCat = cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='catalog'").fetchall()[0][1]
                    keyboard.txtKeyItemsCat = txtKeyItemsCat

                    await bot.send_message(message.from_user.id, '✨ Текст кнопки каталога изменен', reply_markup=keyboard.keyBtnAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста кнопки каталога')


# Изменение текста кнопки связаться с менеджером
@dp.message_handler(state=statesGroup.Form.txtBtnSendMngr)
async def sendMngr_button_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyBtnAd)
            else:
                async with state.proxy() as data:
                    data['txtBtnSendMngr'] = message.text
                    txtBtnSendMngr = data['txtBtnSendMngr']
                    conn_b = sqlite3.connect('buttons.sqlite3')
                    cursor_b = conn_b.cursor()
                    cursor_b.execute("UPDATE buttons SET button_text='" +
                                     str(txtBtnSendMngr)+"' WHERE button='sendMngr'")
                    conn_b.commit()

                    txtKeySendMngr = cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='sendMngr'").fetchall()[0][1]
                    keyboard.txtKeySendMngr = txtKeySendMngr

                    await bot.send_message(message.from_user.id, '✨ Текст кнопки связаться с менеджером изменен', reply_markup=keyboard.keyBtnAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста кнопки связаться с менеджером')


# Изменение текста кнопки пререхода к оплате
@dp.message_handler(state=statesGroup.Form.txtBtnGoPay)
async def goPay_button_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyBtnAd)
            else:
                async with state.proxy() as data:
                    data['txtBtnGoPay'] = message.text
                    txtBtnGoPay = data['txtBtnGoPay']
                    conn_b = sqlite3.connect('buttons.sqlite3')
                    cursor_b = conn_b.cursor()
                    cursor_b.execute(
                        "UPDATE buttons SET button_text='"+str(txtBtnGoPay)+"' WHERE button='goPay'")
                    conn_b.commit()

                    txtKeyGoPay = cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='goPay'").fetchall()[0][1]
                    keyboard.txtKeyGoPay = txtKeyGoPay

                    await bot.send_message(message.from_user.id, '✨ Текст кнопки перехода к оплате изменен', reply_markup=keyboard.keyBtnAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста кнопки пререхода к оплате')


# Изменение текста кнопки проверки оплаты
@dp.message_handler(state=statesGroup.Form.txtBtnCheckPay)
async def checkPay_button_edit(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyBtnAd)
            else:
                async with state.proxy() as data:
                    data['txtBtnCheckPay'] = message.text
                    txtBtnCheckPay = data['txtBtnCheckPay']
                    conn_b = sqlite3.connect('buttons.sqlite3')
                    cursor_b = conn_b.cursor()
                    cursor_b.execute("UPDATE buttons SET button_text='" +
                                     str(txtBtnCheckPay)+"' WHERE button='checkPay'")
                    conn_b.commit()

                    txtKeyCheckPay = cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='checkPay'").fetchall()[0][1]
                    keyboard.txtKeyCheckPay = txtKeyCheckPay

                    await bot.send_message(message.from_user.id, '✨ Текст кнопки проверки оплаты изменен', reply_markup=keyboard.keyBtnAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении текста кнопки проверки оплаты')


# Промежуток который принимает категорию при добавлении товара
@dp.message_handler(state=statesGroup.Form.txtCatItem)
async def process_category(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            conn_c = sqlite3.connect('categories.sqlite3')
            cursor_c = conn_c.cursor()
            all_categories = cursor_c.execute(
                "SELECT * FROM categories").fetchall()
            if all_categories:
                for category in all_categories:
                    if message.text == category[0]:
                        async with state.proxy() as data:
                            data['txtCatItem'] = message.text
                        await statesGroup.Form.next()
                        await bot.send_message(message.from_user.id, '✨ Почти готово, введите описание', reply_markup=keyboard.keyCancel)
                    elif message.text == keyboard.txtKeyCancel:
                        await state.finish()
                        await bot.send_message(message.from_user.id,
                                               '💤 Действие отменено', reply_markup=keyboard.keyCatItemAd)
                    elif message.text != category[0] or keyboard.txtKeyCancel:
                        await bot.send_message(message.from_user.id, '💢 Такой категории нет!')
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка выбора категории при добавлении товара')


# Промежуток который принимает описание при добавлении товара
@dp.message_handler(state=statesGroup.Form.txtDesItem)
async def process_category(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyCatItemAd)
            else:
                async with state.proxy() as data:
                    data['txtDesItem'] = message.text
                await statesGroup.Form.next()
                await bot.send_message(message.from_user.id, '✨ Отлично! Теперь введите название и цену разделенную символом |', reply_markup=keyboard.keyCancel)
                await bot.send_message(message.from_user.id, '❗ ВАЖНО\nЦену вводить БЕЗ знака ₽', reply_markup=keyboard.keyCancel)
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка ввода описания при добавлении товара')


# Добовляет товар
@dp.message_handler(state=statesGroup.Form.txtAdd)
async def add_item(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyCatItemAd)
            else:
                async with state.proxy() as data:
                    data['txtAdd'] = message.text
                    txtAdd = data['txtAdd']
                    txtCatItem = data['txtCatItem']
                    txtDesItem = data['txtDesItem']
                    conn_i = sqlite3.connect('items.sqlite3')
                    cursor_i = conn_i.cursor()
                    all_items = cursor_i.execute(
                        "SELECT name FROM items").fetchall()
                    if all_items:
                        for items in all_items:
                            items = items[0]
                        if items == str(txtAdd.split(' | ')[0]):
                            await bot.send_message(message.from_user.id, '💢 Такой товар уже существует')
                        else:
                            cursor_i.execute("INSERT INTO items VALUES ('"+str(random.randint(111111, 999999))+"', '"+str(txtAdd.split(
                                ' | ')[0])+"', '"+str(txtAdd.split(' | ')[1]+' ₽')+"', '"+str(txtCatItem)+"', '"+str(txtDesItem)+"')")
                            conn_i.commit()
                            await bot.send_message(message.from_user.id, '✨ Товар добавлен', reply_markup=keyboard.keyCatItemAd)
                            await state.finish()
                    else:
                        cursor_i.execute("INSERT INTO items VALUES ('"+str(random.randint(111111, 999999))+"', '"+str(txtAdd.split(
                            ' | ')[0])+"', '"+str(txtAdd.split(' | ')[1]+' ₽')+"', '"+str(txtCatItem)+"', '"+str(txtDesItem)+"')")
                        conn_i.commit()
                        await bot.send_message(message.from_user.id, '✨ Товар добавлен', reply_markup=keyboard.keyCatItemAd)
                        await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при добавлении товара')


# Удаляет товар
@dp.message_handler(state=statesGroup.Form.txtDel)
async def del_item(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyCatItemAd)
            else:
                async with state.proxy() as data:
                    data['txtDel'] = message.text
                    txtDel = data['txtDel']
                    conn_i = sqlite3.connect('items.sqlite3')
                    cursor_i = conn_i.cursor()
                    cursor_i.execute(
                        "DELETE FROM items WHERE name='"+str(txtDel)+"'")
                    conn_i.commit()
                    await bot.send_message(message.from_user.id, '✨ Товар удален', reply_markup=keyboard.keyCatItemAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при удалении товара')


# Добавляет категорию
@dp.message_handler(state=statesGroup.Form.txtAddCat)
async def add_item(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyCatItemAd)
            else:
                async with state.proxy() as data:
                    data['txtAddCat'] = message.text
                    txtAddCat = data['txtAddCat']

                    conn_c = sqlite3.connect('categories.sqlite3')
                    cursor_c = conn_c.cursor()
                    all_categories = cursor_c.execute(
                        "SELECT * FROM categories").fetchall()
                    if all_categories:
                        for category in all_categories:
                            category = category[0]
                        if category == txtAddCat:
                            await bot.send_message(message.from_user.id, '💢 Такая категория уже существует')
                        else:
                            conn_c = sqlite3.connect('categories.sqlite3')
                            cursor_c = conn_c.cursor()
                            cursor_c.execute(
                                "INSERT INTO categories VALUES ('"+str(txtAddCat)+"')")
                            conn_c.commit()
                            await bot.send_message(message.from_user.id, '✨ Категория добавлена', reply_markup=keyboard.keyCatItemAd)
                            await state.finish()
                    else:
                        conn_c = sqlite3.connect('categories.sqlite3')
                        cursor_c = conn_c.cursor()
                        cursor_c.execute(
                            "INSERT INTO categories VALUES ('"+str(txtAddCat)+"')")
                        conn_c.commit()
                        await bot.send_message(message.from_user.id, '✨ Категория добавлена', reply_markup=keyboard.keyCatItemAd)
                        await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при добавлении категории')


# Удаляет категорию
@dp.message_handler(state=statesGroup.Form.txtDelCat)
async def del_item(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyCatItemAd)
            else:
                async with state.proxy() as data:
                    data['txtDelCat'] = message.text
                    txtDelCat = data['txtDelCat']
                    conn_c = sqlite3.connect('categories.sqlite3')
                    cursor_c = conn_c.cursor()
                    cursor_c.execute(
                        "DELETE FROM categories WHERE category='"+str(txtDelCat)+"'")
                    conn_c.commit()

                    conn_i = sqlite3.connect('items.sqlite3')
                    cursor_i = conn_i.cursor()
                    cursor_i.execute(
                        "DELETE FROM items WHERE category='"+str(txtDelCat)+"'")
                    conn_i.commit()
                    await bot.send_message(message.from_user.id, '✨ Категория удалена', reply_markup=keyboard.keyCatItemAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при удалении категории')


# Изменяет номер платежа
@dp.message_handler(state=statesGroup.Form.txtWal)
async def update_wallet(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyWalAd)
            else:
                async with state.proxy() as data:
                    data['txtWal'] = message.text
                    txtWal = data['txtWal']
                    conn_w = sqlite3.connect('wallets.sqlite3')
                    cursor_w = conn_w.cursor()
                    cursor_w.execute(
                        "UPDATE wallets SET acc_number=('"+str(txtWal)+"')")
                    conn_w.commit()
                    config.qiwi_number = str(cursor_w.execute(
                        "SELECT * FROM wallets").fetchall()[0][0])
                    await bot.send_message(message.from_user.id, '✨ Кошелек обновлен', reply_markup=keyboard.keyWalAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении номера QIWI')


# Изменяет токен QIWI
@dp.message_handler(state=statesGroup.Form.txtWalToken)
async def update_wallet_token(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyWalAd)
            else:
                async with state.proxy() as data:
                    data['txtWalToken'] = message.text
                    txtWalToken = data['txtWalToken']
                    conn_w = sqlite3.connect('wallets.sqlite3')
                    cursor_w = conn_w.cursor()
                    cursor_w.execute(
                        "UPDATE wallets SET token=('"+str(txtWalToken)+"')")
                    conn_w.commit()
                    config.qiwi_token = str(cursor_w.execute(
                        "SELECT * FROM wallets").fetchall()[0][1])
                    await bot.send_message(message.from_user.id, '✨ Токен обновлен', reply_markup=keyboard.keyWalAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении токена QIWI')


# Изменяет ID администратора
@dp.message_handler(state=statesGroup.Form.txtAdminId)
async def update_wallet_token(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAdminAd)
            else:
                async with state.proxy() as data:
                    data['txtAdminId'] = message.text
                    txtAdminId = data['txtAdminId']
                    conn_a = sqlite3.connect('admin.sqlite3')
                    cursor_a = conn_a.cursor()
                    cursor_a.execute(
                        "UPDATE admin SET value=('"+str(txtAdminId)+"') WHERE name='admin_id'")
                    conn_a.commit()
                    config.admin_id = int(cursor_a.execute(
                        "SELECT * FROM admin WHERE name='admin_id'").fetchall()[0][1])
                    await bot.send_message(message.from_user.id, '✨ ID администратора обновлен', reply_markup=keyboard.keyMain)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении ID администратора')


# Изменяет ID группы
@dp.message_handler(state=statesGroup.Form.txtGroupId)
async def update_wallet_token(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAdminAd)
            else:
                async with state.proxy() as data:
                    data['txtGroupId'] = message.text
                    txtGroupId = data['txtGroupId']
                    conn_a = sqlite3.connect('admin.sqlite3')
                    cursor_a = conn_a.cursor()
                    cursor_a.execute(
                        "UPDATE admin SET value=('"+str(txtGroupId)+"') WHERE name='group_id'")
                    conn_a.commit()
                    config.group_id = str(cursor_a.execute(
                        "SELECT * FROM admin WHERE name='group_id'").fetchall()[0][1])
                    await bot.send_message(message.from_user.id, '✨ Рассылка в группу включена', reply_markup=keyboard.keyAdminAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении ID группы')


# Изменяет username менеджера
@dp.message_handler(state=statesGroup.Form.txtMngrId)
async def update_wallet_token(message, state: FSMContext):
    try:
        if message.from_user.id == config.admin_id:
            if message.text == keyboard.txtKeyCancel:
                await state.finish()
                await bot.send_message(message.from_user.id,
                                       '💤 Действие отменено', reply_markup=keyboard.keyAdminAd)
            else:
                async with state.proxy() as data:
                    data['txtMngrId'] = message.text
                    txtMngrId = data['txtMngrId']
                    conn_a = sqlite3.connect('admin.sqlite3')
                    cursor_a = conn_a.cursor()
                    cursor_a.execute(
                        "UPDATE admin SET value=('"+str(txtMngrId)+"') WHERE name='manager'")
                    conn_a.commit()
                    config.manager = str(cursor_a.execute(
                        "SELECT * FROM admin WHERE name='manager'").fetchall()[0][1])
                    await bot.send_message(message.from_user.id, '✨ Usermane менеджера обновлен', reply_markup=keyboard.keyAdminAd)
                await state.finish()
    except:
        await bot.send_message(message.from_user.id, '💢 Ошибка при изменении username менеджера')


# Реагирование на Call
@dp.callback_query_handler(lambda call: True)
async def del_all_items(call):
    try:
        conn_u = sqlite3.connect('udb.sqlite3')
        cursor_u = conn_u.cursor()

        chat_id = call.from_user.id
        # Удаляет ВСЕ товары
        try:
            if call.data == 'delAllItems_Yes':
                conn_i = sqlite3.connect('items.sqlite3')
                cursor_i = conn_i.cursor()
                all_items = cursor_i.execute("SELECT * FROM items").fetchall()
                if all_items:
                    for item in all_items:
                        cursor_i.execute(
                            "DELETE FROM items WHERE index_item='"+str(item[0])+"'")
                        conn_i.commit()
                    await bot.send_message(chat_id, '✨ Все товары удалены')
            # Отмена удаления ВСЕХ товаров
            elif call.data == 'delAllItems_No':
                await bot.send_message(chat_id, '✨ Товары НЕ будут удалены')
        except:
            await bot.send_message(chat_id, '💢 Ошибка при удалении всех товаров')

        try:
            # Отключает рассылку в группу
            if call.data == 'groupDel_Yes':
                conn_a = sqlite3.connect('admin.sqlite3')
                cursor_a = conn_a.cursor()
                cursor_a.execute(
                    "UPDATE admin SET value=('"+str('None')+"') WHERE name='group_id'")
                conn_a.commit()
                config.group_id = str(cursor_a.execute(
                    "SELECT * FROM admin WHERE name='group_id'").fetchall()[0][1])
                await bot.send_message(chat_id, '✨ Рассылка в группу отключена')
            # Отмена удаления ВСЕХ товаров
            elif call.data == 'groupDel_No':
                await bot.send_message(chat_id, '✨ Рассылка в группу отстается')
        except:
            await bot.send_message(chat_id, '💢 Ошибка при отключении рассылки в группу')

        try:
            # Проверка оплаты
            if call.data == "check":
                try:
                    last_payment = functions.get_last_pay(
                        config.qiwi_number, config.qiwi_token)
                except:
                    await send_in_group("💢 У пользователя возникла проблема с номером или токеном QIWI")
                    txtKeyMngr = cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
                    await bot.send_message(message.from_user.id, '💢 Error #CLLxLP\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))

                conn_m = sqlite3.connect('messages.sqlite3')
                cursor_m = conn_m.cursor()

                current_price = str(cursor_u.execute(
                    "SELECT * FROM udb WHERE uid='"+str(chat_id)+"'").fetchall()[0][2])
                current_IDpay = str(cursor_u.execute(
                    "SELECT * FROM udb WHERE uid='"+str(chat_id)+"'").fetchall()[0][3])

                # Оплата прошла
                qiwiSum = str(last_payment["sum"])
                qiwiCom = str(last_payment["description"])
                if str(qiwiSum) == str(current_price) and str(qiwiCom) == str(current_IDpay):
                    check_message = str(cursor_m.execute(
                        "SELECT * FROM messages WHERE name='check_message'").fetchall()[0][1])
                    await bot.send_message(chat_id, check_message.format(), parse_mode="HTML")
                    await send_in_group("💸 Получена оплата в размере - {}р от юзера @{} с chat_id {}".format(qiwiSum, call.message.chat.username, chat_id))

                    users = functions.DataBase()
                    users.pay(chat_id, qiwiSum)
                    users.close()
                    cursor_u.execute(
                        "DELETE FROM udb WHERE uid='"+str(chat_id)+"'")
                    cursor_u.execute(
                        "INSERT INTO udb VALUES ('"+str(chat_id)+"', 'none', 'none', 'none')")
                    conn_u.commit()

                # Оплаты нет
                else:
                    check_fail_message = str(cursor_m.execute(
                        "SELECT * FROM messages WHERE name='check_fail_message'").fetchall()[0][1])
                    await bot.send_message(chat_id, check_fail_message.format(), parse_mode="HTML")
        except:
            await send_in_group("💢 У пользователя возникла проблема с проверкой оплаты")
            txtKeyMngr = cursor_b.execute(
                "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
            await bot.send_message(message.from_user.id, '💢 Error #CLLxCHK\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))

        # Проверка тестовой оплаты
        try:
            if call.data == "check_test":
                try:
                    last_payment = functions.get_last_pay(
                        config.qiwi_number, config.qiwi_token)
                except:
                    await send_in_group("💢 У пользователя возникла проблема с номером или токеном QIWI")
                    txtKeyMngr = cursor_b.execute(
                        "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
                    await bot.send_message(message.from_user.id, '💢 Error #CLLxLP\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))

                current_price = str(cursor_u.execute(
                    "SELECT * FROM udb WHERE uid='"+str(chat_id)+"'").fetchall()[0][2])
                current_IDpay = str(cursor_u.execute(
                    "SELECT * FROM udb WHERE uid='"+str(chat_id)+"'").fetchall()[0][3])

                # Получена тестовая оплата
                qiwiSum = "1"
                qiwiCom = str(last_payment["description"])
                if str(qiwiSum) == str(current_price) and str(qiwiCom) == str(current_IDpay):
                    check_message = str(cursor_m.execute(
                        "SELECT * FROM messages WHERE name='check_message'").fetchall()[0][1])
                    await bot.send_message(chat_id, check_message.format(), parse_mode="HTML")
                    await send_in_group("💸 Получена тестовая оплата в размере - {}р от юзера @{} с chat_id {}".format(qiwiSum, call.message.chat.username, chat_id))

                    users = functions.DataBase()
                    users.pay(chat_id, qiwiSum)
                    users.close()
                    cursor_u.execute(
                        "DELETE FROM udb WHERE uid='"+str(chat_id)+"'")
                    cursor_u.execute(
                        "INSERT INTO udb VALUES ('"+str(chat_id)+"', 'none', 'none', 'none')")
                    conn_u.commit()

                # Не получена
                else:
                    check_fail_message = str(cursor_m.execute(
                        "SELECT * FROM messages WHERE name='check_fail_message'").fetchall()[0][1])
                    await bot.send_message(chat_id, check_fail_message.format(), parse_mode="HTML")
        except:
            await send_in_group("💢 У пользователя возникла проблема с проверкой тестовой оплаты")
            txtKeyMngr = cursor_b.execute(
                "SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
            await bot.send_message(message.from_user.id, '💢 Error #CLLxCHKtst\nДля получения помощи нажмите на кнопку "{}"'.format(txtKeyMngr))
    except:
        await bot.send_message(chat_id, '💢 Ошибка реагирования на call')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
