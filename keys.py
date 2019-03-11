import os
import xmltodict
import types
import collections

ordereddict = collections.OrderedDict()

def find_keys(col, L):
    if type(col) == type(""):
        return []
    else:
        #print(list(col.keys()))
        if type(col) == type(ordereddict):
            L.extend(list(col.keys()))
            for item in col:
                find_keys(col[item], L)
        else:
            for i in range(len(col)):
                if type(col[i]) == type(ordereddict):
                    find_keys(col[i], L)

if __name__ == '__main__':
    files = [f for f in os.listdir('.') if f.endswith('.xml')]
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

    while(count < 10000):

        try:
            with open(files[count], 'rb') as c:
                doc = xmltodict.parse(c.read())
                L = []
                find_keys(doc, L)
                #print(files[count])


                try:
                    nct_id = doc['clinical_study']['id_info']['nct_id']
                except Exception as e:
                    nct_id = None
                    nct_id_not_found +=1
                    print(e)
                try:
                    title = doc['clinical_study']['brief_title']
                except Exception as e:
                    title = None
                    title_not_found +=1
                    print(e)
                try:
                    summary = doc['clinical_study']['brief_summary']['textblock']
                except Exception as e:
                    summary = None
                    summary_not_found +=1
                    print(e)
                try:
                    status = doc['clinical_study']['overall_status'].upper()
                    #unknown status
                except Exception as e:
                    status = 'UNKNOWN STATUS'
                    status_not_found += 1
                    print(e)

                try:
                    study_type = doc['clinical_study']['study_type']
                except Exception as e:
                    study_type = None
                    study_type_not_found += 1
                    print(e)

                try:
                    url = doc['clinical_study']['required_header']['url']
                except Exception as e:
                    url = "https://clinicaltrials.gov/ct2/show/" + nct_id
                    url_not_found += 1
                    print(e)

                try:
                    gender = doc['clinical_study']['eligibility']['gender']
                except Exception as e:
                    gender = None
                    gender_not_found +=1
                    print(e)

                try:
                    min_age = doc['clinical_study']['eligibility']['minimum_age']
                except Exception as e:
                    min_age = "N/A"
                    min_age_not_found +=1
                    print(e)

                try:
                    max_age = doc['clinical_study']['eligibility']['maximum_age']
                except Exception as e:
                    max_age = "N/A"
                    max_age_not_found +=1
                    print(e)

                try:
                    healthy_volunteers = doc['clinical_study']['eligibility']['healthy_volunteers']
                except Exception as e:
                    healthy_volunteers = None
                    healthy_volunteers_not_found += 1
                    print(e)

                try:
                    allocation = doc['clinical_study']['study_design_info']['allocation']
                except Exception as e:
                    allocation = None
                    allocation_not_found += 1
                    print(e)

                try:
                    purpose = doc['clinical_study']['study_design_info']['primary_purpose']
                except Exception as e:
                    purpose = None
                    purpose_not_found += 1
                    print(e)

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
                    print(e)

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
                    print(e)

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
                    print(e)

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
                    print(e)

                try:
                    source = doc['clinical_study']['source']
                except Exception as e:
                    source = None
                    source_not_found += 1
                    print(e)

                #print('study_design_info' in doc['clinical_study']['studyin'])
                #print(list(set(L)))
                #print(L)
                c.close()
            count += 1
        except Exception as e:

            print(e)
        #print(status)

