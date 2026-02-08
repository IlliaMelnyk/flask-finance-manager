from flask import Blueprint, render_template, request, redirect, session, flash
from app.service.user_service import *
from app.service.transaction_service import *
from functools import wraps
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

auth = Blueprint('auth', __name__, template_folder='templates')


def authentication(f):
    @wraps(f)
    def wraper(*args, **kwargs):
        if 'user' in session:
            return f(*args, **kwargs)
        else:
            return redirect('/homepage/sign_in')

    return wraper


def is_limit_exceeded(user_id):
    outcome = get_account_summary(get_account_info(user_id)[0][2])["outcome"]
    budget = get_user_data(user_id).budget
    if budget and outcome:
        return outcome > budget
    else:
        print(f"is limit exceeded error: budget = {budget}, outcome = {outcome}")


def plot_statistic(outcome, income, category_data=None):
    fig1, ax1 = plt.subplots(figsize=(6, 5))
    bar_width = 0.35

    ax1.bar([0], outcome, bar_width, label="Outcome", color="r")
    ax1.bar([0.5], income, bar_width, label="Income", color="b")
    ax1.set_ylabel("Amount")
    ax1.set_title("Outcome vs Income")
    ax1.set_xticks([])
    ax1.legend()

    plt.tight_layout()
    plt.savefig("app/static/img/outcome_income_chart.png")
    plt.close(fig1)

    if category_data:
        fig2, ax2 = plt.subplots(figsize=(6, 5))
        labels = list(category_data.keys())
        values = list(category_data.values())
        ax2.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax2.set_title("Categories Distribution")

        plt.tight_layout()
        plt.savefig("app/static/img/category_distribution_chart.png")
        plt.close(fig2)



@auth.route('/auth/account', methods=['GET', 'POST'])
@authentication
def account():
    user = get_user_data(session['user'])
    accounts = get_account_info(user.get_id())
    selected_account_id = int(request.form.get("selected_account")) if request.method == 'POST' and request.form.get(
        "selected_account") else accounts[0][2]

    if request.method == 'POST':
        if request.form["action"] == "add_transaction":
            try:
                add_new_transaction(request.form, user.get_id())
                selected_account_id = int(request.form.get("selected_account_id"))
                flash("Transaction successfully added!", "success")
                return redirect('/auth/account')
            except ValueError as ve:
                flash(str(ve), "error")
            except ValueError as ve:
                flash(str(ve), "error")
        elif request.form["action"] == "delete_transaction":
            transaction_id = request.form.get("transaction_id")
            delete_transaction(transaction_id)
        elif request.form["action"] == "add_account":
            add_account(request.form, user.get_id())
            accounts = get_account_info(user.get_id())
            selected_account_id = accounts[-1][2]
        elif request.form["action"] == "change_name":
            change_account_name(request.form, selected_account_id)
            return redirect(f"/auth/account?selected_account_id={selected_account_id}")
        elif request.form["action"] == "delete_account":
            delete_account(request.form)
            return redirect(request.referrer)
        elif request.form["action"] == "edit_transaction":
            try:
                update_transaction(request.form,user.get_roles())
                flash("Transaction successfully updated!", "success")
            except ValueError as ve:
                flash(f"Invalid data: {ve}", "error")
            except Exception as e:
                flash(f"An error occurred: {e}", "error")


    for account in accounts:
        if account[2] == selected_account_id:
            selected_account_name = account[0]
            balance = account[1]
            break

    summary = get_account_summary(selected_account_id)
    list_of_transactions = get_all_transactions(selected_account_id,user.get_id(),user.get_roles(),user.get_rights())
    income = summary["income"]
    outcome = summary["outcome"]
    calculated_balance = balance + income - outcome

    return render_template(
        "/mainpage/account.html",
        role=user.get_roles(),
        transactions=list_of_transactions,
        accounts=accounts,
        selected_account_id=selected_account_id,
        selected_account_name=selected_account_name,
        balance=calculated_balance,
        income=income,
        outcome=outcome,
    )


@auth.route('/auth/family', methods=["GET", "POST"])
@authentication
def family():
    session_user = get_user_data(session['user'])
    list_of_users = get_all_users()
    if request.method == 'POST':
        if request.form["action"] == "add_smember":
            user = is_user(request.form)
            if not user:
                add_user(request.form)
                flash("New family member successfully added!", "success")
            else:
                return render_template("/mainpage/family.html",
                                       session_user=session_user,
                                       role=session_user.get_roles(), is_limit_exceeded=is_limit_exceeded,
                                       right=session_user.get_rights(), users=list_of_users)
        elif request.form["action"] == "delete_member":
            user_id = request.form["user_id"]
            if int(user_id) != session_user.uid:
                delete_user(user_id)
                flash("Family member successfully deleted!", "success")
            else:
                flash(f"{session_user.fullname} are in session!", "error")

        elif request.form["action"] == "change_budget":
            change_budget(request.form)
            flash("Budget was successfully changed!", "success")

        elif request.form["action"] == "change_access":
            update_user(request.form)
            flash("Editing was successfully!", "success")

        elif request.form["action"] == "delete_access": 
            user=get_user_data(request.form["user_id"])
            if not request.form.get("right"):
                flash("Please select right!", "error")
            if request.form.get("right") not in user.get_rights():
                flash("This right is not assigned to the user!", "error")
            else:
                delete_user_right(request.form)
                flash("Right successfully deleted!", "success")

    list_of_users = get_all_users()
    return render_template("/mainpage/family.html",
                           session_user=session_user,
                           role=session_user.get_roles(), is_limit_exceeded=is_limit_exceeded,
                           right=session_user.get_rights(), users=list_of_users)


@auth.route('/auth/statistic', methods=['GET', 'POST'])
@authentication
def statistic():
    selected_user_id = str(request.form.get("user_id", "all"))
    list_of_users = [{"uid": str(user.uid), "fullname": user.fullname} for user in get_all_users()]

    if selected_user_id == 'all':
        accounts = get_all_accounts()
        total_income, total_outcome = 0, 0
        category_data = {
            "Allowance": 0, "Gifts": 0, "Salary": 0,
            "Food": 0, "Entertainment": 0, "Transport": 0,
            "Education": 0, "Clothing": 0, "Transaction for Another Account": 0
        }

        for account in accounts:
            account_summary = get_account_summ(account[0])
            total_income += account_summary["income"]
            total_outcome += account_summary["outcome"]

            for category, amount in account_summary["categories"].items():
                category_data[category] += amount

        plot_statistic(total_outcome, total_income, category_data)
        return render_template("/mainpage/statistic.html", users=list_of_users, selected_user_id=selected_user_id)

    account_info = get_account_info(selected_user_id)
    if not account_info:
        return render_template("/mainpage/statistic.html", users=list_of_users, selected_user_id=selected_user_id)

    account_id = account_info[0][2]
    account_summary = get_account_summ(account_id)

    outcome = account_summary["outcome"]
    income = account_summary["income"]
    category_data = account_summary["categories"]

    plot_statistic(outcome, income, category_data)
    return render_template("/mainpage/statistic.html", users=list_of_users, selected_user_id=selected_user_id)


@auth.route('/auth/log_out')
@authentication
def log_out():
    session.pop('user')
    return redirect("/")


