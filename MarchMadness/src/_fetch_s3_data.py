import os
from pathlib import Path
from tempfile import TemporaryDirectory
os.chdir("/home/jovyan/work")

import boto3
import inflection
import pandas as pd
import sqlalchemy


def fetch_data():
    """Fetch Data from S3 and put it into the database"""
    print("\n" + "/"*111)
    print("/" + " "*44 + "DOWNLOAD DATA FROM S3" + " "*44 + "/")
    print("/"*111 + "\n\n")
    # get S3 Connection
    s3 = boto3.resource("s3", 
                        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
                       )

    # get postgres connection
    engine = sqlalchemy.create_engine("postgresql://postgres@postgres_container:5432")

    # query template 
    query = sqlalchemy.text('SELECT * FROM pg_catalog.pg_tables WHERE tablename=:table')

    with TemporaryDirectory() as tdir:    
        for obj in s3.Bucket("jgoerner-kaggle").objects.all():
            # skip tables with leading underscore
            name=obj.key
            if name.startswith("_"):
                continue

            # start log
            print("#"*(len(name)+15))
            print("# Processing {} #".format(name))
            print("#"*(len(name)+15))

            # skip if table already exists
            t_name = "t_original_{}".format(inflection.underscore(name.replace(".csv", "")))
            tbl_already_exists = pd.read_sql(query, con=engine, params={'table': t_name}).shape[0]
            if tbl_already_exists:
                print("Table '{}' already exists".format(name))
                print("Skipping\n")
                continue

            # download file to temporary dir
            path = Path(tdir, name)
            print("Downloading")
            s3.Bucket("jgoerner-kaggle").download_file(name, str(path))
            print("Ingesting\n")
            df = pd.read_csv(path)

            # serialize dataframe to database
            # TODO: lower column name
            df.to_sql(t_name, con=engine, if_exists="fail")


if __name__ == "__main__":
    fetch_data()