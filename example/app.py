from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'


if __name__ == '__main__':
    # Listen on all interfaces so Docker can route to the container
    app.run(host='0.0.0.0', port=5000)
