import os
import urllib.request
import xmltodict
import psycopg2
from selenium import webdriver
import time
import zipfile
import shutil

USER = 'postgres'
HOST = 'localhost'
PWD = '123456'
DB = "Clinical"
download_path = "C:\\Users\\deria\\Downloads"
data_dest = "C:\\Users\\deria\\Documents\\OSU\\Winter 2019\\CS 540\\Project\\cancer"
link = "https://clinicaltrials.gov/ct2/download_studies?term=cancer&down_chunk="

def check_directory(path):
    files = [f for f in os.listdir(path)]
    if files != []:
        shutil.rmtree(path)
        os.mkdir(path)


def download_source(link):
    try:
        check_directory(data_dest)
        driver = webdriver.Chrome("./chromedriver.exe")
        for i in range(1, 3):

            driver.get(link + str(i))
            time.sleep(3)
            downloads_checker()
            move_file(download_path+"\\search_result.zip", data_dest+"\\"+str(i)+".zip")
        driver.quit()

        unzip_file(data_dest)
    except Exception as e:
        print(e)
        driver.quit()

def unzip_file(file_path):
    list_of_file = [f for f in os.listdir(file_path) if f.endswith(".zip")]
    for zip_file in list_of_file:
        zip_ref = zipfile.ZipFile(file_path + "\\" + zip_file, 'r')
        zip_ref.extractall(file_path)
        #os.remove(file_path + "\\" + zip_file)
    zip_ref.close()

def move_file(src, dest):
    os.rename(src, dest)

def downloads_checker():
    """
    Check if webdriver is still downloading a file. sleep the system if it still does to avoid driver from quitting
    """
    stuff = [i for i in os.listdir(download_path) if i.endswith('.crdownload')]
    if stuff != []:
        time.sleep(3)
        downloads_checker()

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
        if count > 5:
            break
        try:
            key_list = []
            with open(path + file) as content:
                doc = xmltodict.parse(content.read())
                print(type(doc['clinical_study']['required_header']))
                #while True:

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
    download_source(link)
    path = '../cancer/'
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


    print("quit")