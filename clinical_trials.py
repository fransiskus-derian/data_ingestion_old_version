import os
import urllib.request
import xmltodict
import psycopg2
from selenium import webdriver
import time
import zipfile
import shutil
import collections


##GLOBAL VARIABLES##
USER = 'postgres'
HOST = 'localhost'
PWD = '123456'
DB = "Clinical"
download_path = "C:\\Users\\deria\\Downloads"
data_dest = "C:\\Users\\deria\\Documents\\OSU\\Winter 2019\\CS 540\\Project\\cancer"
link = "https://clinicaltrials.gov/ct2/download_studies?term=cancer&down_chunk="
ordereddict = collections.OrderedDict()

def check_directory(path):
    """
    check if the given path contains any files, if it does, remove the directory and create new one (to remove duplicate when downloading)
    :param path: the source path to check if there exist files in the directory
    :return: None
    """
    files = [f for f in os.listdir(path)]
    if files != []:
        shutil.rmtree(path)
        os.mkdir(path)


def download_source(link):
    """
    call check directory to clean and create directory.
    Use selenium webdriver to download all the files from the online source and unzip the files to a specific directory
    :param link: link to the online data source
    :return:
    """
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
    """
    Unzip all zip files in the given directory
    :param file_path: path to unzip
    :return: None
    """
    list_of_file = [f for f in os.listdir(file_path) if f.endswith(".zip")]
    for zip_file in list_of_file:
        zip_ref = zipfile.ZipFile(file_path + "\\" + zip_file, 'r')
        zip_ref.extractall(file_path)
        #os.remove(file_path + "\\" + zip_file)
    zip_ref.close()

def move_file(src, dest):
    """
    move and rename file from one directory to another directory
    """
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

def integrate_data(xml_files, path):
    """
    """
    count = 0

    nct_id_not_found = 0
    title_not_found = 0
    summary_not_found = 0
    status_not_found = 0
    study_type_not_found = 0
    url_not_found = 0
    gender_not_found = 0
    min_age_not_found = 0
    max_age_not_found = 0
    healthy_volunteers_not_found = 0
    allocation_not_found = 0
    purpose_not_found = 0
    country_not_found = 0
    start_date_not_found = 0
    completion_date_not_found = 0
    condition_not_found = 0
    source_not_found = 0

    while(count < 100):

        try:
            with open(path + xml_files[count], 'rb') as c:
                doc = xmltodict.parse(c.read())

                try:
                    nct_id = doc['clinical_study']['id_info']['nct_id']
                except Exception as e:
                    nct_id = None
                    nct_id_not_found +=1
                    #print(e)
                try:
                    title = doc['clinical_study']['brief_title']
                except Exception as e:
                    title = None
                    title_not_found +=1
                    #print(e)
                try:
                    summary = doc['clinical_study']['brief_summary']['textblock']
                except Exception as e:
                    summary = None
                    summary_not_found +=1
                    #print(e)
                try:
                    status = doc['clinical_study']['overall_status'].upper()
                    #unknown status
                except Exception as e:
                    status = 'UNKNOWN STATUS'
                    status_not_found += 1
                    #print(e)

                try:
                    study_type = doc['clinical_study']['study_type']
                except Exception as e:
                    study_type = None
                    study_type_not_found += 1
                    #print(e)

                try:
                    url = doc['clinical_study']['required_header']['url']
                except Exception as e:
                    url = "https://clinicaltrials.gov/ct2/show/" + nct_id
                    url_not_found += 1
                    #print(e)

                try:
                    gender = doc['clinical_study']['eligibility']['gender']
                except Exception as e:
                    gender = None
                    gender_not_found +=1
                    #print(e)

                try:
                    min_age = doc['clinical_study']['eligibility']['minimum_age']
                except Exception as e:
                    min_age = "N/A"
                    min_age_not_found +=1
                    #print(e)

                try:
                    max_age = doc['clinical_study']['eligibility']['maximum_age']
                except Exception as e:
                    max_age = "N/A"
                    max_age_not_found +=1
                    #print(e)

                try:
                    healthy_volunteers = doc['clinical_study']['eligibility']['healthy_volunteers']
                except Exception as e:
                    healthy_volunteers = None
                    healthy_volunteers_not_found += 1
                    #print(e)

                try:
                    allocation = doc['clinical_study']['study_design_info']['allocation']
                except Exception as e:
                    allocation = None
                    allocation_not_found += 1
                    #print(e)

                try:
                    purpose = doc['clinical_study']['study_design_info']['primary_purpose']
                except Exception as e:
                    purpose = None
                    purpose_not_found += 1
                    #print(e)

                try:
                    country_temp = []
                    if type(doc['clinical_study']['location_countries']['country']) == type([]):
                        country_temp.extend(doc['clinical_study']['location_countries']['country'])
                    else:
                        country_temp.append(doc['clinical_study']['location_countries']['country'])
                    country = str(set(country_temp))
                except Exception as e:
                    country = str(set())
                    country_not_found += 1
                    #print(e)

                try:
                    # may contain: OrderedDict([('@type', 'Actual'), ('#text', 'January 17, 1996')]) OR ('January 17, 1996') OR (January 1996)
                    #print(doc['clinical_study']['start_date'])

                    if type(doc['clinical_study']['start_date']) == type(ordereddict):
                        start_month = doc['clinical_study']['start_date']['#text'].split()[0]
                        start_year = doc['clinical_study']['start_date']['#text'].split()[-1]
                    else:
                        start_month = doc['clinical_study']['start_date'].split()[0]
                        start_year = doc['clinical_study']['start_date'].split()[-1]
                except Exception as e:
                    start_month = None
                    start_year = None
                    start_date_not_found += 1
                    #print(e)

                try:
                    # may contain: OrderedDict([('@type', 'Actual'), ('#text', 'January 17, 1996')]) OR ('January 17, 1996') OR (January 1996)
                    # print(doc['clinical_study']['start_date'])

                    if type(doc['clinical_study']['completion_date']) == type(ordereddict):
                        completion_month = doc['clinical_study']['completion_date']['#text'].split()[0]
                        completion_year = doc['clinical_study']['completion_date']['#text'].split()[-1]
                    else:
                        completion_month = doc['clinical_study']['completion_date'].split()[0]
                        completion_year = doc['clinical_study']['completion_date'].split()[-1]
                except Exception as e:
                    completion_month = None
                    completion_year = None
                    completion_date_not_found += 1
                    #print(e)

                try:
                    condition_temp = []
                    #print(doc['clinical_study']['condition'])
                    if type(doc['clinical_study']['condition']) == type([]):
                        condition_temp.extend(doc['clinical_study']['condition'])
                    else:
                        condition_temp.append(doc['clinical_study']['condition'])
                    condition = str(set(condition_temp))
                except Exception as e:
                    condition = str(set())
                    condition_not_found += 1
                    #print(e)

                try:
                    source = doc['clinical_study']['source']
                except Exception as e:
                    source = None
                    source_not_found += 1
                    #print(e)
                c.close()
            count += 1
        except Exception as e:

            print(e)
    print(nct_id_not_found)
    print(title_not_found)
    print(summary_not_found)
    print(status_not_found)
    print(study_type_not_found)
    print(url_not_found)
    print(gender_not_found)
    print(min_age_not_found)
    print(max_age_not_found)
    print(healthy_volunteers_not_found)
    print(allocation_not_found)
    print(purpose_not_found)
    print(country_not_found)
    print(start_date_not_found)
    print(completion_date_not_found)
    print(condition_not_found)
    print(source_not_found)

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
    #download_source(link)
    path = '../cancer/'
    all_files_path = os.listdir(path)
    xml_files = get_xml_files(all_files_path)
    integrate_data(xml_files, path)

    #cursor = open_connection(HOST, DB, USER, PWD)

