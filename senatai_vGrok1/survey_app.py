from flask import Flask, request, render_template, redirect, url_for, session
from survey_database import SurveyDatabase

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Change this for production
db = SurveyDatabase()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_id = db.verify_user(username, password)
        if user_id:
            session["user_id"] = user_id
            return redirect(url_for("dashboard"))
        return "Login failed! <a href='/'>Try again</a>"
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    user_id = session["user_id"]
    tokens = db.get_user_tokens(user_id)
    return render_template("dashboard.html", tokens=tokens, username=user_id)

@app.route("/transfer", methods=["POST"])
def transfer():
    if "user_id" not in session:
        return redirect(url_for("login"))
    to_user_id = request.form["to_username"]
    amount = float(request.form["amount"])
    from_user_id = session["user_id"]
    if db.transfer_tokens(from_user_id, to_user_id, amount):
        return redirect(url_for("dashboard"))
    return "Transfer failed! <a href='/dashboard'>Back</a>"

if __name__ == "__main__":
    app.run(debug=True)

