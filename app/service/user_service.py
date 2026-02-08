import sqlite3
import hashlib
from app.modules.User import User

role_mapping = {
    "Adult": 1,
    "Child": 2,
    "Admin": 3
}
access_rights_mapping = {
    "Edit": 1,
    "Delete": 2,
    "Manage": 3
}


def is_user(form):
    password = hashlib.md5(form['password'].encode()).hexdigest()
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    result = cursor.execute("""SELECT 
                          user_id 
                          FROM User 
                          WHERE username=? and password=?""",
                            (form['username'], password)).fetchall()

    if len(result):
        return result[0]
    conn.close()
    return 0


def get_all_users():
    conn = sqlite3.connect('database/data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    result_users = cursor.execute(""" SELECT 
                User.user_id,
                User.fullName,
                User.username,
                User.email,
                User.password,
                User.creationDate,
                Account.balance,
                Account.name,
                GROUP_CONCAT(DISTINCT Role.type) AS roles,
                GROUP_CONCAT(DISTINCT AccessRightType.name) AS accessRights,
                AccessRight.amountLimit AS budget 
                FROM User
                LEFT JOIN UserRoles ON User.user_id = UserRoles.user_id
                LEFT JOIN Role ON UserRoles.role_id = Role.role_id
                LEFT JOIN Account ON User.user_id = Account.user_id
                LEFT JOIN AccessRight ON User.user_id = AccessRight.user_id
                LEFT JOIN AccessRightType ON AccessRight.rightType_id = AccessRightType.rightType_id
                GROUP BY User.user_id, Account.balance, Account.name, AccessRight.amountLimit;
    """).fetchall()

    users = []

    for row in result_users:
        roles_list = row["roles"].split(",") if row["roles"] else None
        access_rights_list = row["accessRights"].split(",") if row["accessRights"] else None
        print(roles_list)
        users.append(User(row["fullName"], row["username"],
                          row["email"], row["password"], row["user_id"],
                          row["creationDate"], row["balance"],row["budget"] ,row["name"],
                          roles_list, access_rights_list
                          ))
    conn.close()
    return users


def get_user_data(id):
    conn = sqlite3.connect('database/data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if isinstance(id, tuple):
        id = id[0]

    result_user = cursor.execute(
        """
        SELECT fullname, username, email, password, creationDate
        FROM User
        WHERE user_id = ?
        """,
        (id,)
    ).fetchone()

    if not result_user:
        conn.close()
        print(f"User with id {id} not found.")

    result_account = cursor.execute(
        """
        SELECT balance, name
        FROM Account
        WHERE user_id = ?
        """,
        (id,)
    ).fetchone()

    result_role = cursor.execute(
        """
        SELECT type
        FROM User
        JOIN UserRoles ON User.user_id = UserRoles.user_id
        JOIN Role ON UserRoles.role_id = Role.role_id
        WHERE User.user_id = ?
        """,
        (id,)
    ).fetchall()

    result_access_rights = cursor.execute(
        """
        SELECT name, amountLimit
        FROM AccessRightType
        JOIN AccessRight ON AccessRightType.rightType_id = AccessRight.rightType_id
        JOIN User ON User.user_id = AccessRight.user_id
        WHERE User.user_id = ?
        """,
        (id,)
    ).fetchall()

    print(f"User: {result_user['fullname']}")
    print(f"Balance: {result_account['balance']}")
    print(f"Access Rights: {[ar['name'] for ar in result_access_rights]}")
    print(f"Roles: {[rl['type'] for rl in result_role]}")

    user = User(
        fullname=result_user['fullname'],
        username=result_user['username'],
        email=result_user['email'],
        password=result_user['password'],
        uid=id,
        creationDate=result_user['creationDate'],
        balance=result_account['balance'] if result_account else None,
        budget=result_access_rights[0]["amountLimit"] if result_access_rights else None,
        account=result_account['name'] if result_account else None,
        accessRights=[ar["name"] for ar in result_access_rights]
    )

    for role in result_role:
        user.add_role(role['type'])

    conn.close()
    return user


def add_first_user(form):
    conn = sqlite3.connect('database/data.db')
    password = hashlib.md5(form["password"].encode()).hexdigest()
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO User 
                   (username, fullname, email, password) 
                   values(?,?,?,?)""",
                       (form["username"], form["fullname"], form["email"], password))
        last_user_id = cursor.lastrowid
        cursor.execute("""INSERT INTO 
                       UserRoles (user_id, role_id)
                       VALUES (?, ?)""",
                       (last_user_id, 3))
        cursor.execute("""INSERT INTO 
                       UserRoles (user_id, role_id)
                       VALUES (?, ?)""",
                       (last_user_id, 1))
        cursor.execute("""INSERT INTO 
                       Account (user_id, name, balance) VALUES (?, ?, ?)""",
                       (last_user_id, f"{form['fullname']}@{form['username']}", 0.00))

        cursor.execute("""INSERT INTO 
                       AccessRight (user_id, rightType_id, endOfValidity, amountLimit, expirationDate) 
                       VALUES (?, ?, ?, ?, ?)
                       """, (last_user_id, 3, None, 1000.00, None))
        conn.commit()
    except sqlite3.Error as e:
        print(f" function registration of admin: {e}")
    conn.close()
    return


def add_user(form):
    conn = sqlite3.connect('database/data.db')
    password = hashlib.md5(form["password"].encode()).hexdigest()
    cursor = conn.cursor()

    try:
        cursor.execute("""INSERT INTO User 
                   (username, fullname, email, password) 
                   values(?,?,?,?)""",
                       (form["username"], form["fullname"], form.get("email"), password))
        last_user_id = cursor.lastrowid
        cursor.execute("""INSERT INTO 
                       Account (user_id, name, balance) VALUES (?, ?, ?)""",
                       (last_user_id, f"{form['fullname']}@{form['username']}", 0.00))

        conn.commit()
    except sqlite3.Error as e:
        print(f" function add user: {e}")
    conn.close()


def update_user(form):
    conn = sqlite3.connect('database/data.db')
    password = hashlib.md5(form["password"].encode()).hexdigest()
    role = role_mapping.get(form["role"])
    right = access_rights_mapping.get(form["right"])
    cursor = conn.cursor()
    try:
        cursor.execute("""UPDATE User SET username=?,fullname=?,password=? WHERE user_id=?""",
                       (form["username"], form["fullname"], password, form["user_id"])
                       )

        cursor.execute("""
        SELECT 1 FROM UserRoles WHERE user_id = ? AND role_id = ?
            """, (form["user_id"], role))

        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO UserRoles (user_id, role_id)
                VALUES (?, ?) """, (form["user_id"], role))
        else:
            print("This role is already assigned to the user.")

        cursor.execute("""
        SELECT 1 FROM AccessRight WHERE user_id = ? AND rightType_id = ?
            """, (form["user_id"], right))

        if cursor.fetchone() is None:
            cursor.execute(""" INSERT OR IGNORE INTO 
                       AccessRight (user_id, rightType_id,  endOfValidity,  amountLimit, expirationDate) 
                       VALUES (?, ?, ?, ?, ?)
                       """, (form["user_id"], right, None, 1000.00, None))
        else:
            print("This right is already assigned to the user.")

        conn.commit()
    except sqlite3.Error as e:
        print(f" Error updating user: {e}")
    conn.close()


def change_budget(form):
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""UPDATE AccessRight SET amountLimit=? WHERE user_id=?""", (form["limit"], form["user_id"]))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error deleting transaction: {e}")
    conn.close()


def delete_user_right(form):
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    try:
        right_id=access_rights_mapping.get(form["right"])     
        cursor.execute("""DELETE FROM AccessRight WHERE user_id = ? AND rightType_id = ?""", (form["user_id"], right_id))
        conn.commit()
        print("User right deleted successfully!")
    except sqlite3.Error as e:
        print(f"Error deleting user right: {e}")
    finally:
        conn.close()


def delete_user(user_id):
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''DELETE FROM User WHERE user_id = ?''', (user_id,))
        cursor.execute('''DELETE FROM Account WHERE user_id = ?''', (user_id,))
        cursor.execute('''DELETE FROM AccessRight WHERE user_id = ?''', (user_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f" function delete user: {e}")
    conn.close()