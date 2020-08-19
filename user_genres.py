import itertools
from collections import OrderedDict
from statistics import mean
import pandas as pd

movie_data = pd.read_csv(r"ml-latest-small\movies.csv")
ratings_data = pd.read_csv(r"ml-latest-small\ratings.csv", usecols=["movieId", "rating", "userId"])
movie_data_merged = pd.merge(ratings_data, movie_data, on='movieId')

def other_users_genres(userId = None):
    other_user_genre_dict = {}
    user_list = set(movie_data_merged["userId"])
    def lister(userID):
        user_data = movie_data_merged.loc[movie_data_merged['userId'] == userID]
        user_data = user_data.sort_values('rating', ascending=False).drop_duplicates(subset=['movieId', 'title'], keep='first')
        filtered_genres = list(user_data["genres"])
        filtered_ratings = list(user_data["rating"])
        user_data = user_data.join(user_data.genres.str.split('|', expand=True))
        user_data = user_data.rename(columns={0:'genre1', 1:'genre2', 2:'genre3', 3:'genre4', 4:'genre5', 5:'genre6', 6:'genre7'})
        user_data = user_data.drop(['genres'], 1)
        genre_list = [ "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", 
        "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"]  
        rating_dict = {}
        for variable in genre_list:
            rating_dict[variable] = 0
        for x in range(len(filtered_genres)):
            for y in range(len(genre_list)):
                if genre_list[y] in filtered_genres[x]:
                    rating_dict[genre_list[y]] = rating_dict[genre_list[y]] + float((filtered_ratings[x])/5)
        rating_dict = OrderedDict(sorted(rating_dict.items(), key=lambda t: t[1], reverse=True))
        x = list(itertools.islice(rating_dict.keys(), 0, 5))
        return x
    
    if userId != None:
        user_list.remove(userId)
    for userID in user_list:
        other_user_genre_dict[userID] = lister(userID)

    return other_user_genre_dict   
