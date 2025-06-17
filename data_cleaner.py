import pandas as pd
import os

def genreFilter(genreRaw, filmData, genreFiltered):
    print(f"Loading {filmData}")
    df_filmData = pd.read_csv(filmData)
    imdbIDs = set(df_filmData['imdb_id'].dropna().unique())
    print(f"Extracted {len(imdbIDs)} unique IMDb IDs\n")

    print(f"Pre-cleaning and filtering {genreRaw}")
    try:
        with open(genreRaw, 'r', encoding='utf-8') as infile, \
             open(genreFiltered, 'w', encoding='utf-8') as outfile:
            
            header = infile.readline().strip().split('\t')
            try:
                tconst_idx = header.index('tconst')
                genres_idx = header.index('genres')
            except ValueError as e:
                #Không tìm thấy cột 'tconst' hoặc 'genres'
                print(f"Error: Missing expected column in {genreRaw} header: {e}")
                return False

            outfile.write(f"{header[tconst_idx]}\t{header[genres_idx]}\n")

            for line_num, line in enumerate(infile, start=2):
                parts = line.strip().split('\t')
                if len(parts) > max(tconst_idx, genres_idx):
                    tconst = parts[tconst_idx]
                    genres = parts[genres_idx]
                    
                    if tconst in imdbIDs:
                        outfile.write(f"{tconst}\t{genres}\n")
                else:
                    # Dòng không hợp lệ, báo rồi bỏ qua
                    print(f"Warning: Skipping malformed line {line_num} in {genreRaw}: {line.strip()}")
        print(f"Filtered genres saved to {genreFiltered}\n")
        return True
    
    except FileNotFoundError:
        print(f"\nError: File not found at {genreRaw}\n")
        return False
    
    except Exception as e:
        print(f"\nAn unexpected error occurred during file processing: {e}\n")
        return False

def merge_data(filmData, genreFiltered):
    print(f"Loading {filmData}")
    df_filmData = pd.read_csv(filmData)

    '''
    Sample of prepared data:
   index        id           title   type  ...    imdb_id  imdb_score imdb_votes            genres
0      0   tm84618     Taxi Driver  MOVIE  ...  tt0075314         8.3   795222.0    [Crime, Drama]

---> Remove 'index' col
    '''
    if 'index' in df_filmData.columns:
        df_filmData = df_filmData.drop(columns=['index'])


    print(f"Loading {genreFiltered}...\n")
    df_genres = pd.read_csv(genreFiltered, sep='\t')

    print("Merging")
    df_genres.rename(columns={'tconst': 'imdb_id'}, inplace=True)
    merged_df = pd.merge(df_filmData, df_genres, on='imdb_id', how='inner')
    print("Merged\n")

    print("Cleaning genres column")
    merged_df['genres'] = merged_df['genres'].apply(
        lambda x: [g.strip() for g in str(x).split(',') if g.strip() != '\\N'] if pd.notna(x) else []
    )
    print("Cleaned\n")
    
    return merged_df

# Merge full instead (For phase 2))
def prepareFullData(filmData, genreRaw):
    os.system('cls' if os.name == 'nt' else 'clear')

    df_filmData = pd.read_csv(filmData)
    df_genreRaw = pd.read_csv(genreRaw, sep='\t')

    # Rename
    df_genreRaw.rename(columns={'tconst': 'imdb_id'}, inplace=True)

    print("Merging")
    merged_df = pd.merge(df_filmData, df_genreRaw, on='imdb_id', how='inner')
    print(f"Merge complete. Shape: {merged_df.shape}")

    # Handle duplicates
    initial_rows = len(merged_df)
    merged_df.drop_duplicates(subset='imdb_id', inplace=True)
    print(f"Removed {initial_rows - len(merged_df)} duplicate IDs. New shape: {merged_df.shape}")

    # Basic cleaning
    merged_df['imdb_score'] = pd.to_numeric(merged_df['imdb_score'], errors='coerce')
    merged_df['imdb_votes'] = pd.to_numeric(merged_df['imdb_votes'], errors='coerce')
    merged_df['release_year'] = pd.to_numeric(merged_df['release_year'], errors='coerce')
    merged_df['runtimeMinutes'] = pd.to_numeric(merged_df['runtimeMinutes'], errors='coerce')

    # Drop rows with NaN
    critical_columns = ['imdb_id', 'title', 'imdb_score', 'imdb_votes', 'release_year', 'genres']
    initial_rows_after_dedup = len(merged_df)
    merged_df.dropna(subset=critical_columns, inplace=True)
    print(f"Removed {initial_rows_after_dedup - len(merged_df)} rows with missing critical data. New shape: {merged_df.shape}")

    # Clean genre
    merged_df['genres'] = merged_df['genres'].apply(
        lambda x: [g.strip() for g in str(x).split(',') if g.strip() != '\\N'] if pd.notna(x) else []
    )
    print("Genres column cleaned")
    print("Full data preparation done\n")

    return merged_df