import sqlite3

conn = sqlite3.connect('/Users/macbook/PycharmProjects/python_basic_diploma/tele_bot.db', check_same_thread=False)
cursor = conn.cursor()


def update_history_db(user_id: int, username: str, command: str, command_date):
    cursor.execute(
        """
    INSERT INTO `telebot_history` (user_id, username, command, command_date) VALUES 
        (?, ?, ?, ?);
    """,
        (user_id, username, command, command_date),
    )
    conn.commit()


def update_history_hotels_db(hotels: str):
    cursor.execute(
        """
    INSERT INTO `telebot_history` (hotels) VALUES 
        (?);
    """,
        (hotels),
    )
    conn.commit()


def get_history_db(username):
    history_list = []
    cursor.execute(
        """
    SELECT command, command_date FROM 'telebot_history' WHERE username == (?)
    """,
        (username, )
    )
    result = cursor.fetchall()
    for res in result:
        for r in res:
            history_list.append(r)
    return history_list

