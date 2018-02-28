import pandas as pd
from sqlalchemy import create_engine, text


def get_connection():
    """Returns a database engine to connect to postgres"""
    engine = create_engine("postgres://postgres@postgres_container:5432")
    return engine

def table_exists(t_name):
    """Check if a given table already exists in the database"""
    query = text('SELECT * FROM pg_catalog.pg_tables WHERE tablename=:table')
    return pd.read_sql(query, con=get_connection(), params={'table': t_name}).shape[0] > 0

def get_table(t_name):
    """Return the requested table as a pandas DataFrame"""
    if not table_exists(t_name):
        return None
    else:
        table = pd.read_sql("SELECT * FROM {table}".format(table=t_name), con=get_connection())
    return table

def write_table(dataframe, t_name, prefix="t_derived_"):
    """Write a dataframe to the database"""
    t_name_composed = prefix + t_name
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Must pass a DataFrame!")
    if table_exists(t_name_composed):
        raise ValueError("Table {} already exists".format(t_name_composed))
    else:
        dataframe.to_sql(t_name_composed, con=get_connection())
    return t_name_composed