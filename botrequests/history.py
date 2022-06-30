import sqlite3

conn = sqlite3.connect('/Users/macbook/PycharmProjects/python_basic_diploma/database/tele_bot.db', check_same_thread=False)
cursor = conn.cursor()


def update_history_db(user_id: int, username: str, command: str, command_date, hotels):
    cursor.execute(
        """
    INSERT INTO `telebot_history` (user_id, username, hotels, command, command_date) VALUES 
        (?, ?, ?, ?, ?);
    """,
        (user_id, username, hotels, command, command_date),
    )
    conn.commit()


def get_history_db(username):
    history_list = []
    history_str = ''
    cursor.execute(
        """
    SELECT command, command_date, hotels FROM 'telebot_history' WHERE username == (?)
    """,
        (username, )
    )
    result = cursor.fetchall()
    for res in result:
        for r in res:
            history_str += str(r) + ' '
            history_list.append(history_str)
    return history_list

#
# print(get_history_db('aleksashkaprog'))