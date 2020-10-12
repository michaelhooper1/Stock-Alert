from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello! This is your main page <h1>HOME <h1>"

if __name__ == "__main__":
    app.run()