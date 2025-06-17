import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os

def analyze_data(df):
    if df.empty:
        print("DataFrame is empty. Cannot perform EDA.")
        return
    os.makedirs('img', exist_ok=True)
    # Ensure numeric types and drop NaNs for critical columns
    df['imdb_score'] = pd.to_numeric(df['imdb_score'], errors='coerce')
    df['imdb_votes'] = pd.to_numeric(df['imdb_votes'], errors='coerce')
    df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
    df['runtimeMinutes'] = pd.to_numeric(df['runtimeMinutes'], errors='coerce')
    df.dropna(subset=['imdb_score', 'imdb_votes', 'release_year'], inplace=True)

    print(f"Total films for analysis after cleaning: {len(df)}")

    # Distribution of IMDb Scores
    print("\n--- Distribution of IMDb Scores ---")
    plt.figure(figsize=(10, 6))
    sns.histplot(df['imdb_score'], bins=20, kde=True)
    plt.title('Distribution of IMDb Scores')
    plt.xlabel('IMDb Score')
    plt.ylabel('Number of Films')
    plt.grid(axis='y', alpha=0.75)
    plt.tight_layout()
    try:
        plt.savefig('img/imdb_score_distribution.png')
        print("Generated 'imdb_score_distribution.png'")
    except Exception as e:
        print(f"Error generating imdb_score_distribution.png: {e}")
    finally:
        plt.clf() # Clear the current figure
        plt.close() # Close the figure to free memory

    # Top N Films by IMDb Score
    print("\n--- Top 10 Films by IMDb Score ---")
    top_films = df.sort_values(by='imdb_score', ascending=False).head(10)

    plt.figure(figsize=(12, 7))
    sns.barplot(x='imdb_score', y='title', data=top_films, palette='viridis')
    plt.title('Top 10 Films by IMDb Score')
    plt.xlabel('IMDb Score')
    plt.ylabel('Film Title')
    plt.tight_layout()
    try:
        plt.savefig('img/top_films_by_imdb_score.png')
        print("Generated 'top_films_by_imdb_score.png'")
    except Exception as e:
        print(f"Error generating top_films_by_imdb_score.png: {e}")
    finally:
        plt.clf()
        plt.close()

    # Films by Release Year
    print("\n--- Films by Release Year ---")
    plt.figure(figsize=(12, 6))
    films_per_year = df['release_year'].value_counts().sort_index()
    films_per_year.plot(kind='bar')
    plt.title('Number of Films Released Per Year')
    plt.xlabel('Release Year')
    plt.ylabel('Number of Films')
    plt.xticks(rotation=90, ha='right')
    plt.tight_layout()
    try:
        plt.savefig('img/films_per_year.png')
        print("Generated 'films_per_year.png'")
    except Exception as e:
        print(f"Error generating films_per_year.png: {e}")
    finally:
        plt.clf()
        plt.close()

    # Genre Distribution
    print("\n--- Genre Distribution ---")
    all_genres = [genre for sublist in df['genres'] for genre in sublist]
    genre_counts = Counter(all_genres)
    top_genres = pd.DataFrame(genre_counts.most_common(10), columns=['Genre', 'Count'])

    plt.figure(figsize=(12, 7))
    sns.barplot(x='Count', y='Genre', data=top_genres)
    plt.title('Top 10 Most Common Genres')
    plt.xlabel('Count')
    plt.ylabel('Genre')
    plt.tight_layout()
    try:
        plt.savefig('img/top_genres_distribution.png')
        print("Generated 'top_genres_distribution.png'")
    except Exception as e:
        print(f"Error generating top_genres_distribution.png: {e}")
    finally:
        plt.clf()
        plt.close()

    # Average IMDb Score per Genre
    print("\n--- Average IMDb Score per Genre ---")
    genre_scores = {}
    for index, row in df.iterrows():
        for genre in row['genres']:
            if genre not in genre_scores:
                genre_scores[genre] = []
            genre_scores[genre].append(row['imdb_score'])

    avg_genre_scores = {genre: sum(scores) / len(scores) for genre, scores in genre_scores.items() if scores}
    avg_genre_scores_df = pd.DataFrame(list(avg_genre_scores.items()), columns=['Genre', 'Average IMDb Score'])
    avg_genre_scores_df = avg_genre_scores_df.sort_values(by='Average IMDb Score', ascending=False).head(10)

    plt.figure(figsize=(12, 7))
    sns.barplot(x='Average IMDb Score', y='Genre', data=avg_genre_scores_df)
    plt.title('Top 10 Genres by Average IMDb Score')
    plt.xlabel('Average IMDb Score')
    plt.ylabel('Genre')
    plt.xlim(6.0, 8.0)
    plt.tight_layout()
    try:
        plt.savefig('img/avg_imdb_score_per_genre.png')
        print("Generated 'avg_imdb_score_per_genre.png'")
    except Exception as e:
        print(f"Error generating avg_imdb_score_per_genre.png: {e}")
    finally:
        plt.clf()
        plt.close()

    # Title Type Distribution
    print("\n--- Title Type Distribution ---")
    if 'titleType' in df.columns:
        title_type_counts = df['titleType'].value_counts().head(10)
        plt.figure(figsize=(10, 6))
        sns.barplot(x=title_type_counts.index, y=title_type_counts.values)
        plt.title('Distribution of Top 10 Title Types')
        plt.xlabel('Title Type')
        plt.ylabel('Count')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        try:
            plt.savefig('img/title_type_distribution.png')
            print("Generated 'title_type_distribution.png'")
        except Exception as e:
            print(f"Error generating title_type_distribution.png: {e}")
        finally:
            plt.clf()
            plt.close()
    else:
        print("\n'titleType' column not found in. Skipping")

    print("\nDone")
