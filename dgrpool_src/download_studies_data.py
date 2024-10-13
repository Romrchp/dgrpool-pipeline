from helpers.download_helper import *


DATA_DIRECTORY = f"..{os.sep}data" 
INFORMATION_DIRECTORY = f"{os.sep}information" 
STUDIES_DIRECTORY = f"{os.sep}studies" 
OUTPUT_DIRECTORY = f"{os.sep}output" 

STUDY_LIST = f"{os.sep}study_information.xlsx"


studies = pd.read_excel(DATA_DIRECTORY + INFORMATION_DIRECTORY + STUDY_LIST)

create_adequate_dirs(studies,DATA_DIRECTORY,STUDIES_DIRECTORY)

FTP_download(studies,DATA_DIRECTORY,STUDIES_DIRECTORY)
figshare_download(studies,DATA_DIRECTORY,STUDIES_DIRECTORY)
github_download(studies,DATA_DIRECTORY,STUDIES_DIRECTORY)
