from flask import Flask, render_template_string

app = Flask(__name__)


@app.route('/')
def index():
    # Serve the rideshare.html content
    return render_template_string(open('rideshare.html').read())


if __name__ == '__main__':
    app.run(port=5000)
