import pandas as pd
from sqlalchemy import create_engine
import random

# Function to load and sample the IMDb datasets
def load_and_sample_tsv(file_name, sample_fraction=0.1):
    df = pd.read_csv(file_name, sep='\t', na_values='\\N')
    df_sampled = df.sample(frac=sample_fraction, random_state=42)
    return df_sampled

# Load and sample the IMDb datasets
akas = load_and_sample_tsv('data/title.akas.tsv.gz', sample_fraction=0.1)
basics = load_and_sample_tsv('data/title.basics.tsv.gz', sample_fraction=0.1)
crew = load_and_sample_tsv('data/title.crew.tsv.gz', sample_fraction=0.1)
episodes = load_and_sample_tsv('data/title.episode.tsv.gz', sample_fraction=0.1)
principals = load_and_sample_tsv('data/title.principals.tsv.gz', sample_fraction=0.1)
ratings = load_and_sample_tsv('data/title.ratings.tsv.gz', sample_fraction=0.1)
names = load_and_sample_tsv('data/name.basics.tsv.gz', sample_fraction=0.1)

# Data Cleaning
def clean_data(df):
    df.fillna(value=pd.NA, inplace=True)
    return df

akas = clean_data(akas)
basics = clean_data(basics)
crew = clean_data(crew)
episodes = clean_data(episodes)
principals = clean_data(principals)
ratings = clean_data(ratings)
names = clean_data(names)

# Save cleaned data to SQL database
engine = create_engine('sqlite:///imdb_sampled.db')

akas.to_sql('title_akas', engine, index=False, if_exists='replace')
basics.to_sql('title_basics', engine, index=False, if_exists='replace')
crew.to_sql('title_crew', engine, index=False, if_exists='replace')
episodes.to_sql('title_episodes', engine, index=False, if_exists='replace')
principals.to_sql('title_principals', engine, index=False, if_exists='replace')
ratings.to_sql('title_ratings', engine, index=False, if_exists='replace')
names.to_sql('name_basics', engine, index=False, if_exists='replace')

from sqlalchemy import Table, Column, Integer, String, ForeignKey, Boolean, MetaData

metadata = MetaData()

title_akas = Table('title_akas', metadata,
                   Column('titleId', String, primary_key=True),
                   Column('ordering', Integer),
                   Column('title', String),
                   Column('region', String),
                   Column('language', String),
                   Column('types', String),
                   Column('attributes', String),
                   Column('isOriginalTitle', Boolean)
                   )

title_basics = Table('title_basics', metadata,
                     Column('tconst', String, primary_key=True),
                     Column('titleType', String),
                     Column('primaryTitle', String),
                     Column('originalTitle', String),
                     Column('isAdult', Boolean),
                     Column('startYear', Integer),
                     Column('endYear', Integer),
                     Column('runtimeMinutes', Integer),
                     Column('genres', String)
                     )

title_crew = Table('title_crew', metadata,
                   Column('tconst', String, ForeignKey('title_basics.tconst')),
                   Column('directors', String),
                   Column('writers', String)
                   )

title_episodes = Table('title_episodes', metadata,
                       Column('tconst', String, ForeignKey('title_basics.tconst')),
                       Column('parentTconst', String, ForeignKey('title_basics.tconst')),
                       Column('seasonNumber', Integer),
                       Column('episodeNumber', Integer)
                       )

title_principals = Table('title_principals', metadata,
                         Column('tconst', String, ForeignKey('title_basics.tconst')),
                         Column('ordering', Integer),
                         Column('nconst', String, ForeignKey('name_basics.nconst')),
                         Column('category', String),
                         Column('job', String),
                         Column('characters', String)
                         )

title_ratings = Table('title_ratings', metadata,
                      Column('tconst', String, ForeignKey('title_basics.tconst')),
                      Column('averageRating', Integer),
                      Column('numVotes', Integer)
                      )

name_basics = Table('name_basics', metadata,
                    Column('nconst', String, primary_key=True),
                    Column('primaryName', String),
                    Column('birthYear', Integer),
                    Column('deathYear', Integer),
                    Column('primaryProfession', String),
                    Column('knownForTitles', String)
                    )

metadata.create_all(engine)
