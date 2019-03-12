"""
Project Description:
"""
import psycopg2

def get_details():
    with open("data.txt", 'r') as r1:
        host = r1.readline().split("=")[1].strip()
        db = r1.readline().split("=")[1].strip()
        user = r1.readline().split("=")[1].strip()
        pwd = r1.readline().split("=")[1].strip()
        r1.close()
    return (host, db, user, pwd)

# Connect to an existing database
def connect_database():
    details = get_details()
    conn = psycopg2.connect(host=details[0], database=details[1], user=details[2], password=details[3])
    return conn

# Open a cursor to perform database operations
def start_transaction(conn):
    cur = conn.cursor()
    return cur

# Create table function
def construct_case_table(cur):
    drop_table_query ="""DROP TABLE IF EXISTS clinical_trial"""
    
    cur.execute(drop_table_query)
    
    create_table_query ="""CREATE TABLE clinical_trial(
    nct_id text PRIMARY KEY,
    title text,
    description text,
    url text,
    keyword text,
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
