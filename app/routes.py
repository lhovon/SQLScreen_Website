from app import app
from app.forms import LoginForm
from app.models.user import User
from flask import render_template, request, make_response, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user
import simplejson as json
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
        )
        user.set_password(form.password.data)
        try:
            user.create()
            flash("Congratulations, you are now a registered user!")
            return redirect(url_for("login"))
        except Exception as e:
            print(e)
            flash("Could not register. Try again.")
            return redirect(url_for("register"))

    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = LoginForm()
    if form.validate_on_submit():

        user = User.get_by_username(form.username.data)
        print(user)

        print(form.password.data)

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))

        login_user(user, remember=form.remember_me.data)
        flash(f"Hello {user.firstname}")

        next = request.args.get("next")
        if not next or url_parse(next).netloc != "":
            next = url_for("index")
        return redirect(next)

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/load", methods=["POST"])
def load():
    data = request.json
    query_where_clause = data["sql"]
    limit = data["limit"]
    offset = data["offset"]
    sortby = data["sortby"]
    sortorder = data["sortorder"]

    # query_where_clause = (
    #     "symbol in ('CEE', 'FOUR', 'HMM.A', 'MCS', 'RBX', 'TAL', 'VCI',  'AAB', 'AAV', 'AC', 'ACB')"
    # )

    print("Received data: " + query_where_clause)

    fields = """ symbol, name, sector, industry, exshortname, price, pricechange, percentchange, price, openprice, prevclose, dayhigh, 
        daylow, weeks52high, weeks52low, day21movingavg, day50movingavg, day200movingavg, volume, averagevolume10d, averagevolume30d, 
        averagevolume50d, shareoutstanding, marketcap, totalsharesoutstanding, marketcapallclasses, sharesescrow, 
        alpha, beta, eps, peratio, pricetobook, pricetocashflow, returnonequity, returnonassets, totaldebttoequity, vwap, 
        dividendfrequency, dividendyield, dividendamount, dividendcurrency, exdividenddate, dividendpaydate """

    query = f"select {fields} from quotes where {query_where_clause} order by {sortby} {sortorder} limit {limit} offset {offset};"

    # TODO: What is the best practice here? Should the app have a single connection or every call generate its own?
    query_result = db.exec_realdict(query)

    json_result = json.dumps(query_result, default=str, use_decimal=True)
    print(len(json_result))

    return make_response(json_result, 200)


# Endpoint called when query is submitted.
@app.route("/results", methods=["GET", "POST"])
def submit_query():

    query_where_clause = request.args.get("q")

    query = f"select count(*) from quotes where {query_where_clause};"

    # TODO: What is the best practice here? Should the app have a single connection or every call generate its own?
    number_results = db.exec_realdict(query)

    return render_template("query-result.html", query=query_where_clause)


# Test url to see results page without having to go through usual flow
@app.route("/submit-query", methods=["GET"])
def submit_query_old():

    query_where_clause = "symbol in ('CRDL.WT', 'TRL.WT', 'BXR', 'EKG', 'LRT.UN', 'AGF.B')"

    fields = """ symbol, name, sector, industry, exshortname, price, pricechange, percentchange, price, openprice, prevclose, dayhigh,
        daylow, weeks52high, weeks52low, day21movingavg, day50movingavg, day200movingavg, volume, averagevolume10d, averagevolume30d,
        averagevolume50d, shareoutstanding, marketcap, totalsharesoutstanding, marketcapallclasses, sharesescrow,
        alpha, beta, eps, peratio, pricetobook, pricetocashflow, returnonequity, returnonassets, totaldebttoequity, vwap,
        dividendfrequency, dividendyield, dividendamount, dividendcurrency, exdividenddate, dividendpaydate """

    query = f"select {fields} from quotes where {query_where_clause};"

    query_result = db.execute_self_contained(query)

    return render_template("query-result_old.html", query=query, query_result=query_result)


@app.context_processor
def utility_processor():
    def get_symbol(change):
        if change < 0:
            return "-"
        else:
            return "+"

    def format_change(change):
        return "{:+.2f}".format(change)

    def format_2_decimals(change):
        if change is None or change == 0:
            return "-"
        return "{:.2f}".format(change)

    def format_comma(amount):
        if amount is None or amount == 0:
            return "-"
        return "{:,}".format(amount)

    def format_price(price):
        if price is None:
            return "-"
        return "{:.2f}".format(price)

    def not_none(s):
        if s is None:
            return "-"
        return s

    def abbreviate(x):
        if x is None:
            return "-"
        abbreviations = ["", "K", "M", "B", "T"]
        base = "1"
        i = 0
        while len(base) < len(str(x)) - 3:
            base += "000"
            i += 1
        base = round(x / int(base), 2)
        return str(base) + abbreviations[i]

    def format_financial(x):
        if x is None:
            return "-"
        # return str(round(x, 4))
        return "{:.4f}".format(x).rstrip("0").rstrip(".")

    def format_divi_date(date):
        if date is not None:
            return date.strftime("%Y-%m-%d")
        return date

    return dict(
        format_change=format_change,
        format_2_decimals=format_2_decimals,
        format_comma=format_comma,
        format_price=format_price,
        not_none=not_none,
        abbreviate=abbreviate,
        format_financial=format_financial,
        format_divi_date=format_divi_date,
    )
