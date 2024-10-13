import os
import json
import numpy as np
import pandas as pd
import itertools
import re
import matplotlib.pyplot as plt
import math

DATA_DIRECTORY = f"..{os.sep}data" 
INFORMATION_DIRECTORY = "information" 
DICTIONNARY_LINES = "dictionnaryLines.json"
DICTIONNARY = "dictionnary.xlsx"
STUDIES_DIRECTORY = "studies" 
OUTPUT_DIRECTORY = f"{os.sep}output" 

STUDY_LIST = f"{os.sep}study_information.xlsx"


def get_studies_of_line(line):
    nb_line = line.replace("DGRP_", "")
    studies_of_line = []
    dirs = sorted(os.listdir(f"{DATA_DIRECTORY}/{STUDIES_DIRECTORY}"))
    for siId in range(1, len(dirs)):
        data_study = pd.read_json(f'{DATA_DIRECTORY}/{STUDIES_DIRECTORY}/{dirs[siId]}')
        data_lines_used = [str(line) for line in data_study.iloc[0,:]]
        if line in data_lines_used or nb_line in data_lines_used:
            studies_of_line.append(f"{dirs[siId].replace('.json', '')}")

    return studies_of_line


def getExcelDictionnaryInfo(study, study_phenotype_used):
    dictionnary = pd.ExcelFile(f"{DATA_DIRECTORY}/{INFORMATION_DIRECTORY}/{DICTIONNARY}")
    dictionnary_sheet = dictionnary.parse("Sheet1")
    info_line_to_use = [study for study in dictionnary_sheet.iloc[:,0]].index(study)

    if not type(dictionnary_sheet.iloc[info_line_to_use, 3]) == float:
        abr_phenotype_names = re.split(r" , |, | ,|,", dictionnary_sheet.iloc[info_line_to_use, 2].replace("'", "").strip(']['))
    else:
        abr_phenotype_names = []
    if not type(dictionnary_sheet.iloc[info_line_to_use, 3]) == float:
        full_phenotype_names = re.split(r" , |, | ,|,", dictionnary_sheet.iloc[info_line_to_use, 3].replace("'", "").strip(']['))
    else:
        full_phenotype_names = abr_phenotype_names

    for i in range(len(study_phenotype_used)):
        try: 
            phenotype_nb = abr_phenotype_names.index(study_phenotype_used[i])
            study_phenotype_used[i] = [pheno_name for pheno_name in full_phenotype_names][phenotype_nb]
        except:
            print("Error !")

    return study_phenotype_used


def study_information(line, study):
    data_study = pd.read_json(f'{DATA_DIRECTORY}/{STUDIES_DIRECTORY}/{study}.json')
    line_nb = [str(line) for line in data_study.iloc[0,:]].index(line)
    study_phenotypes = [str(phenotype) for phenotype in data_study.index[2:]]
    study_phenotypes_values = data_study.iloc[2:, line_nb]
    valid_line_study_phenotype = []
    for i in range(len(study_phenotypes)):
        valNaN = 0
        for value in study_phenotypes_values[i]:
            if value == None:
                valNaN += 1
        if valNaN != len(study_phenotypes_values[i]):
            valid_line_study_phenotype.append(study_phenotypes[i])

    return valid_line_study_phenotype


def all_study_information(line):
    studies_of_line = get_studies_of_line(line)
    all_study_information = []
    for study in studies_of_line:
        full_name_phenotypes = getExcelDictionnaryInfo(study, study_information(line, study))
        all_study_information.append(full_name_phenotypes)
    return all_study_information


def all_lines_used():
    lines_used = []
    dirs = sorted(os.listdir(f"{DATA_DIRECTORY}/{STUDIES_DIRECTORY}"))
    for siId in range(1, len(dirs)):
        data_study = pd.read_json(f"{DATA_DIRECTORY}/{STUDIES_DIRECTORY}/{dirs[siId]}")
        data_lines_used = [line for line in data_study.iloc[0,:]]
        for new_line in data_lines_used:
            if not new_line in lines_used:
                lines_used.append(new_line)
    return sorted(lines_used)


def get_data(study, line, phenotype):
    data = pd.read_json(f"{DATA_DIRECTORY}/{STUDIES_DIRECTORY}/{study}.json")
    column = [pheno for pheno in data.index].index(phenotype)
    line_nb = [str(line) for line in data.iloc[0,:]].index(line)
    
    return data.iloc[column, line_nb]

def variance(data):
    mean = sum(data)/len(data)
    var_list = [(x-mean)**2 for x in data]
    return (sum(var_list)/len(var_list))**0.5


def gaussian_analysis(study, phenotype, sex):
    if sex == "F":  sex_id = 0
    elif sex == "M":  sex_id = 1
    elif sex == "NA":  sex_id = 2
    data = pd.read_json(f'{DATA_DIRECTORY}/{INFORMATION_DIRECTORY}/{DICTIONNARY_LINES}')
    mean_data = []
    lines_used = []
    for line_id in range(len(data.columns)):
        study_id = [study for study in data.iloc[:,line_id].index].index(study)
        data_line = data.iloc[study_id, line_id]
        if type(data_line) == dict:
            if data_line[phenotype][sex_id] != None and type(data_line[phenotype][sex_id]) != str:
                mean_data.append(data_line[phenotype][sex_id])
                lines_used.append(data.columns[line_id])

    mean = sum(mean_data)/len(mean_data)
    var = variance(mean_data)
    steps = [-1.645*var, -1.08*var, -0.739*var, -0.468*var, -0.228*var, 0, 0.228*var, 0.468*var, 0.739*var, 1.08*var, 1.645*var]
    lines_note = {}
    for line_id in range(len(lines_used)):
        for step in range(len(steps)):
            if (mean_data[line_id] - mean) < steps[step]:
                lines_note[lines_used[line_id]] = step
                break
            elif steps == len(steps)-1:
                lines_note[lines_used[line_id]] = -1
                break
    
    fig, ax = plt.subplots(figsize =(10, 7))
    ax.hist(mean_data)

    def gaussian(x, var, m):
        return 30/(var*(2*math.pi)**0.5) * np.exp(-0.5*((x-m)/var)**2)

    x = np.linspace(sorted(mean_data)[0], sorted(mean_data)[-1], 1000)
    plt.plot(x, gaussian(x, var, mean))
    plt.show()
    
    return lines_note




# dictionnary functions
def str_fix(line, study):
    study_data = {}
    sexes = get_data(study, line, "sex")
    for phenotype in study_information(line, study):
        data = [None, None, None]
        raw_data = get_data(study, line, phenotype)
        if "F" in sexes:    data[0] = raw_data[sexes.index("F")]
        if "M" in sexes:    data[1] = raw_data[sexes.index("M")]
        if "NA" in sexes:    data[2] = raw_data[sexes.index("NA")]
        study_data[phenotype] = data
    return study_data


def mean_phenotype_fix(line, study, sexes, circ_phenotypes):
    study_data = {}
    all_values = []
    circ_phenotypes_valid = []
    for circ_pheno in circ_phenotypes:
        values = []
        circ_phenotype_index = get_data(study, line, circ_pheno)
        for value in circ_phenotype_index:
            if (not value in values) and (value != None):
                values.append(value)
        if values != []:
            all_values.append(values)
            circ_phenotypes_valid.append(circ_pheno)

    if len(all_values) == 1:
        combinations = [[i] for i in all_values[0]]
    else:
        combinations = list(itertools.product(all_values[0], all_values[1]))
        for values in all_values[2:]:
            combinations = list(itertools.product(combinations, values))
            for comb in range(len(combinations)):
                final = []
                for z in combinations[comb][0]:
                    final.append(z)
                final.append(combinations[comb][1])
                combinations[comb] = tuple(final)


    for values in combinations:
        end_desc = ""
        for pheno_id in range(len(circ_phenotypes_valid)):
            end_desc += f"/{circ_phenotypes_valid[pheno_id]}={values[pheno_id]}"
        all_phenotypes = study_information(line, study)
        info_circ_pheno = []
        for circ_pheno in circ_phenotypes_valid:
            info_circ_pheno.append(get_data(study, line, circ_pheno))

        for phenotype in all_phenotypes:
            if phenotype in circ_phenotypes:
                pass
            else:
                data = [None, None, None]
                data_F = []
                data_M = []
                data_NA = []
                raw_data = get_data(study, line, phenotype)

                all_NaN = True
                for NaN_data in raw_data:
                    if NaN_data != None:
                        all_NaN = False
                        break

                if not all_NaN:
                    for sex_id in range(len(sexes)):
                        if raw_data[sex_id] != None:
                            information = []
                            for x in range(len(info_circ_pheno)):
                                information.append(info_circ_pheno[x][sex_id])
                            if len(information) != 1:
                                information = tuple(information)
                            if information == values:
                                if sexes[sex_id] == "F":
                                    data_F.append(raw_data[sex_id])
                                elif sexes[sex_id] == "M":
                                    data_M.append(raw_data[sex_id]) 
                                elif sexes[sex_id] == "NA":
                                    data_NA.append(raw_data[sex_id])

                    if data_F != []:    data[0] = sum(data_F)/len(data_F)
                    if data_M != []:    data[1] = sum(data_M)/len(data_M)
                    if data_NA != []:    data[2] = sum(data_NA)/len(data_NA)
                study_data[phenotype + end_desc] = data
                
    return study_data

def mean_fix(line, study):
    sexes = get_data(study, line, "sex")
    phenotype_list = study_information(line, study)
    circ_phenotypes = []
    circ_list = ["treatment", "Treatment", "Wo", "Line_Status", "condition", "Mating", "Temperature", "temperature", "Body part", "diet", "s", "MatingStatus", "Mating Status", "Mating_status", "Infection_treatment", "Infection"]
    for x in circ_list:
        if x in phenotype_list:
            circ_phenotypes.append(x)

    data = mean_phenotype_fix(line, study, sexes, circ_phenotypes)
    return data

def column_fix(line, study):
    study_data = {}
    sexes = get_data(study, line, "sex")
    for phenotype in study_information(line, study):
        raw_data = get_data(study, line, phenotype)
        data = [None, None, None]
        data_F = []
        data_M = []
        data_NA = []
        str_alert = False
        for sex_id in range(len(sexes)):
            try:
                if raw_data[sex_id] != None:
                    if sexes[sex_id] == "F":
                        data_F.append(raw_data[sex_id])
                    elif sexes[sex_id] == "M":
                        data_M.append(raw_data[sex_id]) 
                    elif sexes[sex_id] == "NA":
                        data_NA.append(raw_data[sex_id])
            except:
                if raw_data[0] != None:
                    if sexes[sex_id] == "F":
                        data_F.append(raw_data[0])
                    elif sexes[sex_id] == "M":
                        data_M.append(raw_data[0]) 
                    elif sexes[sex_id] == "NA":
                        data_NA.append(raw_data[0])
            for x in data_F:
                if type(x) == str:
                    str_alert = True
                    break
            for x in data_M:
                if type(x) == str:
                    str_alert = True
                    break
            for x in data_NA:
                if type(x) == str:
                    str_alert = True
                    break
            if not str_alert:
                if data_F != []:    data[0] = sum(data_F)/len(data_F)
                if data_M != []:    data[1] = sum(data_M)/len(data_M)
                if data_NA != []:    data[2] = sum(data_NA)/len(data_NA)
            else:
                if data_F != []:    data[0] = data_F[0]
                if data_M != []:    data[1] = data_M[0]
                if data_NA != []:    data[2] = data_NA[0]
        study_data[phenotype] = data
    return study_data

# to make the dictionnary
def makeDictionnaryLines():
    str_problem_studies = ["SI017", "SI022", "SI028", "SI037", "SI046", "SI097", "SI106", "SI044", "SI065"]
    mean_problem_studies = ["SI043", "SI047", "SI078", "SI041", "SI058", "SI059", "SI075", "SI076", "SI089", "SI095", "SI100", "SI105", "SI116", "SI120", "SI121"]
    column_problem_studies = ["SI085", "SI102", "SI103"]
    blacklisted_studies = ["SI105"]
    all_lines = {}
    for line in all_lines_used()[0:1]:
        line = "DGRP_026"
        print(line)
        all_lines[line] = {}
        for study in get_studies_of_line(line):
            print(study)
            if study in blacklisted_studies:
                print("\n WAIT \n")
            elif study in str_problem_studies:
                all_lines[line][study] = str_fix(line, study)
            elif study in mean_problem_studies:
                all_lines[line][study] = mean_fix(line, study)
            elif study in column_problem_studies:
                all_lines[line][study] = column_fix(line, study)
            
            else:
                all_lines[line][study] = {}
                sexes = get_data(study, line, "sex")
                for phenotype in study_information(line, study):
                    data = [None, None, None]
                    data_F = []
                    data_M = []
                    data_NA = []
                    raw_data = get_data(study, line, phenotype)
                    for sex_id in range(len(sexes)):
                        if raw_data[sex_id] != None:
                            if sexes[sex_id] == "F":
                                data_F.append(raw_data[sex_id])
                            elif sexes[sex_id] == "M":
                                data_M.append(raw_data[sex_id]) 
                            elif sexes[sex_id] == "NA":
                                data_NA.append(raw_data[sex_id])
                    if data_F != []:    data[0] = sum(data_F)/len(data_F)
                    if data_M != []:    data[1] = sum(data_M)/len(data_M)
                    if data_NA != []:    data[2] = sum(data_NA)/len(data_NA)
                    all_lines[line][study][phenotype] = data
    
    json_obj = json.dumps(all_lines)
    with open(f"{DATA_DIRECTORY}/{INFORMATION_DIRECTORY}/{DICTIONNARY_LINES}", "w") as fileDico:
        fileDico.write(json_obj)
        print("\n PRINTED")