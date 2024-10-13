from general_helper import *

import pandas as pd
import json
import os.path

DATA_DIRECTORY = "..\\data" 
INFORMATION_DIRECTORY = "\\information" 
STUDIES_DIRECTORY = "\\studies" 
OUTPUT_DIRECTORY = "\\output" 
UNREFINDE_STUDY_LIST = "\\unrefined_study_information.xlsx"
STUDY_LIST = "\\study_information.xlsx"
PHENODIC = "\\dictionnary.xlsx"
STUDY_ANNOTATION = "\\study_annotation.xlsx"
EXTRACT = "\\Extract"


def GetPhenoNames(currjson):
    PhenoNames = []
    for key in currjson['0']  :
        print(key)
        if key != "sex" and key != "Line" :
               PhenoNames.append(key)

    print(PhenoNames)       
    return PhenoNames;  

def PhenosFetcher(CurrS):
  
   if(os.path.exists(DATA_DIRECTORY + STUDIES_DIRECTORY + "\\"+ CurrS + EXTRACT )) :
        
            f = open(DATA_DIRECTORY + STUDIES_DIRECTORY + "\\"+ CurrS + EXTRACT + "\\" + CurrS + ".json",)
            currjson = json.load(f)

            if not currjson :
               return ("No exploitable phenotypes for" + CurrS);
        
            else :     
               PhenoNames = GetPhenoNames(currjson)
               return PhenoNames;     

   else:
        return("No json file for "+ CurrS);
   

def DictionnaryStart(gathered_studies,dictionnaryxlsx) :
    
    dictionnaryxlsx["StudyID"] = gathered_studies["StudyID"]
    dictionnaryxlsx["All phenotype(s)"] = dictionnaryxlsx["All phenotype(s)"].astype(object)
   
    
    for study in dictionnaryxlsx["StudyID"]:
        if(os.path.exists(DATA_DIRECTORY + STUDIES_DIRECTORY + "\\" + study + EXTRACT + "\\" +study + ".json" )) :
        
           CurrIndex = dictionnaryxlsx.index[dictionnaryxlsx["StudyID"] == study].values.astype(int)[0]
           CurrPhenos = PhenosFetcher(study)
           dictionnaryxlsx.at[CurrIndex,"All phenotype(s)"] = CurrPhenos
           dictionnaryxlsx.at[CurrIndex,"Number of exploitable phenotypes"] = len(CurrPhenos)
    
    dictionnaryxlsx.to_excel(DATA_DIRECTORY + INFORMATION_DIRECTORY + PHENODIC, index = False) 
    return("The excel dictionnary file has been built in ")


def BuildDictionnary(xlsxdico) :

    phenodic = {}
    
    for index,row in xlsxdico.iterrows() :
        
        tmpAbvnames = row["All phenotype(s)"]
        tmpStdnames = row["Standard phenotype name"]
        
        if (not pd.isnull(tmpAbvnames)) and (not pd.isnull(tmpStdnames))  :
            Abvnames,Stdnames = GetListElements(tmpAbvnames), GetListElements(tmpStdnames)
            
            for abv, std in zip(Abvnames, Stdnames):
                phenodic[abv] = (std,row["StudyID"])

        else:
            print(row["StudyID"]+' does not have any exploitable phenotypes')
    
    with open('../data/information/phenodic.json', 'w') as f:
         json.dump(phenodic, f)
    #print(phenodic)        
    return('The dictionnary has been built !')
