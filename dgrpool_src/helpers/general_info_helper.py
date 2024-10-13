import pandas as pd
import numpy as np
import parse
from habanero import Crossref

def get_general_info_from_titles(titles):
    cr = Crossref()
    
    dois = []
    journals = []
    years = []
    authors = []
    abbreviation = []
    
    for title in titles:

        res = cr.works(query_title = title, limit = 1)
        
        dois.append('DOI: ' + res['message']['items'][0]['DOI'])

        journals.append(res['message']['items'][0]['publisher'])

        years.append(res['message']['items'][0]['created']['date-parts'][0][0])
        
        paper_authors = res['message']['items'][0]['author']
        authors_family = list([author['family'] for author in paper_authors])
        authors_given = list([ ''.join(list([name[0].upper() for name in author['given'].split()])) for author in paper_authors])
        paper_authors = []
        for i,family in enumerate(authors_family):
            paper_authors.append( family + ' '+  authors_given[i])
        authors.append(', '.join(paper_authors))
        
        abbreviation.append(authors_family[0] + str(res['message']['items'][0]['created']['date-parts'][0][0]))      
        
    
    return dois, journals, years, authors, abbreviation;


def isNew(doi, studies):
    return doi not in list(studies['DOI'])

def set_identifiers(unrefined_studies,studies) :

    tmp_unrefined_studies = unrefined_studies
    format_string = 'SI{:0>3}'
    identifiers = list([ int(parse.parse(format_string,string)[0]) for string in studies['StudyID']])
    first_new_identifier = max(identifiers) + 1
    new_identifiers = np.arange(first_new_identifier,first_new_identifier + unrefined_studies.shape[0],1)
    tmp_unrefined_studies['StudyID'] =  list([ format_string.format(id) for id in new_identifiers])
    return tmp_unrefined_studies;

def add_annotations(studies_df,annotations_df) :
    final_df = studies_df.merge(annotations_df, how = 'left', on = 'StudyID')
    final_df['Annotated'] = True
    return final_df;

def prepare_download_infos(df) :
    df['Annotated'] = True
    df['Downloaded'] = False
    df['FTP_Downloaded'] = False
    df['FTP'] = np.nan
    df['Figshare_Downloaded'] = False
    df['Figshare_ID'] = np.nan
    df['Github_Downloaded'] = False
    df['Github_Link'] = np.nan
    df['Closed_Access_Identified'] = False

    return df;  

