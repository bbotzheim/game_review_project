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
                key=lambda x: x["num_games"], reverse=True)
        return render_template("index.html", platforms=platforms, genres=genres)


    @app.route("/api/_recommend-games")
    def recommend_games():
        search_game = request.args.get("game", "", type=str)
        platform = request.args.get("platform", "", type=str)
        genres_str = request.args.get("genres", "", type=str)

        if search_game == "":
            return jsonify(result="", error="No game input :(")

        if genres_str == "":
            genre_ids = []
        else:
            genre_ids = [int(gid) for gid in genres_str.split(",")]

        if platform == "":
            platform_id = None
        else:
            platform_id = int(platform)

        game_id = recommender_obj.lookup_game_id(search_game, platform_id)
        if len(game_id) == 0:
            return jsonify(result="", error="Unable to match the input name to a game :(")

        recommended_ids = recommender_obj.get_filtered_recommendations(game_id, 
                platform_id, genre_ids, N_RECOMMENDATIONS)

        if recommended_ids is not None:
            recommended_games = [recommended_ids[gid][0] for gid in recommended_ids]
            return jsonify(result=recommended_games)
        else:
            return jsonify(result="", error="Unable to find any matches :(")

    @app.route("/api/_complete-games")
    def complete_games():
        partial = request.args.get("game_partial", "", type=str)
        completions = recommender_obj.get_game_completions(partial)
        return jsonify(result=completions)

    return app


