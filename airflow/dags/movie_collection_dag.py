from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import sys
import os

# Add src to Python path for importing our modules
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'src'))

from ingestion.tmdb_collector import TMDBCollector
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Default arguments for our DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def collect_tmdb_movies(**context):
    """Collect movie data from TMDB."""
    try:
        collector = TMDBCollector()
        df = collector.collect_and_transform(num_pages=5)
        
        # Save to CSV for loading into database
        output_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data',
            'tmdb_movies.csv'
        )
        collector.save_to_csv(df, output_path)
        
        # Push the file path to XCom for the next task
        context['task_instance'].xcom_push(key='csv_path', value=output_path)
        
    except Exception as e:
        logger.error(f"Error collecting TMDB movies: {str(e)}")
        raise

# Create DAG
dag = DAG(
    'movie_collection',
    default_args=default_args,
    description='Collect and process movie data from various sources',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['movies', 'data_collection'],
)

# Create data directory if it doesn't exist
create_data_dir = BashOperator(
    task_id='create_data_dir',
    bash_command='mkdir -p {{ dag_run.conf.base_path }}/data',
    dag=dag,
)

# Initialize database tables
init_db = PostgresOperator(
    task_id='init_db',
    postgres_conn_id='movie_db',
    sql="""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        overview TEXT,
        release_date DATE,
        vote_average FLOAT,
        vote_count INTEGER,
        popularity FLOAT,
        original_language VARCHAR(10),
        runtime INTEGER,
        budget BIGINT,
        revenue BIGINT,
        genres TEXT[],
        production_companies TEXT[],
        cast TEXT[],
        crew TEXT[],
        keywords TEXT[]
    );
    """,
    dag=dag,
)

# Collect TMDB movies
collect_movies = PythonOperator(
    task_id='collect_tmdb_movies',
    python_callable=collect_tmdb_movies,
    provide_context=True,
    dag=dag,
)

# Load data into PostgreSQL
load_to_db = PostgresOperator(
    task_id='load_to_db',
    postgres_conn_id='movie_db',
    sql="""
    COPY movies FROM '{{ task_instance.xcom_pull(task_ids='collect_tmdb_movies', key='csv_path') }}'
    DELIMITER ',' CSV HEADER;
    """,
    dag=dag,
)

# Define task dependencies
create_data_dir >> init_db >> collect_movies >> load_to_db
