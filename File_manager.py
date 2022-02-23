import glob
import os
from pathlib import Path
import platform
class FileManager:
    
    def __init__(self):
        i = 0
        self.file_system = platform.system()
        
    def cleanFiletypeString(self,  file_type):
        return file_type[file_type.find("_") + 1:].lower()
    
    def getAccessionNumbers(self,  entity,  filing_type):
        file_type = self.cleanFiletypeString(str(filing_type))

        if ("Linux" in self.file_system):
            file_string1 = "/home/pi/EdgarAppTempFolders/" + entity + "/" + file_type + "/" + "*.txt"
        elif ("Windows" in self.file_system):
            file_string1 = "C:\\Users\\rubio\\Documents\\EdgarAppTempFolders\\" + entity + "\\" + file_type + "\\" + "*.txt"
        file_names = glob.glob(file_string1)
        temp_list = []
        for filename in file_names:
            t_index = filename.find(file_type) + len(file_type) +1
            dot_index = filename.find('.txt')
            temp_list.append(filename[t_index:dot_index])
        print(temp_list)
        return temp_list
        
        #--------------TO DO --------------

    def getFileText(self,  number):
        if ("Linux" in self.file_system):
            glob_string = "/home/pi/EdgarAppTempFolders/*/*/" + str(number) + ".txt"
        elif ("Windows" in self.file_system):
            glob_string = "C:\\Users\\rubio\\Documents\\EdgarAppTempFolders\\*\\*\\" + str(number) + ".txt"
        file_name = glob.glob(glob_string)
        file_text = Path(file_name[0]).read_text()
        return file_text
        
    def deleteTempFilesandFolders(self):
        #remove files
        if ("Linux" in self.file_system):
            glob_strings = ["/home/pi/EdgarAppTempFolders/*/*/*.txt", "/home/pi/EdgarAppTempFolders/*/*","/home/pi/EdgarAppTempFolders/*" ]
        elif ("Windows" in self.file_system):
            glob_strings = ["C:\\Users\\rubio\\Documents\\EdgarAppTempFolders\\*\\*\\*.txt", "C:\\Users\\rubio\\Documents\\EdgarAppTempFolders\\*\\*", "C:\\Users\\rubio\\Documents\\EdgarAppTempFolders\\*"]

        file_names = glob.glob(glob_strings[0])
        for file in file_names:
            if os.path.exists(file):
                os.remove(file)
        
        #remove filing type folders 
        filing_type_folder_names = glob.glob(glob_strings[1])
        
        for folder in filing_type_folder_names:
            folder_path = Path(folder)
            if folder_path.is_dir():
                os.rmdir(folder)
        
        #remove entity folders
        folder_names = glob.glob(glob_strings[2])
        for folder in folder_names:
            folder_path = Path(folder)
            if folder_path.is_dir():
                os.rmdir(folder)
        

