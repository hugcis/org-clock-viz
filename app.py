from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def base_dashboard():
    return render_template("clock.html")
