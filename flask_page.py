from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

@app.route("/<name>/")
def home(name):
    return render_template("index.html", content = name)


@app.route("/admin/")
def admin():
    return redirect(url_for("user", name = "Admin"))

@app.route("/<name>/portfolio")
def porfolio(name):
    return f"Hello, {name}!"

if __name__ == "__main__":
    app.run()