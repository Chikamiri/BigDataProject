import os
from flask import Flask, render_template, send_from_directory, request
import sys
import subprocess

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from main import phase2, get_merged_data, search_films, recommend

app = Flask(__name__)

IMAGE_DIR = 'img'
MERGED_DATA = None

if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    with app.app_context():
        MERGED_DATA = get_merged_data()
        if MERGED_DATA.empty:
            print("Warning: Merged data is empty. Recommendation features may not work.")

@app.route('/')
def index():
    print(f"Current working directory: {os.getcwd()}")
    print(f"Attempting to list files in: {os.path.abspath(IMAGE_DIR)}")
    try:
        image_files = [f for f in os.listdir(IMAGE_DIR) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        print(f"Found image files: {image_files}")
        return render_template('index.html', image_files=image_files)
    except FileNotFoundError:
        print(f"Image directory '{IMAGE_DIR}' not found.")
        return "Image directory not found", 404
    except Exception as e:
        print(f"An error occurred while listing images: {e}")
        return "An error occurred while listing images.", 500

@app.route('/image/<filename>')
def display_image(filename):
    return send_from_directory(IMAGE_DIR, filename)

@app.route('/generate_and_show')
def generate_and_show():
    try:
        phase2()
        print("main.py's main() function executed successfully, images should be generated.")
    except subprocess.CalledProcessError as e:
        print(f"Error running main.py: {e}")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return f"Error generating images: {e.stderr}", 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}", 500

    return "Images generated. Please go to the <a href='/'>homepage</a> to view them.", 200

@app.route('/search', methods=['GET', 'POST'])
def search():
    films = []
    query = ""
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            search_results_df, _ = search_films(MERGED_DATA, query, page_size=10, page_number=1)
            films = search_results_df.to_dict(orient='records')
    return render_template('search.html', films=films, query=query)

@app.route('/film/<imdb_id>')
def film_details(imdb_id):
    if MERGED_DATA is None or MERGED_DATA.empty:
        return "Data not loaded.", 500

    selected_film_row = MERGED_DATA[MERGED_DATA['imdb_id'] == imdb_id]
    if selected_film_row.empty:
        return "Film not found.", 404

    film = selected_film_row.iloc[0].to_dict()
    
    recommendations_df, _ = recommend(MERGED_DATA, imdb_id, page_size=5, page_number=1)
    recommendations = recommendations_df.to_dict(orient='records')

    return render_template('film_details.html', film=film, recommendations=recommendations)

@app.route('/recommend/<imdb_id>/<int:page>')
def get_recommendations_paginated(imdb_id, page):
    if MERGED_DATA is None or MERGED_DATA.empty:
        return "Data not loaded.", 500

    recommendations_df, total_recommendations = recommend(MERGED_DATA, imdb_id, page_size=5, page_number=page)
    recommendations = recommendations_df.to_dict(orient='records')
    total_pages = (total_recommendations + 5 - 1) // 5

    return render_template('recommendations_partial.html', recommendations=recommendations, imdb_id=imdb_id, current_page=page, total_pages=total_pages)


if __name__ == '__main__':
    os.makedirs(IMAGE_DIR, exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
