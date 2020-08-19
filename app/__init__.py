import re

from flask import Flask
from flask import render_template
from flask import request, jsonify


def create_app():
    app = Flask(__name__)

    @app.route("/")
    @app.route("/index")
    def main():
        return render_template("index.html")


    @app.route("/api/_recommend-games")
    def recommend_games():
        search_game = request.args.get("game", "", type=str)
        platform = request.args.get("platform", "", type=str)
        genres_str = request.args.get("genres", "", type=str)
        genres = genres_str.split(",")

        

        results = ["Result 1", "Result 2", "Result 3"]
        return jsonify(result=results)

    return app

