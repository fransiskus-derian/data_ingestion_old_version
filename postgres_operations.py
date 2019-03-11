"""
Project Description:
"""
import psycopg2

# Connect to an existing database
def connect_database():
    conn = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="qw")
    return conn

# Open a cursor to perform database operations
def start_transaction(conn):
    cur = conn.cursor()
    return cur

# Create table function
def construct_table(cur):
    create_table_query ="""CREATE TABLE clinical_trial(
    nct_id text PRIMARY KEY,
    title text,
    description text,
    url text,
    country text[],
    source text,
    overall_status text,
    primary_purpose text,
    study_type text,
    allocation text,
    start_year integer,
    start_month text,
    completion_year integer,
    completion_month text,
    gender text,
    minimum_age text,
    maximum_age text,
    condition text[],
    healthy_volunteers text
    )"""
    cur.execute(create_table_query)

# Insert into table function
def insert_value(cur, table_name, attributes):
    if table_name == "clinical_trial":
        insert_query = """
        INSERT INTO clinical_trial 
        VALUES(%s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
        )"""
    else:
        pass
        
    cur.execute(insert_query,attributes)

#Delete table
def delete_table(cur,table):
    delete_query = "DROP TABLE " + table
    cur.execute(delete_query)

# Make the changes to the database persistent
def commit_transaction(conn):
    conn.commit()

#Undo changes of current transaction to the DB
def rollback_transaction(conn):
    conn.rollback()
    
# Close communication with the database (cursor & DB connection)
def end_transaction(cur,conn):
    cur.close()
    conn.close()
                                                                                                                conn.close()
