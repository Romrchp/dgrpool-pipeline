from general_helper import *

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import json
import seaborn as sns
import os.path
import itertools
import numpy as np
import scipy as sp
from scipy import stats
import matplotlib
from scipy.stats import entropy
from scipy.stats import pearsonr
from scipy.stats import spearmanr


DATA_DIRECTORY = "../data" 
INFORMATION_DIRECTORY = "/information" 
STUDIES_DIRECTORY = "/studies" 
OUTPUT_DIRECTORY = "/output" 
UNREFINDE_STUDY_LIST = "/unrefined_study_information.xlsx"
STUDY_LIST = "/study_information.xlsx"
STUDY_ANNOTATION = "/study_annotation.xlsx"
EXTRACT = "/Extract"

def jsonFetcher(CurrS):
      
     if(os.path.exists(DATA_DIRECTORY + STUDIES_DIRECTORY + "/"+ CurrS + EXTRACT )) :
        
            op = open(DATA_DIRECTORY + STUDIES_DIRECTORY + "/"+ CurrS + EXTRACT + "/" + CurrS + ".json",)
            ogjson = json.load(op)
            
            colnames = []
            for colname in ogjson['0'] :
                colnames.append(colname)
            
            workingdf = pd.DataFrame(columns=colnames)
            
            for line in ogjson :
                workingdf = workingdf.append(ogjson[line], ignore_index=True)
                    
            return workingdf;         
            
     else :
        
        return(CurrS + " doesn't provide us with any interesting data for further analyses")
       

def GetPhenoNames(study_df):
    FirstPhenoIndex = 0
    PhenoNames = []
    for ColName in study_df.columns.values:
        
        if ColName == "sex" :
            for i in range(FirstPhenoIndex+1,np.size(study_df.columns.values)) :
               PhenoNames.append(study_df.columns.values[i])
            break;
        else :
            FirstPhenoIndex += 1
    #print(PhenoNames)       
    return PhenoNames;        


def GatherValues(studydf,pheno_name,sex) :
    
   values_dictionnary = {}
     
   if isinstance(studydf, str)  :
    return(values_dictionnary,False)
   else:
    
    for index, row in studydf.iterrows() :
        
     if sex not in row["sex"] :
        #print(row["Line"]+ "does not possess a value for this specific phenotype/sex pair")
        pass
        
     else: 
        
      if row["sex"].count(sex) > 1 :
        indexes = get_index_positions(row["sex"],sex)
        values_gathered = [row[pheno_name][i] for i in indexes]
        
        if any(isinstance(value,str) for value in values_gathered) :
            return(values_dictionnary,False)   
            
        else :
            if not np.isnan(final_value):
                final_value = np.mean(values_gathered)
                values_dictionnary[row["Line"]] = final_value
      else :

        index = row["sex"].index(sex)
        final_value = row[pheno_name][index]
        
        if type(final_value) == str :
            return(values_dictionnary,False) 
        
        else:
            if not np.isnan(final_value) :
                values_dictionnary[row["Line"]] = final_value  
     
    if values_dictionnary :
        return(values_dictionnary,True) 
    else:
        return(values_dictionnary,False)

def TableBuilder(first_pheno,second_pheno,sex,studydf) :
    
     first_pheno_infos = GatherValues(studydf,first_pheno,sex)
     second_pheno_infos = GatherValues(studydf,second_pheno,sex)
     final_table = []
     
     if (first_pheno_infos[1]) == False :
        return("A mapping of some sort would be necessary for the '" + first_pheno + "' phenotype of the current study, as it contains strings.",False)
     
     elif (second_pheno_infos[1]) == False :
        return("A mapping of some sort would be necessary for the '" + second_pheno + "' phenotype of the current study, as it contains strings.",False)
        
     else:
        
        for line in first_pheno_infos[0] :    
            if line in second_pheno_infos[0] :
                
                final_table.append([line,first_pheno_infos[0][line],second_pheno_infos[0][line]])       
     return(final_table,True)       


def stats_analysis(table_array,fp_names,sp_names,studied_sex,study_id):
    
    fp_abvname, fp_realname = fp_names[0],fp_names[1]
    sp_abvname, sp_realname = sp_names[0],sp_names[1]
    
    all_values = table_array[:,1:3].astype(np.float64)
    fp_values = table_array[:,1].astype(np.float64)
    sp_values = table_array[:,2].astype(np.float64)
    stat_df = pd.DataFrame(all_values, columns = [fp_realname,sp_realname])

    
    #Get the spearman rho's value as well as the p-value
    rho, pvalue = spearmanr(fp_values,sp_values)
    
    if rho > 0.3 :

     p = sns.jointplot(x=fp_values, y=sp_values,kind = "reg",height = 8);
     plt.rcParams.update({'figure.max_open_warning': 0})
     p.fig.tight_layout()
     p.set_axis_labels(fp_realname,sp_realname, fontsize=12)
     p.fig.subplots_adjust(top=0.95) 
     p.ax_joint.annotate(f'Spearmans $\\rho = {rho:.3f}, p = {pvalue:.5f}$',
                    xy=(0.05, 0.98), xycoords='axes fraction',
                    ha='left', va='center',
                    bbox={'boxstyle': 'round', 'fc': 'LightSteelBlue', 'ec': 'navy'})
     
        
     path = DATA_DIRECTORY + STUDIES_DIRECTORY + "/"+ study_id + OUTPUT_DIRECTORY
    
     if not (os.path.exists(path)) :
             os.mkdir(path)
             
     p.fig.savefig(path + "/" + fp_abvname + '_' + sp_abvname + studied_sex+ '.jpg',bbox_inches = 'tight')
     
     
     print('Some correlation was found and graph has been created for ' + fp_realname +' and '+ sp_realname +', concerning the follwing sex : ' + studied_sex) 


def CorrelationsFinder(studydf,study_id) :
    
     CurrStudyPhenos = GetPhenoNames(studydf)
     f = open(DATA_DIRECTORY + INFORMATION_DIRECTORY + "/phenodic.json")
     phenodic = json.load(f)
    
     for phenos in itertools.combinations(CurrStudyPhenos,2) :
            
            first_pheno_names = [phenos[0],phenodic[phenos[0]][0]]
            second_pheno_names = [phenos[1],phenodic[phenos[1]][0]]
        
            for studied_sex in ['M','F','NA'] :

                curr_pair_infos = TableBuilder(phenos[0],phenos[1],studied_sex,studydf)
                if curr_pair_infos[1] == False :
                    pass
                elif curr_pair_infos[1] == True :      
                    curr_table = curr_pair_infos[0]
                    statistical_results = stats_analysis(np.asarray(curr_table),first_pheno_names,second_pheno_names,studied_sex,study_id)    


def IntraCorrs() :
    studies = pd.read_excel(DATA_DIRECTORY + INFORMATION_DIRECTORY + STUDY_LIST)
    for index, row in studies.iterrows():
        study_id = row["StudyID"]
        CorrelationsFinder(jsonFetcher(study_id),study_id)