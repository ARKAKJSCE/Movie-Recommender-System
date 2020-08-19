import itertools
from collections import OrderedDict
from statistics import mean
import pandas as pd
from user_genres import other_users_genres
import sys

movie_data = pd.read_csv(r"ml-latest-small\movies.csv")
ratings_data = pd.read_csv(r"ml-latest-small\ratings.csv", usecols=["movieId", "rating", "userId"])
movie_data_merged = pd.merge(ratings_data, movie_data, on='movieId')
movie_data_merged['mean'] = pd.DataFrame(movie_data_merged.groupby('movieId')['rating'].mean())
movie_data_merged['rating_counts'] = pd.DataFrame(movie_data_merged.groupby('movieId')['rating'].count())
movie_data_merged = movie_data_merged[movie_data_merged['rating_counts']>=50].sort_values('mean', ascending=False)

choice = str(input("Are you a new user, or existing user? Enter 'n' for new, 'e' for existing: "))
if choice == 'e':
    try:
        userID = int(input("Please enter userId: "))
        if userID > 610:
            print("User doesn't exist")
            sys.exit()
        user_data = (movie_data_merged.loc[movie_data_merged['userId'] == userID])
        user_data = user_data.sort_values('rating', ascending=False).drop_duplicates(subset=['movieId', 'title'], keep='first')
        filtered_genres = list(user_data["genres"])
        filtered_ratings = list(user_data["rating"])
        filtered_movies = list(user_data["title"])
        user_data = user_data.join(user_data.genres.str.split('|', expand=True))
        user_data = user_data.rename(columns={0:'genre1', 1:'genre2', 2:'genre3', 3:'genre4', 4:'genre5', 5:'genre6', 6:'genre7'})
        user_data = user_data.drop(['genres'], 1)

        def favourite_genres():
            genre_list = [ "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", "Documentary", "Drama", "Fantasy"
            , "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"]  
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

        print("Seems like your top 5 genres are: ")
        for el in favourite_genres():
            print(el)

        mask = (movie_data_merged.loc[movie_data_merged['userId'] == userID])
        recommender_data = movie_data_merged.drop(mask.index)

        mask = recommender_data['title'].isin(filtered_movies)
        recommender_data = recommender_data[~mask]
        recommender_data.drop_duplicates(subset=['movieId', 'title'], keep='first', inplace=True)
        recommender_data = recommender_data.join(recommender_data.genres.str.split('|', expand=True))
        recommender_data = recommender_data.rename(columns={0:'genre1', 1:'genre2', 2:'genre3', 3:'genre4', 4:'genre5'})
        recommender_data = recommender_data.drop(['genres', 'rating'], 1)
        recommender_data["index"] = range(1, len(recommender_data)+1)
        recommender_data.set_index("index", inplace=True)

        def genre_similarity():
            column_list = recommender_data.columns.to_list()
            movie_list = list(recommender_data['title'])
            genre_header_list = []
            listno = []
            movie_genre_dict = {}
            for column in column_list:
                if 'genre' in column:
                    genre_header_list.append(column)
            for each in genre_header_list:
                listno.append(list(recommender_data[each]))
            for size in range(len(listno[0])):
                genre_list = []
                for each in listno:
                    genre_list.append(each[size])
                movie_genre_dict[movie_list[size]] = genre_list 
                #Contains a dict of all possible movies for recommendation and their genres in a list. 
                # The key is the movie title, value is list of genres.
            recommendations = {}
            for k,v in movie_genre_dict.items():
                count = 0
                for genre in v:
                    if genre in favourite_genres():
                        count = count + 1
                if count >= 2:
                    recommendations[k] = recommender_data[recommender_data['title'] == k]['mean'].values[0]
            recommendations = OrderedDict(sorted(recommendations.items(), key=lambda t: t[1], reverse=True))
            return recommendations

        def user_similarity():
            global movie_data_merged
            number = 0
            dict_movies = {}
            for k,v in other_users_genres(userId = userID).items():
                for el in favourite_genres():
                    if el in v:
                        number = number + 1
                if number >= 2:
                    new_dataframe = movie_data_merged.loc[movie_data_merged['userId'] == k]
                    new_dataframe = new_dataframe.drop(['mean', 'rating_counts'], 1).sort_values('rating', ascending=False)
                    for movies in list(new_dataframe['title']):
                        dict_movies[movies] = new_dataframe[new_dataframe['title'] == movies]['rating'].values[0]
            dict_movies = OrderedDict(sorted(dict_movies.items(), key=lambda t: t[1], reverse=True))
            return dict_movies

        print('\nWe think you will like these movies: \n')
        for k in genre_similarity().keys():
            for vi in user_similarity().keys():
                if k == vi:
                    print(k)

    except Exception as ex:
        message = f"An exception of type {type(ex).__name__} occurred. \nArguments: {ex.args}"
        replacements = [',', '(', ')']
        for _ in replacements:
            message = message.replace(_, '')
        print(message) 

elif choice == 'n':
    try:
        genre_list = [ "Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", "Documentary", 
        "Drama", "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"]  
        genre_dict = {}
        user_genre_list = []
        for x in range(len(genre_list)):
            genre_dict[x] = genre_list[x]
        for k,v in genre_dict.items():
            print(k,'-',v)
        genres = [int(x) for x in input("Enter your favourite genre numbers: ").split()] 
        print('\nThese are what you chose: ')
        for x in genres:
            print(genre_dict[x])
            user_genre_list.append(genre_dict[x])
        print('\n')

        def genre_similarity_new():
            all_data = movie_data_merged.sort_values('rating', ascending=False).drop_duplicates(subset=['movieId', 'title'], keep='first')
            all_data = all_data.join(all_data.genres.str.split('|', expand=True))
            all_data = all_data.rename(columns={0:'genre1', 1:'genre2', 2:'genre3', 3:'genre4', 4:'genre5', 5:'genre6', 6:'genre7'}).drop(['genres'], 1)
            column_list = all_data.columns.to_list()
            movie_list = list(all_data['title'])
            genre_header_list = []
            listno = []
            movie_genre_dict = {}
            for column in column_list:
                if 'genre' in column:
                    genre_header_list.append(column)
            for each in genre_header_list:
                listno.append(list(all_data[each]))
            for size in range(len(listno[0])):
                genre_list = []
                for each in listno:
                    genre_list.append(each[size])
                movie_genre_dict[movie_list[size]] = genre_list 
                #Contains a dict of all possible movies for recommendation and their genres in a list. The key is the movie title, value is list of genres.
            recommendations = {}
            for k,v in movie_genre_dict.items():
                count = 0
                for genre in v:
                    if genre in user_genre_list:
                        count = count + 1
                if count >= 2:
                    recommendations[k] = all_data[all_data['title'] == k]['mean'].values[0]
            recommendations = OrderedDict(sorted(recommendations.items(), key=lambda t: t[1], reverse=True))
            return recommendations

        def user_similarity_new():
            global movie_data_merged
            number = 0
            dict_movies = {}
            for k,v in other_users_genres().items():
                for el in user_genre_list:
                    if el in v:
                        number = number + 1
                if number >= 2:
                    new_dataframe = movie_data_merged.loc[movie_data_merged['userId'] == k]
                    new_dataframe = new_dataframe.drop(['mean', 'rating_counts'], 1).sort_values('rating', ascending=False)
                    for movies in list(new_dataframe['title']):
                        dict_movies[movies] = new_dataframe[new_dataframe['title'] == movies]['rating'].values[0]        
            dict_movies = OrderedDict(sorted(dict_movies.items(), key=lambda t: t[1], reverse=True))
            return dict_movies

        print('We think you will like these movies: \n')
        for k in genre_similarity_new().keys():
            for vi in user_similarity_new().keys():
                if k == vi:
                    print(k)

    except Exception as ex:
        message = f"An exception of type {type(ex).__name__} occurred. \nArguments: {ex.args}"
        replacements = [',', '(', ')']
        for _ in replacements:
            message = message.replace(_, '')
        print(message)    

