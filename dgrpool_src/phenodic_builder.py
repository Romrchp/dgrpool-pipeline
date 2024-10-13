from helpers.dictionnary_building_helper import *
import os

DATA_DIRECTORY = f"..{os.sep}data" 
INFORMATION_DIRECTORY = f"..{os.sep}information" 
STUDIES_DIRECTORY = f"..{os.sep}studies" 
OUTPUT_DIRECTORY = f"..{os.sep}output" 
UNREFINDE_STUDY_LIST = f"..{os.sep}unrefined_study_information.xlsx"
STUDY_LIST = f"..{os.sep}study_information.xlsx"
PHENODIC = f"..{os.sep}dictionnary.xlsx"
STUDY_ANNOTATION = f"..{os.sep}study_annotation.xlsx"
EXTRACT = f"..{os.sep}Extract"

study_list = pd.read_excel(DATA_DIRECTORY + INFORMATION_DIRECTORY + STUDY_LIST)
xl_dictionnary = pd.read_excel(DATA_DIRECTORY + INFORMATION_DIRECTORY + PHENODIC)


#DictionnaryStart(study_list,xl_dictionnary) 
BuildDictionnary(xl_dictionnary)