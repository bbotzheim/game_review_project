import gensim
from gensim.models.doc2vec import Doc2Vec
import os

import pandas as pd

def initialize_recommender(model_path, table_path):
    doc2vec_model = Doc2Vec.load(model_path+'/doc2vec.model')

    games = pd.read_csv(os.path.join(table_path, "games.csv"))
    platforms = pd.read_csv(os.path.join(table_path, "platforms.csv"))
    genres = pd.read_csv(os.path.join(table_path, "genres.csv"))
    game_genre_tags = pd.read_csv(os.path.join(table_path, "game_genre_tags.csv"))

    return Recommender(doc2vec_model, games, platforms, genres, game_genre_tags)



class Recommender(object):
    def __init__(self, model, games_df, platform_df, genre_df, game_genre_tags_df):
        self.model = model
        self.games_df = games_df
        self.platform_df = platform_df
        self.genre_df = genre_df
        self.game_genre_tags_df = game_genre_tags_df
        
        self.genre_dict = {}
        for i in self.game_genre_tags_df['game_ID'].unique():
            self.genre_dict[i] = [self.game_genre_tags_df['genre_ID'][j] for j in self.game_genre_tags_df[self.game_genre_tags_df['game_ID']==i].index]

    def get_platform_list(self):
        '''Gets a list of dicts containing platform name and id from the platform data table
        
        Returns:
            A list of dicts containing the following entries:
            - "name": the common name of the platform
            - "id": The (internal use) ID of the platform
            - "game_count": The number of games recorded which are for that platform
        '''
        platform_list = []
        for platform_row in self.platform_df.itertuples():
            platform_id = platform_row.platform_ID
            num_games = sum(self.games_df["platform_ID"] == platform_id)
            platform_entry = {"name": platform_row.platform, "id": platform_id, "num_games": num_games}
            platform_list.append(platform_entry)
        return platform_list

    def get_genre_list(self):
        '''Gets a list of dicts containing genre name and id from the genre data table
        
        Returns:
            A list of dicts containing the following entries:
            - "name": the common name of the genre
            - "id": The (internal use) ID of the genre
            - "game_count": The number of games recorded which are labelled as that genre
        '''
        genre_list = []
        for genre_row in self.genre_df.itertuples():
            genre_id = genre_row.genre_ID
            num_games = sum(self.game_genre_tags_df["genre_ID"] == genre_id)
            genre_entry = {"name": genre_row.genre_name, "id": genre_id, "num_games": num_games}
            genre_list.append(genre_entry)
        # genre_list = [{"name": t.genre_name, "id": t.genre_ID} for t in self.genre_df.itertuples()]
        return genre_list

    def create_lookup(self):
        '''Helper method that creates a lookup dictionary (from the games table) to easily filter by game ID.'''
        self.lookup_df = self.games_df[['game_ID', 'title', 'platform_ID', 'summary', 'url']]
        self.lookup_df['game_ID'] = self.lookup_df['game_ID'].astype(str)
        self.lookup_dict = self.lookup_df.set_index('game_ID').to_dict(orient='index')
        return self.lookup_dict
        
    def get_recommendations(self, keyword, n = 100):
        '''Helper method that calls the Doc2Vec model to get recommendations.
            
            Args:
                keyword: A single Game ID or a list of IDs, to build recommendations from.
                    Must be strings. 
                n: Number of recommendations to return (default = 100)
        '''
        return self.model.docvecs.most_similar(keyword, topn=n)

    def get_filtered_recommendations(self, keyword, platform_ID, genre_IDs, n):
        ''' Method that takes a keyword to build recommendations from, and filters recommendations by game 
        platform and genres, to the top 'n' recommendations.
                Input: 
                keyword = game ID (string)
                platform_ID = platform ID (integer)
                genre_IDs = genre ID (list of integers)
                n = number of recommendations to return (integer)
                
                Output:
                filtered_results = dictionary
        '''
        lookup_dict = self.create_lookup()
        ranked_results = self.get_recommendations(keyword)
        
        filtered_results = {}

        for game in ranked_results:
            if len(filtered_results) < n:
                dict_id = int(game[0])
                dict_game_name = lookup_dict[game[0]]['title']
                dict_platform_ID = lookup_dict[game[0]]['platform_ID']
                dict_summary = lookup_dict[game[0]]['summary']
                dict_url = lookup_dict[game[0]]['url']

                if dict_id not in self.genre_dict:
                    self.genre_dict[dict_id] = []

                if (platform_ID is None) and (len(genre_IDs) == 0):
                    filtered_results[dict_id] = lookup_dict[game[0]]

                elif len(genre_IDs) == 0:
                    if (dict_platform_ID == platform_ID):
                        if dict_id in filtered_results:
                            continue
                        else:
                            filtered_results[dict_id] = lookup_dict[game[0]]

                elif platform_ID is None:
                    if set(genre_IDs) & set(self.genre_dict[dict_id]) > 0:
                        if dict_id in filtered_results:
                            continue
                        else:
                            filtered_results[dict_id] = lookup_dict[game[0]]

                elif (dict_platform_ID == platform_ID) and (len(set(genre_IDs) & set(self.genre_dict[dict_id])) > 0):
                        if dict_id in filtered_results:
                            continue
                        else:  
                            filtered_results[dict_id] = lookup_dict[game[0]]

        if len(filtered_results) > 0:
            return filtered_results
        else:
            return None
        
    def lookup_value(self, id_number, id_type):
        '''Method that looks up the value of the ID number for a game, platform, or genre.
                Input: 
                id_number = game, platform, or genre ID (integer)
                id_type = must equal 'game', 'platform', or 'genre'
                
                Output:
                Corresponding name for a genre or platform ID (as string). Returns the entire corresponding
                row for a game ID.
        '''
        if id_type == 'game':
            return self.games_df[self.games_df['game_ID']==id_number]
            
        elif id_type == 'platform':
            return self.platform_df[self.platform_df['platform_ID']==id_number]['platform'].iloc[0]
        
        elif id_type == 'genre':
            return self.genre_df[self.genre_df['genre_ID']==id_number]['genre_name'].iloc[0]
        
        else:
            raise ValueError("id_type must equal 'game', 'platform', or 'genre'")
            
    def lookup_id(self, name, id_type):
        '''Method that looks up the ID of a game, platform, or genre.
                Input: 
                name = game, platform, or genre name (string)
                id_type = must equal 'game', 'platform', or 'genre
                
                Output:
                Corresponding ID for a genre or platform name (as integer). Returns the entire corresponding
                row for a game.
        '''
        if id_type == 'game':
            return self.games_df[self.games_df['title']==name]
            
        elif id_type == 'platform':
            return self.platform_df[self.platform_df['platform']==name]['platform_ID'].iloc[0]
        
        elif id_type == 'genre':
            return self.genre_df[self.genre_df['genre_name']==name]['genre_ID'].iloc[0]
        
        else:
            raise ValueError("id_type must equal 'game', 'platform', or 'genre'. Error may be caused by\
            no corresponding ID for input 'name'.")


    def lookup_game_id(self, game_name, platform_id=None):
        game_matches =  self.games_df[self.games_df['title']==game_name]
        if platform_id is not None:
            platform_matches = game_matches[game_matches['platform_ID']==platform_id]
            if len(platform_matches) > 0:
                game_matches = platform_matches

        # Converted to string for input into get_recommendations
        return [str(i) for i in game_matches["game_ID"].tolist()]

    def get_game_completions(self, partial_name):
        '''Returns a list of games which match the partial name provided'''
        games_lower = self.games_df["title"].str.lower()
        start_matches = self.games_df[games_lower.str.match(partial_name.lower())]["title"]
        matches = sorted(start_matches.unique())
        return matches
            
        