import os
import xmltodict
from selenium import webdriver
import time
import zipfile
import shutil
import collections
import matplotlib.pyplot as plt
import pandas as pd

import postgres_operations as po

##GLOBAL VARIABLES##
download_path = ""
data_dest = '../cancer/'
link = "https://clinicaltrials.gov/ct2/download_studies?term=cancer&down_chunk="
ordereddict = collections.OrderedDict()

age_group_query = """
            with age_groups as (
                SELECT 
                    CASE 
                        WHEN min_age_in_weeks/52 <= 10 THEN '0-10'
                        WHEN min_age_in_weeks/52 <= 20 THEN '11-20'
                        WHEN min_age_in_weeks/52 <= 30 THEN '21-30'
                        WHEN min_age_in_weeks/52 <= 40 THEN '31-40'
                        WHEN min_age_in_weeks/52 <= 50 THEN '41-50'
                        WHEN min_age_in_weeks/52 <= 60 THEN '51-60'
                        WHEN min_age_in_weeks/52 > 60 THEN '61 ++'
                    END age_group,
                    COUNT(nct_id) total_per_age_group
                FROM 
                    (SELECT 
                            nct_id,
                            CASE 
                                WHEN LOWER(num_type) IN ('year', 'years') THEN num*52
                                WHEN LOWER(num_type) IN ('month', 'months') THEN num*4
                                ELSE num
                            END min_age_in_weeks
                        FROM 
                            (SELECT
                                nct_id,
                                CAST(split_part(minimum_age, ' ', 1) AS INT) num,
                                split_part(minimum_age, ' ', 2) num_type
                            FROM 
                                clinical_trial
                            WHERE 
                                minimum_age != 'N/A' and keyword = 'Cancer'
                            ) t
                         ) t1
                GROUP BY 1
                ORDER BY 1
                ), total as (
                SELECT 
                    SUM(total_per_age_group) total_case 
                FROM 
                    age_groups )

            SELECT 
                age_group, ROUND((total_per_age_group/total_case)*100, 1) percentage_of_case
            FROM 
                age_groups, total

            """

def make_directory(path):
    """
    Create a directory based on given path (Firstly remove the directory if it already exists)
    :param path: the source path to check if there exist files in the directory
    :return: None
    """
    try:
        shutil.rmtree(path)
        os.mkdir(path)
    except Exception as e:
        os.mkdir(path)



def download_source(link):
    """
    call check directory to clean and create directory.
    Use selenium webdriver to download all the files from the online source and unzip the files to a specific directory
    :param link: link to the online data source
    :return:
    """
    try:
        make_directory(data_dest)
        driver = webdriver.Chrome("./chromedriver.exe")
        for i in range(10, 11):

            driver.get(link + str(i))
            time.sleep(3)
            downloads_checker()
            move_file(download_path+"/search_result.zip", data_dest+"/"+str(i)+".zip")
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

def integrate_case_data(xml_files, path, cur, keyword, total_xml):
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

    while(count < total_xml):

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
                    country = '{}'
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
                    condition = str(set(condition_temp)).replace("\"", "\'")
                    #print(set(condition_temp))
                except Exception as e:

                    condition = '{}'
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
        try:
            if start_year != None:
                start_year = int(start_year)

            if completion_year != None:
                completion_year = int(completion_year)

            attributes = (nct_id, title, summary, url, keyword, country, source, status, purpose, study_type, allocation,
                          start_year, start_month, completion_year, completion_month, gender, min_age, max_age,
                          condition, healthy_volunteers)
            po.insert_value(cur, "clinical_trial", attributes)
        except Exception as e:
            print("INSERTION FAILURE")
            print(e)
            #print(nct_id)
            print(attributes)
            break

    #KEY FINDING RESULTS#
    print("total NCT_ID not found: " + str(nct_id_not_found))
    print("total TITLE not found: " + str(title_not_found))
    print("total DESCRIPTION not found: " + str(summary_not_found))
    print("total CASE STATUS not found: " + str(status_not_found))
    print("total STUDY TYPE not found: " + str(study_type_not_found))
    print("total URL not found: " + str(url_not_found))
    print("total GENDER not found: " + str(gender_not_found))
    print("total MIN_AGE not found: " + str(min_age_not_found))
    print("total MAX_AGE not found: " + str(max_age_not_found))
    print("total HEALTHY VOLUNTEERS not found: " + str(healthy_volunteers_not_found))
    print("total ALLOCATION not found: " + str(allocation_not_found))
    print("total PURPOSE not found: " + str(purpose_not_found))
    print("total COUNTRY not found: " + str(country_not_found))
    print("total START DATE not found: " + str(start_date_not_found))
    print("total COMPLETION DATE not found: " + str(completion_date_not_found))
    print("total CONDITION not found: " + str(condition_not_found))
    print("total SOURCE not found: " + str(source_not_found))

def plot_analysis(query, conn, x_axis, y_axis, plot_title):
    """
    Retrieve results from from PostgreSQL server based on the given query and plot the result into a horizontal bar graph
    according to the given x-axis, y-axis, and title plot
    :param query: SQL Query to retrieve results from SQL Server
    :param conn: Connection to the DB
    :param x_axis: table attribute name to be used as the x-axis of the plot
    :param y_axis: table attribute name to be used as the y-axis of the plot
    :param plot_title: title to be used for the plot
    :return: None
    """
    df = pd.read_sql_query(query, conn)
    df.plot.barh(x=x_axis, y=y_axis, title=plot_title)
    plt.show()

if __name__ == "__main__":
    try:
        #DOWNLOAD DATA FROM THE WEBSITE
        download_source(link)
        path = data_dest
        keywords = ["Cancer"]
        all_files_path = os.listdir(path)
        xml_files = get_xml_files(all_files_path)
        length_of_files = len(xml_files)
        #connect to database

        conn = po.connect_database()
        # construct relation
        po.construct_case_table(cur)

        # commit changes to DB
        po.commit_transaction(conn)

        cur = po.start_transaction(conn)

        #integrate case data to the DB
        for keyword in keywords:
            integrate_case_data(xml_files, path, cur, keyword, 1000)

        #commit data integration
        po.commit_transaction(conn)

        #draw plot
        plot_analysis(age_group_query, conn, 'age_group', 'percentage_of_case', '% of Cancer Case by Age Groups')

        #end connection to DB
        po.end_transaction(cur, conn)
    except Exception as e:
        print(e)
        print("TERMINATING PROGRAM..")
        time.sleep(2)
        print("PROGRAM TERMINATED")
