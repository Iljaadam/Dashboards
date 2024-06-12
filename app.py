import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# Connect to the database
engine = create_engine('sqlite:///imdb_sampled.db')

# Define functions to load data from the database
@st.cache_data
def load_data(query):
    with engine.connect() as connection:
        return pd.read_sql(query, connection)

# Function to split genres into separate entries
def split_genres(df):
    df = df.dropna(subset=['genres'])
    df['genres'] = df['genres'].apply(lambda x: x.split(','))
    df = df.explode('genres')
    return df

# Dashboard 1: Top Directors and Their Highest Rated Works
def top_directors_highest_rated():
    total_directors_query = '''
    SELECT COUNT(DISTINCT nc.nconst) as total_directors
    FROM name_basics nc
    JOIN title_crew tc ON nc.nconst = tc.directors
    '''
    total_directors = load_data(total_directors_query).iloc[0]['total_directors']
    
    films_range_query = '''
    SELECT MIN(film_count) as min_films, MAX(film_count) as max_films
    FROM (SELECT COUNT(tb.tconst) as film_count
          FROM name_basics nc
          JOIN title_crew tc ON nc.nconst = tc.directors
          JOIN title_basics tb ON tc.tconst = tb.tconst
          GROUP BY nc.nconst)
    '''
    films_range = load_data(films_range_query).iloc[0]
    
    num_to_show = st.sidebar.slider('Number of Directors to Show', min_value=5, max_value=50, value=10)
    
    query = f'''
    SELECT nc.primaryName as director, tb.primaryTitle, tr.averageRating, COUNT(tb.tconst) as film_count, AVG(tr.averageRating) as avg_rating
    FROM name_basics nc
    JOIN title_crew tc ON nc.nconst = tc.directors
    JOIN title_basics tb ON tc.tconst = tb.tconst
    JOIN title_ratings tr ON tb.tconst = tr.tconst
    GROUP BY nc.primaryName
    ORDER BY avg_rating DESC
    LIMIT {num_to_show}
    '''
    data = load_data(query)
    
    st.metric("Total Directors", total_directors)
    st.metric("Range of Films per Director", f"{films_range['min_films']} - {films_range['max_films']}")
    
    data = data.drop(columns=['averageRating'])  # Remove duplicate column
    
    fig1 = px.bar(data, x='director', y='avg_rating', color='primaryTitle', title='Top Directors and Their Highest Rated Works')
    st.plotly_chart(fig1)
    
    fig2 = px.scatter(data, x='director', y='film_count', size='avg_rating', color='avg_rating', title='Director Film Count vs. Average Rating')
    st.plotly_chart(fig2)
    
    st.dataframe(data)
    
    # Additional visualization
    fig3 = px.pie(data, values='film_count', names='director', title='Distribution of Films Among Top Directors')
    st.plotly_chart(fig3)
    
    fig4 = px.line(data, x='director', y='avg_rating', title='Average Rating of Top Directors')
    st.plotly_chart(fig4)

# Dashboard 2: Genre Popularity Over Time
def genre_popularity_over_time():
    genres_query = '''
    SELECT DISTINCT genres
    FROM title_basics
    WHERE genres IS NOT NULL
    '''
    genres = load_data(genres_query)
    genres = split_genres(genres)
    unique_genres = genres['genres'].unique().tolist()
    
    selected_genre = st.sidebar.selectbox('Select Genre', [""] + unique_genres, index=0)
    
    if selected_genre:
        query = f'''
        SELECT tb.startYear, tb.genres, COUNT(*) as count, AVG(tr.averageRating) as avg_rating
        FROM title_basics tb
        JOIN title_ratings tr ON tb.tconst = tr.tconst
        WHERE tb.genres LIKE "%{selected_genre}%" AND tb.startYear >= 1940 AND tb.startYear <= 2024
        GROUP BY tb.startYear, tb.genres
        ORDER BY tb.startYear
        '''
        data = load_data(query)
        
        st.metric("Total Movies", len(data))
        st.metric("Average Movies per Year", f"{data['count'].mean():.2f}")
        
        fig1 = px.line(data, x='startYear', y='count', title=f'Movies Released Over Time ({selected_genre})')
        st.plotly_chart(fig1)
        
        fig2 = px.bar(data, x='startYear', y='avg_rating', title=f'Average Ratings Over Time ({selected_genre})')
        st.plotly_chart(fig2)
        
        st.dataframe(data)
        
        # Additional visualization
        fig3 = px.pie(data, values='count', names='startYear', title=f'Distribution of Movies Over Time ({selected_genre})')
        st.plotly_chart(fig3)
        
        fig4 = px.scatter(data, x='startYear', y='avg_rating', size='count', title=f'Movies Count vs. Average Rating ({selected_genre})')
        st.plotly_chart(fig4)
    else:
        default_query = '''
        SELECT tb.startYear, tb.genres, COUNT(*) as count
        FROM title_basics tb
        WHERE tb.startYear >= 1940 AND tb.startYear <= 2024
        GROUP BY tb.startYear, tb.genres
        ORDER BY tb.startYear
        '''
        data = load_data(default_query)
        fig = px.line(data, x='startYear', y='count', color='genres', title='Genre Popularity Over Time')
        st.plotly_chart(fig)

# Dashboard 3: Breakdown of TV Series by Seasons and Episodes
def tv_series_breakdown():
    total_series_query = '''
    SELECT COUNT(DISTINCT te.parentTconst) as total_series
    FROM title_episodes te
    '''
    total_series = load_data(total_series_query).iloc[0]['total_series']
    
    num_to_show = st.sidebar.slider('Number of Series to Show', min_value=5, max_value=50, value=10)
    
    query = f'''
    SELECT te.parentTconst, tb.primaryTitle, COUNT(te.tconst) as episode_count, AVG(tr.averageRating) as avg_rating
    FROM title_episodes te
    JOIN title_basics tb ON te.parentTconst = tb.tconst
    JOIN title_ratings tr ON te.tconst = tr.tconst
    GROUP BY te.parentTconst, tb.primaryTitle
    ORDER BY episode_count DESC
    LIMIT {num_to_show}
    '''
    data = load_data(query)
    
    st.metric("Total TV Series", total_series)
    st.metric("Average Episodes per Series", f"{data['episode_count'].mean():.2f}")
    
    fig1 = px.bar(data, x='primaryTitle', y='episode_count', color='avg_rating', title='Breakdown of TV Series by Seasons and Episodes')
    st.plotly_chart(fig1)
    
    fig2 = px.scatter(data, x='primaryTitle', y='avg_rating', size='episode_count', color='avg_rating', title='TV Series Episode Count vs. Average Rating')
    st.plotly_chart(fig2)
    
    st.dataframe(data)
    
    # Additional visualization
    fig3 = px.pie(data, values='episode_count', names='primaryTitle', title='Distribution of Episodes Among Top TV Series')
    st.plotly_chart(fig3)
    
    fig4 = px.line(data, x='primaryTitle', y='avg_rating', title='Average Rating of Top TV Series')
    st.plotly_chart(fig4)

# Dashboard 4: Actors’ Career Trajectories
def actors_career_trajectories():
    total_actors_query = '''
    SELECT COUNT(DISTINCT np.nconst) as total_actors
    FROM name_basics np
    '''
    total_actors = load_data(total_actors_query).iloc[0]['total_actors']
    
    actors_query = '''
    SELECT np.primaryName, COUNT(tp.tconst) as movie_count, AVG(tr.averageRating) as avg_rating, MIN(tb.startYear) as first_film_year
    FROM name_basics np
    JOIN title_principals tp ON np.nconst = tp.nconst
    JOIN title_basics tb ON tp.tconst = tb.tconst
    JOIN title_ratings tr ON tb.tconst = tr.tconst
    WHERE tb.startYear IS NOT NULL
    GROUP BY np.primaryName
    ORDER BY movie_count DESC
    LIMIT 100
    '''
    actors_data = load_data(actors_query)
    actors = actors_data['primaryName'].tolist()
    selected_actor = st.sidebar.selectbox('Select an Actor', actors)
    
    query = f'''
    SELECT np.primaryName as actor, tb.startYear, COUNT(*) as movie_count, AVG(tr.averageRating) as avg_rating, MIN(tb.startYear) OVER (PARTITION BY np.primaryName) as first_film_year
    FROM name_basics np
    JOIN title_principals tp ON np.nconst = tp.nconst
    JOIN title_basics tb ON tp.tconst = tb.tconst
    JOIN title_ratings tr ON tb.tconst = tr.tconst
    WHERE np.primaryName = "{selected_actor}" AND tb.startYear IS NOT NULL
    GROUP BY np.primaryName, tb.startYear
    ORDER BY tb.startYear
    '''
    data = load_data(query)

    if data.empty:
        st.write(f"No data available for {selected_actor}")
    else:
        st.metric("Total Actors", total_actors)
        
        # Calculate overall average films per actor from the top 100 actors
        avg_films_per_actor = actors_data['movie_count'].mean()
        st.metric("Average Films per Actor", f"{avg_films_per_actor:.2f}")
        
        # Calculate average films per year
        first_film_year = data['first_film_year'].iloc[0]
        total_films = data['movie_count'].sum()
        avg_films_per_year = total_films / (2024 - first_film_year)
        
        st.metric("Average Films per Year", f"{avg_films_per_year:.2f}")
        
        # Remove the first_film_year column from DataFrame display
        data = data.drop(columns=['first_film_year'])
        
        fig1 = px.scatter(data, x='startYear', y='avg_rating', size='movie_count', color='avg_rating', title=f'{selected_actor} Career Trajectories')
        st.plotly_chart(fig1)
        
        st.dataframe(data)
        
        # Additional visualization
        fig2 = px.bar(data, x='startYear', y='avg_rating', color='movie_count', title=f'{selected_actor} Film Ratings Over Time')
        st.plotly_chart(fig2)
        
        fig3 = px.pie(data, values='movie_count', names='startYear', title=f'{selected_actor} Film Distribution Over Years')
        st.plotly_chart(fig3)


# Dashboard 5: International Film Insights
def international_film_insights():
    total_regions_query = '''
    SELECT COUNT(DISTINCT ta.region) as total_regions
    FROM title_akas ta
    '''
    total_regions = load_data(total_regions_query).iloc[0]['total_regions']
    
    num_to_show = st.sidebar.slider('Number of Regions to Show', min_value=5, max_value=50, value=10)
    
    query = f'''
    SELECT ta.region, tb.primaryTitle, tr.averageRating
    FROM title_akas ta
    JOIN title_basics tb ON ta.titleId = tb.tconst
    JOIN title_ratings tr ON tb.tconst = tr.tconst
    WHERE ta.region IS NOT NULL AND tb.primaryTitle NOT LIKE 'Episode%'
    ORDER BY tr.averageRating DESC
    LIMIT {num_to_show}
    '''
    data = load_data(query)
    
    st.metric("Total Regions", total_regions)
    st.metric("Average Rating", f"{data['averageRating'].mean():.2f}")
    
    fig1 = px.bar(data, x='region', y='averageRating', color='primaryTitle', title='International Film Insights')
    st.plotly_chart(fig1)
    
    fig2 = px.scatter(data, x='region', y='averageRating', size='averageRating', color='primaryTitle', title='Film Ratings by Region')
    st.plotly_chart(fig2)
    
    st.dataframe(data)
    
    # Additional visualization
    fig3 = px.pie(data, values='averageRating', names='region', title='Average Rating Distribution by Region')
    st.plotly_chart(fig3)


# Streamlit app layout
def main():
    st.title("IMDb Data Analysis Dashboard")
    st.markdown("### Explore movie statistics and insights")

    st.sidebar.title("Dashboard Selection")
    dashboard = st.sidebar.selectbox("Select a Dashboard", 
                                     ('Top Directors and Their Highest Rated Works', 
                                      'Genre Popularity Over Time', 
                                      'Breakdown of TV Series by Seasons and Episodes', 
                                      'Actors’ Career Trajectories', 
                                      'International Film Insights'))

    if dashboard == 'Top Directors and Their Highest Rated Works':
        top_directors_highest_rated()
    elif dashboard == 'Genre Popularity Over Time':
        genre_popularity_over_time()
    elif dashboard == 'Breakdown of TV Series by Seasons and Episodes':
        tv_series_breakdown()
    elif dashboard == 'Actors’ Career Trajectories':
        actors_career_trajectories()
    elif dashboard == 'International Film Insights':
        international_film_insights()

if __name__ == "__main__":
    main()
