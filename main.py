import textwrap
import pandas as pd
from data_cleaner import genreFilter, merge_data, prepareFullData
from recommender import search_films, recommend
from data_analyzer import analyze_data

FILMDATA = 'data/data.csv'
GENRES_RAW = 'data/title.basics.tsv'
GENRES_FILTERED = 'data/filtered_genres.tsv'

def main():
    #merged_data=phase1()
    phase2()

def get_merged_data():
    return phase1()

def phase1():
    # Data Preparation
    print("\n--- Data Preparation ---")
    if not genreFilter(GENRES_RAW, FILMDATA, GENRES_FILTERED):
        print("Data preparation failed. Exiting.")
        return pd.DataFrame()

    merged_data = merge_data(FILMDATA, GENRES_FILTERED)
    if merged_data.empty:
        print("No data loaded or merged. Exiting.")
        return pd.DataFrame()

    print(f"\nSuccessfully prepared data. Total films available: {len(merged_data)}")
    print("Sample of prepared data:")
    print(merged_data.head())
    return merged_data

def displayInfo(selected_film_row):
    print("\n--- Film Information ---")
    print(f"Title: {selected_film_row['title']}")
    print(f"Release Year: {selected_film_row['release_year']}")
    print(f"IMDb Score: {selected_film_row['imdb_score']:.1f}")
    genres_str = ', '.join(selected_film_row['genres']) if selected_film_row['genres'] else 'N/A'
    print(f"Genres: {genres_str}")
    description = selected_film_row.get('description', 'N/A')
    wrapped_desc = textwrap.fill(description, width=70)
    print(f"Description: {wrapped_desc}")

def recommendHandler(merged_data, filmID, filmTitle):
    pageSize = 5
    currentPage = 1

    while True:
        print(f"\nGenerating recommendations for '{filmTitle}' (Page {currentPage})...")
        recommendations_df, total_recommendations = recommend(merged_data, filmID, pageSize, currentPage)

        if recommendations_df.empty:
            print("No recommendations found.")
            break

        totalPage = (total_recommendations + pageSize - 1) // pageSize
        print(f"\n--- Top Recommendations (Page {currentPage}/{totalPage}) ---")
        for i, row in recommendations_df.iterrows():
            genres_str = ', '.join(row['genres']) if row['genres'] else 'N/A'
            print(f"- {row['title']} ({row['release_year']}) - IMDb: {row['imdb_score']:.1f} - Genres: {genres_str}")
        
        options = []
        if currentPage < totalPage:
            options.append("Next Page (n)")
        if currentPage > 1:
            options.append("Previous Page (p)")
        options += ["Return to Search (r)", "Quit (q)"]

        print("\nOptions:")
        for i, opt in enumerate(options):
            print(f"{i+1}. {opt}")
        
        choice = input("Enter your choice: ").strip().lower()

        if choice == 'n' and currentPage < totalPage:
            currentPage += 1
        elif choice == 'p' and currentPage > 1:
            currentPage -= 1
        elif choice == 'r':
            return 'return_to_search'
        elif choice == 'q':
            return 'quit'
        else:
            print("Invalid choice.")
    return 'return_to_search'

def phase2():
    print("\n--- Data Analysis ---")
    full_merged_data = prepareFullData(FILMDATA, GENRES_RAW)
    if not full_merged_data.empty:
        analyze_data(full_merged_data)
    else:
        print("Failed to prepare data for analysis.")
    print("Data analysis completed\n\n")

def phase3(merged_data):
    print("\n--- Recommendation ---")
    pageSize = 5
    
    while True:
        search_query = input("\nEnter a film title ('q' to quit): ").strip()
        if search_query.lower() == 'q':
            print("Bye!\n")
            break

        if not search_query:
            print("Not valid")
            continue

        currentPage = 1
        while True:
            search_results_df, total_search_results = search_films(merged_data, search_query, pageSize, currentPage)

            if search_results_df.empty:
                print(f"No films found matching '{search_query}'. Please try again.")
                break
            elif search_query=='':
                break

            totalPages = (total_search_results + pageSize - 1) // pageSize
            print(f"\nFound {total_search_results} matching films. Page {currentPage}/{totalPages}:")
            
            for idx, (_, row) in enumerate(search_results_df.iterrows(), start=1):
                genres_str = ', '.join(row['genres']) if row['genres'] else 'N/A'
                print(f"{idx}. {row['title']} ({row['release_year']}) - IMDb: {row['imdb_score']:.1f} - Genres: {genres_str}")
            
            options = ["Select a film (enter number)"]
            if currentPage < totalPages:
                options.append("Next Page (n)")
            if currentPage > 1:
                options.append("Previous Page (p)")
            options += ["New Search (r)", "Quit (q)"]

            print("\nOptions:")
            for i, opt in enumerate(options):
                print(f"{i+1}. {opt}")

            choice = input("Enter your choice: ").strip().lower()

            if choice.isdigit():
                selected_index = int(choice) - 1
                if 0 <= selected_index < len(search_results_df):
                    selected_film_row = search_results_df.iloc[selected_index]
                    filmID = selected_film_row['imdb_id']
                    filmTitle = selected_film_row['title']

                    displayInfo(selected_film_row)
                    while True:
                        recommend_choice = input("\nRecommendation for film? (yes/no): ").strip().lower()
                        if recommend_choice in ['y', 'yes']:
                            result = recommendHandler(merged_data, filmID, filmTitle)
                            if result == 'quit':
                                return
                            elif result == 'return_to_search':
                                search_query=''
                                break
                        elif recommend_choice in ['n', 'no']:
                            print("Returning to search...")
                            search_query=''
                            break
                        else:
                            print("Invalid choice. Please type yes or no.")
                else:
                    print("Invalid selection.")
            elif choice == 'n' and currentPage < totalPages:
                currentPage += 1
            elif choice == 'p' and currentPage > 1:
                currentPage -= 1
            elif choice == 'r':
                search_query=''
                break
            elif choice == 'q':
                print("Bye!\n")
                return
            else:
                print("Invalid input.")

if __name__ == "__main__":
    main()
