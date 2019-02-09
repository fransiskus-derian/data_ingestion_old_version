import os
import urllib.request
import xmltodict
import psycopg2

USER = 'postgres'
HOST = 'localhost'
PWD = '123456'
DB = "Clinical"

def get_xml_files(path):
    """
    Read all the files in the given path and return a list of XML files
    """
    return [f for f in path if f.endswith('.xml')]

def construct_dictionary(xml_files):
    """
    This function reads xml files from a given path and constructs dictionary of all XML files
    that are retrieved from the ClinicalTrials.gov website, with file name / case number as keys.
    """
    data = {}
    count = 0
    for file in xml_files:
        count += 1
        if count > 1000:
            break
        try:
            with open(path + file) as content:
                doc = xmltodict.parse(content.read())
                #print(doc['clinical_study']['required_header']['url'])
                print(doc['clinical_study']['brief_title'])
                content.close()
        except:
            continue
    return data

def open_connection(host, db, user, password):
    """
    This function establish a connection to the local Post-GRE SQL db and return a cursor to execute queries
    :return: cursor
    """
    conn = psycopg2.connect(host=host, database=db, user=user, password=password)
    return conn.cursor()

def execute_query(cur_to_db, query):
    """
    This function use the ongoing connection to the database and execute given query in the parameter
    :param cur_to_db: On going connection
    :param query: SQL query to be submitted to our database
    :return: None
    """
    cur_to_db(query)


if __name__ == "__main__":
    path = '../clinical_file/'
    all_files_path = os.listdir(path)

    xml_files = get_xml_files(all_files_path)
    cases = construct_dictionary(xml_files)

    #cursor = open_connection(HOST, DB, USER, PWD)

    count = 0
    print(len(cases))
    for case in cases.keys():
        print(cases[case])
        count += 1
        if count == 5:
            break