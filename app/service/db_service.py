import sqlite3

def init_db():
    conn=sqlite3.connect('database/data.db')
    cursor=conn.cursor()
    try:
        cursor.execute("""INSERT OR IGNORE Role (type, role_id) values(?, ?)""",('Adult', 1))
        cursor.execute("""INSERT OR IGNORE Role (type, role_id) values(?, ?)""",('Child', 2))
        cursor.execute("""INSERT OR IGNORE Role (type, role_id) values(?, ?)""",('Admin', 3))
        
        cursor.execute("""INSERT OR IGNORE AccessRightType (name, rightType_id) values(?, ?)""",('Edit', 1))
        cursor.execute("""INSERT OR IGNORE AccessRightType  (name, rightType_id) values(?, ?)""",('Delete', 2))
        cursor.execute("""INSERT OR IGNORE AccessRightType (name, rightType_id) values(?, ?)""",('Manage', 3))

        categories = [
            (1, 'Allowance'),
            (2, 'Gifts'),
            (3, 'Salary'),
            (4, 'Food'),
            (5, 'Entertainment'),
            (6, 'Transport'),
            (7, 'Education'),
            (8, 'Clothing'),
            (9, 'Transaction for Another Account')
        ]
        cursor.executemany("""INSERT OR IGNORE INTO TransactionCategory (category_id, name) VALUES (?, ?)""",
                           categories)
        conn.commit()
    except sqlite3.Error as e:
        print(e.sqlite_errorname)
    conn.close()


def clean_db():
    conn=sqlite3.connect('database/data.db')
    cursor=conn.cursor()
    try:
        cursor.execute("DELETE FROM User;")
        cursor.execute("DELETE FROM Role;")
        cursor.execute("DELETE FROM UserRoles;")
        cursor.execute("DELETE FROM AccessRight;")
        cursor.execute("DELETE FROM AccessRightType;")
        cursor.execute("DELETE FROM Account;")
        cursor.execute("DELETE FROM Transactions;")


        cursor.execute("DELETE FROM sqlite_sequence WHERE name='User';")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='Role';")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='UserRoles';")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='AccessRight';")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='AccessRightType';")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='Account';")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='Transactions';")

        conn.commit()
    except sqlite3.Error as e:
        print(e.sqlite_errorname()) 
    conn.close()