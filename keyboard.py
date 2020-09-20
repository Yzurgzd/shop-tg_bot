from aiogram import types

import sqlite3
import config


conn_b = sqlite3.connect('buttons.sqlite3')
cursor_b = conn_b.cursor()


# Тексата для кнопок
# Открытие панели администратора
txtKeyOpenAdmin = '⚙ Панель администратора'

# Создание кпнопок
# Общие кнопки
txtKeyBackAdmin = '⬅ Назад в панель администратора'
txtKeyItemsCat = cursor_b.execute("SELECT * FROM buttons WHERE button='catalog'").fetchall()[0][1]
txtKeyMainMenu = cursor_b.execute("SELECT * FROM buttons WHERE button='main'").fetchall()[0][1]
txtKeySendMngr = cursor_b.execute("SELECT * FROM buttons WHERE button='sendMngr'").fetchall()[0][1]
txtKeyGoPay = cursor_b.execute("SELECT * FROM buttons WHERE button='goPay'").fetchall()[0][1]
txtKeyCheckPay = cursor_b.execute("SELECT * FROM buttons WHERE button='checkPay'").fetchall()[0][1]

# Кнопки администратора
keyAdmin = types.ReplyKeyboardMarkup(True)
txtKeySendAd = '✉ Отправить сообщение пользователям'
txtKeyAnswersAd = '📢 Ответы бота'
txtKeyBtnAd = '🛎 Кнопки'
txtKeyCatItemAd = '🛍 Категории и товары'
txtKeyWalAd = '🏦 Оплата'
txtKeyAdminAd = '🔐 Администрирование'
txtKeyUsersAd = '👥 Показ пользователей'

keyAdmin.row(txtKeySendAd)
keyAdmin.row(txtKeyAnswersAd)
keyAdmin.row(txtKeyBtnAd)
keyAdmin.row(txtKeyCatItemAd)
keyAdmin.row(txtKeyWalAd)
keyAdmin.row(txtKeyAdminAd)
keyAdmin.row(txtKeyUsersAd)
keyAdmin.row(txtKeyMainMenu)

# Кнопки 'Ответы бота' у администратора
keyAnswersAd = types.ReplyKeyboardMarkup(True)
txtKeyStart = '💬 Стартовое сообщение'
txtKeyPay = '💬 Текст оплаты'
txtKeyPayTest = '💬 Текст тестовой оплаты'
txtKeyCheck = '💬 Ответ успешной оплаты'
txtKeyCheckFail = '💬 Ответ безуспешной оплаты'
txtKeyMain = '💬 Ответ главного меню'
txtKeyCatalog = '💬 Ответ каталога'
txtKeyManager = '💬 Текста менеджера'
txtKeyCat = '💬 Ответ категории'
txtKeyItemsMiss = '💬 Ответ отсутствия товаров'

keyAnswersAd.row(txtKeyStart)
keyAnswersAd.row(txtKeyPay)
keyAnswersAd.row(txtKeyPayTest)
keyAnswersAd.row(txtKeyCheck)
keyAnswersAd.row(txtKeyCheckFail)
keyAnswersAd.row(txtKeyMain)
keyAnswersAd.row(txtKeyCatalog)
keyAnswersAd.row(txtKeyManager)
keyAnswersAd.row(txtKeyCat)
keyAnswersAd.row(txtKeyItemsMiss)
keyAnswersAd.row(txtKeyBackAdmin)

# Кнопки 'Кнопки' у администратора, изменяет тект кнопок
keyBtnAd = types.ReplyKeyboardMarkup(True)
txtKeyEdMain = '🔘 Кнопка главного меню'
txtKeyEdItems = '🔘 Кнопка товаров'
txtKeyEdCatalog = '🔘 Кнопка каталога'
txtKeyEdMngr = '🔘 Кнопка менеджера'
txtKeyEdSendMngr = '🔘 Кнопка связаться с менеджером'
txtKeyEdTestPay = '🔘 Кнопка тестовой оплаты'
txtKeyEdGoPay = '🔘 Кнопка перехода к оплате'
txtKeyEdCheckPay = '🔘 Кнопка проверки оплаты'

keyBtnAd.row(txtKeyEdMain)
keyBtnAd.row(txtKeyEdItems)
keyBtnAd.row(txtKeyEdCatalog)
keyBtnAd.row(txtKeyEdMngr)
keyBtnAd.row(txtKeyEdSendMngr)
keyBtnAd.row(txtKeyEdTestPay)
keyBtnAd.row(txtKeyEdGoPay)
keyBtnAd.row(txtKeyEdCheckPay)
keyBtnAd.row(txtKeyBackAdmin)

# Кнопки 'Категории и товар' у администратора
keyCatItemAd = types.ReplyKeyboardMarkup(True)
txtKeyAdd = '➕ Добавить товар'
txtKeyDel = '✖ Удалить товар'
txtKeyDelAll = '❌ Удалить все товары'
txtKeyAddCat = '➕ Добавить категорию'
txtKeyDelCat = '✖ Удалить категорию'

keyCatItemAd.row(txtKeyAdd)
keyCatItemAd.row(txtKeyDel)
keyCatItemAd.row(txtKeyDelAll)
keyCatItemAd.row(txtKeyAddCat)
keyCatItemAd.row(txtKeyDelCat)
keyCatItemAd.row(txtKeyBackAdmin)

# Кнопки 'Оплата' у администратора
keyWalAd = types.ReplyKeyboardMarkup(True)
txtKeyWal = '👛 Изменить номер QIWI'
txtKeyWalToken = '🔖 Изменить токен QIWI'

keyWalAd.row(txtKeyWal)
keyWalAd.row(txtKeyWalToken)
keyWalAd.row(txtKeyBackAdmin)

# Кнопки 'Администрирование' у администратора
keyAdminAd = types.ReplyKeyboardMarkup(True)
txtKeyAdminId = '🔑 ID администратора'
txtKeyGroupId = '🔑 Добавить рассылку в группу'
txtKeyGroupIdDel = '🔑 Отключить рассылку в группу'
txtKeyMngrId = '🔑 Username Менеджера'

keyAdminAd.row(txtKeyAdminId)
keyAdminAd.row(txtKeyGroupId)
keyAdminAd.row(txtKeyGroupIdDel)
keyAdminAd.row(txtKeyMngrId)
keyAdminAd.row(txtKeyBackAdmin)

# Кнопка отмены
keyCancel = types.ReplyKeyboardMarkup(True)
txtKeyCancel = '⭕ Отмена'

keyCancel.row(txtKeyCancel)

# Кнопки главного меню
keyMain = types.ReplyKeyboardMarkup(True)
txtKeyItems = str(cursor_b.execute("SELECT * FROM buttons WHERE button='items'").fetchall()[0][1])
txtKeyMngr = cursor_b.execute("SELECT * FROM buttons WHERE button='manager'").fetchall()[0][1]
txtKeyTest = cursor_b.execute("SELECT * FROM buttons WHERE button='testPay'").fetchall()[0][1]

keyMain.row(txtKeyItems)
keyMain.row(txtKeyMngr)
keyMain.row(txtKeyTest)

# Кнопки главного меню для администратора
keyMainAd = types.ReplyKeyboardMarkup(True)

keyMainAd.row(txtKeyItems)
keyMainAd.row(txtKeyMngr)
keyMainAd.row(txtKeyTest)
keyMainAd.row(txtKeyOpenAdmin)
