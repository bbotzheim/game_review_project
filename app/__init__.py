from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def main():
        return "This is an app!"

    return app

