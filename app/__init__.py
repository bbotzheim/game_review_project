import re

from flask import Flask
from flask import render_template
from flask import request, jsonify

from app import recommender

N_RECOMMENDATIONS = 10

def create_app():
    app = Flask(__name__)

    recommender_obj = recommender.initialize_recommender("models", "data/Processed Data")

    @app.route("/")
    @app.route("/index")
    def main():
        platforms = sorted(recommender_obj.get_platform_list(), 
                key=lambda x: x["name"])
        genres = sorted(recommender_obj.get_genre_list(),
                key=lambda x: x["name"])
        return render_template("index.html", platforms=platforms, genres=genres)


    @app.route("/api/_recommend-games")
    def recommend_games():
        search_game = request.args.get("game", "", type=str)
        platform = request.args.get("platform", "", type=str)
        genres_str = request.args.get("genres", "", type=str)

        if genres_str == "":
            genre_ids = []
        else:
            genre_ids = [int(gid) for gid in genres_str.split(",")]

        if platform == "":
            platform_id = None
        else:
            platform_id = int(platform)

        recommended_ids = recommender_obj.get_filtered_recommendations(search_game, 
                platform_id, genre_ids, N_RECOMMENDATIONS)

        if recommended_ids is not None:
            recommended_games = [recommended_ids[gid][0] for gid in recommended_ids]
            return jsonify(result=recommended_games, found_flag=True)
        else:
            return jsonify(result="")

    return app

