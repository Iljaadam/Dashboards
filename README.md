# IMDb Data Analysis Dashboard

This project is a data analysis dashboard built using Streamlit that explores various insights from the IMDb dataset. The dashboard includes multiple sections focusing on different aspects of the data such as top directors, genre popularity, TV series breakdown, actor career trajectories, and international film insights.

## Features

- **Top Directors and Their Highest Rated Works**: Showcases the most prolific directors and their highest-rated works.
- **Genre Popularity Over Time**: Tracks the popularity of different genres over the years.
- **Breakdown of TV Series by Seasons and Episodes**: Provides insights into TV series, showing the number of seasons and episodes per series.
- **Actors’ Career Trajectories**: Maps out the career trajectories of actors, showing the number of films/TV shows per year and average ratings.
- **International Film Insights**: Explores the performance and reach of films across different regions and languages.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/Iljaadam/dashboards.git
    cd imdb-dashboard
    ```

2. **Create and activate a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Dashboard

1. **Ensure the SQLite database is present:**
    - The dashboard relies on an SQLite database named `imdb_sampled.db`. Ensure this database file is in the root directory of your project.

2. **Start the Streamlit app:**
    ```bash
    streamlit run app.py
    ```

3. **Access the dashboard:**
    - Open your web browser and navigate to `http://localhost:8501`.

## Usage

Once the dashboard is running, you can interact with the various sections via the sidebar to explore different aspects of the IMDb dataset. Use the dropdowns and sliders to filter and customize the views to gain insights into movie statistics.

## Data Sources

- **IMDb Dataset**: The dataset used in this project includes various files such as `title.akas.tsv.gz`, `title.basics.tsv.gz`, `title.crew.tsv.gz`, `title.episode.tsv.gz`, `title.principals.tsv.gz`, `title.ratings.tsv.gz`, and `name.basics.tsv.gz`.

Link: https://datasets.imdbws.com/

## Create the imdb_sampled.db file
Please use the data process script(make sure to create a data/* repository with the archives)
