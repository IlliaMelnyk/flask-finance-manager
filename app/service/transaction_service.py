import sqlite3

def delete_account(form):
    conn=sqlite3.connect('database/data.db')
    cursor=conn.cursor()
    try:
        cursor.execute('''DELETE FROM Account WHERE name = ?''', (form["change_account_name"],))
        conn.commit()
    except sqlite3.Error as e:
        print(f" function delete account: {e}")
    conn.close()

def delete_transaction(transaction_id):
    conn=sqlite3.connect('database/data.db')
    cursor=conn.cursor()
    try:
        cursor.execute('''DELETE FROM Transactions WHERE transaction_id = ?''', (transaction_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error deleting transaction: {str(e)}")
    conn.close()


def add_new_transaction(form, user_id):
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    try:
        is_private = 1 if 'private' in form else 0
        date = form['date']
        selected_account_id = form.get('selected_account_id')

        cursor.execute("""SELECT account_id FROM Account WHERE account_id = ? AND user_id = ?""",
                       (selected_account_id, user_id))
        result_account = cursor.fetchone()
        if not result_account:
            raise ValueError("The selected account is invalid or does not belong to the user.")

        if form['type'] == 'income':
            from_account_id = 0
            to_account_id = selected_account_id
            cursor.execute("""INSERT INTO Transactions (category_id, amount, type, date, isPrivate, from_account_id, to_account_id, owner_id)
                              VALUES (?, ?, 'income', ?, ?, ?, ?, ?)""",
                           (int(form['category_id']), float(form['amount']), date, is_private, from_account_id,
                            to_account_id, user_id))

        elif form['type'] == 'outcome':
            from_account_id = selected_account_id
            to_account_name = form.get('to_account_name')

            if to_account_name:
                cursor.execute("""SELECT account_id, user_id FROM Account WHERE name = ?""", (to_account_name,))
                result_to_account = cursor.fetchone()

                if not result_to_account:
                    raise ValueError("The specified recipient account does not exist.")
                to_account_id = result_to_account[0]
                to_user_id = result_to_account[1]
            else:
                to_account_id = from_account_id  # If no specific account is mentioned, stay within the same account

            cursor.execute("""INSERT INTO Transactions (category_id, amount, type, date, isPrivate, from_account_id, to_account_id, owner_id)
                              VALUES (?, ?, 'outcome', ?, ?, ?, ?, ?)""",
                           (int(form['category_id']), float(form['amount']), date, is_private, from_account_id,
                            to_account_id, user_id))

            
            if to_account_name:
                cursor.execute("""INSERT INTO Transactions (category_id, amount, type, date, isPrivate, from_account_id, to_account_id, owner_id)
                                  VALUES (?, ?, 'income', ?, ?, ?, ?, ?)""",
                               (int(form['category_id']), float(form['amount']), date, is_private, from_account_id,
                                to_account_id, to_user_id))

        conn.commit()

    except ValueError as ve:
        raise ve
    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        conn.close()


def get_all_transactions(account_id, user_id, role, rights):
    conn = sqlite3.connect('database/data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if "Manage" in rights:
        transactions = cursor.execute("""
            SELECT 
                Transactions.type,
                TransactionCategory.name AS category_name,
                Transactions.amount,
                Transactions.date,
                Transactions.isPrivate,
                Transactions.transaction_id,
                User.username AS owner_name,
                Transactions.owner_id
            FROM Transactions
            LEFT JOIN TransactionCategory ON Transactions.category_id = TransactionCategory.category_id
            LEFT JOIN User ON Transactions.owner_id = User.user_id
            ORDER BY Transactions.date DESC
        """).fetchall()



    elif "Adult" in role and "Edit" in rights:
        # Adult with Edit right can see their own transactions and transactions of children (excluding private transactions)
        transactions = cursor.execute("""
    SELECT 
        Transactions.type,
        TransactionCategory.name AS category_name,
        Transactions.amount,
        Transactions.date,
        Transactions.isPrivate,
        Transactions.transaction_id,
        User.username AS owner_name,
        Transactions.owner_id
    FROM Transactions
    LEFT JOIN TransactionCategory ON Transactions.category_id = TransactionCategory.category_id
    LEFT JOIN User ON Transactions.owner_id = User.user_id
    LEFT JOIN UserRoles ON User.user_id = UserRoles.user_id
    LEFT JOIN Role ON UserRoles.role_id = Role.role_id
    WHERE 
        (Transactions.owner_id = ? 
          OR
          (Role.type = 'Child' AND Transactions.isPrivate = 0)
        )
        AND (
            (Transactions.from_account_id = ? AND Transactions.type = 'outcome') 
            OR 
            (Transactions.to_account_id = ? AND Transactions.type = 'income')
         OR
        (Role.type = 'Child' AND Transactions.isPrivate = 0)
    )
    ORDER BY Transactions.date DESC
""", (user_id, account_id, account_id)).fetchall()



    else:
        transactions = cursor.execute("""
            SELECT 
                Transactions.type,
                TransactionCategory.name AS category_name,
                Transactions.amount,
                Transactions.date,
                Transactions.isPrivate,
                Transactions.transaction_id,
                User.username AS owner_name,
                Transactions.owner_id
            FROM Transactions
            LEFT JOIN TransactionCategory ON Transactions.category_id = TransactionCategory.category_id
            LEFT JOIN User ON Transactions.owner_id = User.user_id
            WHERE 
                Transactions.owner_id = ?
                AND (
                    (Transactions.from_account_id = ? AND Transactions.type = 'outcome') OR
                    (Transactions.to_account_id = ? AND Transactions.type = 'income')
                )
            ORDER BY Transactions.date DESC
        """, (user_id, account_id, account_id)).fetchall()

    conn.close()
    return transactions



def get_account_info(user_id):
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    if isinstance(user_id, tuple):
        user_id = user_id[0]
    try:
        accounts = cursor.execute('''SELECT name,balance,account_id FROM Account WHERE user_id = ?''', (user_id,)).fetchall()
        conn.commit()
    except sqlite3.Error as e:
        print(f" function account info: {e}")
    conn.close()
    return accounts


def get_account_summary(account_id):
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    if isinstance(account_id, tuple):
        account_id = account_id[0]
    try:
        income = cursor.execute("""
            SELECT SUM(amount) 
            FROM Transactions 
            WHERE type = 'income' AND to_account_id = ?
        """, (account_id,)).fetchone()[0] or 0

        outcome = cursor.execute("""
            SELECT SUM(amount) 
            FROM Transactions 
            WHERE type = 'outcome' AND from_account_id = ?
        """, (account_id,)).fetchone()[0] or 0
    except sqlite3.Error as e:
        print(f"Error calculating income and outcome: {e}")
        income, outcome = 0, 0
    finally:
        conn.close()
    return {"income": income, "outcome": outcome}


def update_transaction(form, role):
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()

    if "Child" in role:
        is_private = 1 if 'private' in form else 0
    else:
        is_private = 0

    try:
        transaction_id = form['transaction_id']
        amount = float(form['amount'])
        category_id = int(form['category_id'])
        transaction_date = form['date']
        transaction_type = form['type']

        cursor.execute(""" 
            SELECT type, from_account_id, to_account_id, amount
            FROM Transactions
            WHERE transaction_id = ?
        """, (transaction_id,))
        transaction = cursor.fetchone()

        if not transaction:
            raise ValueError("Transaction not found.")

        original_transaction_type, from_account_id, to_account_id, original_amount = transaction

        cursor.execute("""
            UPDATE Transactions
            SET amount = ?, category_id = ?, date = ?, isPrivate = ?, type = ?
            WHERE transaction_id = ?
        """, (amount, category_id, transaction_date, is_private, transaction_type, transaction_id))

        if original_transaction_type == "outcome":
            cursor.execute("""
                SELECT transaction_id
                FROM Transactions
                WHERE type = 'income' 
                AND amount = ? 
                AND date = ? 
                AND from_account_id = ? 
                AND to_account_id = ?
            """, (original_amount, transaction_date, from_account_id, to_account_id))
            linked_transaction = cursor.fetchone()

            if linked_transaction:
                linked_transaction_id = linked_transaction[0]
                cursor.execute("""
                    UPDATE Transactions
                    SET amount = ?, category_id = ?, date = ?
                    WHERE transaction_id = ?
                """, (amount, category_id, transaction_date, linked_transaction_id))

        conn.commit()

    except ValueError as ve:
        print(f"Error: {ve}")
        raise ValueError(f"Invalid data provided for updating transaction: {ve}")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        raise Exception(f"Database error: {e}")
    finally:
        conn.close()
        print("Connection closed.")

def add_account(form,user_id):
    conn=sqlite3.connect('database/data.db')
    cursor=conn.cursor()
    try:
        cursor.execute("""INSERT INTO Account(user_id, name, balance) VALUES (?,?,?)""",(user_id,form["account_name"],0.00))
        conn.commit()
    except sqlite3.Error as e:
        print(f" function add user: {e}")
    conn.close()

def change_account_name(form,account_id):
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""UPDATE Account SET name = ? WHERE account_id = ?""", (form["change_account_name"], account_id))
        conn.commit()
        print("Account name updated successfully!")
    except sqlite3.Error as e:
        print(f"Error updating account name: {e}")
    finally:
        conn.close()
def get_all_accounts():
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    try:
        accounts = cursor.execute('''SELECT account_id, user_id, name, balance FROM Account''').fetchall()
    except sqlite3.Error as e:
        print(f"Error fetching accounts: {e}")
        accounts = []
    conn.close()
    return accounts
def get_account_summ(account_id):
    conn = sqlite3.connect('database/data.db')
    cursor = conn.cursor()
    summary = {"income": 0, "outcome": 0, "categories": {}}

    # Příjmy podle kategorií
    income_data = cursor.execute('''
        SELECT c.name, SUM(t.amount)
        FROM Transactions t
        JOIN TransactionCategory c ON t.category_id = c.category_id
        WHERE t.to_account_id = ?
        GROUP BY c.name
    ''', (account_id,)).fetchall()

    print("Income Categories:", income_data)  # Pro diagnostiku

    for category, amount in income_data:
        if category not in summary["categories"]:
            summary["categories"][category] = 0  # Inicializace kategorie na 0, pokud ještě neexistuje
        summary["categories"][category] += amount
        summary["income"] += amount

    # Výdaje podle kategorií
    outcome_data = cursor.execute('''
        SELECT c.name, SUM(t.amount)
        FROM Transactions t
        JOIN TransactionCategory c ON t.category_id = c.category_id
        WHERE t.from_account_id = ?
        GROUP BY c.name
    ''', (account_id,)).fetchall()

    print("Outcome Categories:", outcome_data)  # Pro diagnostiku

    for category, amount in outcome_data:
        if category not in summary["categories"]:
            summary["categories"][category] = 0  # Inicializace kategorie na 0, pokud ještě neexistuje
        summary["categories"][category] += amount
        summary["outcome"] += amount

    conn.close()
    return summary
