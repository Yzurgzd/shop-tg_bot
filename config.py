import sqlite3


conn_a = sqlite3.connect('admin.sqlite3')
cursor_a = conn_a.cursor()

conn_w = sqlite3.connect('wallets.sqlite3')
cursor_w = conn_w.cursor()


# токен от бота
token = ''

admin_id = int(cursor_a.execute(
    "SELECT * FROM admin WHERE name='admin_id'").fetchall()[0][1])
# Id группы для оповещений. Добавьте бота в группу @getmyid_bot -375120528
group_id = str(cursor_a.execute(
    "SELECT * FROM admin WHERE name='group_id'").fetchall()[0][1])
manager = str(cursor_a.execute(
    "SELECT * FROM admin WHERE name='manager'").fetchall()[0][1])

qiwi_number = str(cursor_w.execute("SELECT * FROM wallets").fetchall()[0][0])
qiwi_token = str(cursor_w.execute("SELECT * FROM wallets").fetchall()[0][1])
