import pandas as pd

def search_films(df, query, page_size=5, page_number=1):
    if not query:
        return pd.DataFrame(), 0
    
    matching_films = df[df['title'].str.contains(query, case=False, na=False)]
    
    # imdb score, descending order
    sorted_films = matching_films.sort_values(by='imdb_score', ascending=False)
    total_results = len(sorted_films)
    
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    paginated_films = sorted_films.iloc[start_index:end_index]
    
    display_columns = ['title', 'release_year', 'imdb_score', 'genres', 'imdb_id', 'description']
    return paginated_films[display_columns], total_results

def recommend(df, filmID, page_size=5, page_number=1):
    selected_film = df[df['imdb_id'] == filmID]
    
    if selected_film.empty:
        print(f"Error: Film with IMDb ID {filmID} not found.")
        return pd.DataFrame(), 0

    selected_genres = selected_film['genres'].iloc[0]
    
    if not selected_genres:
        print(f"No genres found for selected film '{selected_film['title'].iloc[0]}'")
        return pd.DataFrame(), 0

    print("Finding similar films...")

    # Find films that share at least 2 genres with the selected film
    # Exclude the selected film
    potential_recommendations = df[
        (df['imdb_id'] != filmID) & 
        (df['genres'].apply(lambda film_genres: sum(1 for g in film_genres if g in selected_genres) >= 2))
    ]
    
    # Descending order, imdb score
    sorted_recommendations = potential_recommendations.sort_values(by='imdb_score', ascending=False)
    
    total_results = len(sorted_recommendations)
    
    # Calculate start and end index for pagination
    start_index = (page_number - 1) * page_size
    end_index = start_index + page_size
    
    paginated_recommendations = sorted_recommendations.iloc[start_index:end_index]
    
    display_columns = ['title', 'release_year', 'imdb_score', 'genres']
    return paginated_recommendations[display_columns], total_results
