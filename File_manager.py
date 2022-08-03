import glob
import os
from pathlib import Path
import platform
from Edgar_database import EdgarDatabase


class FileManager:

    def __init__(self):
        self.file_system = platform.system()
        self.temp_folder_directory = self.getTempFolderDirectory()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_tb):
        return

    def getTempFolderDirectory(self):
        with EdgarDatabase(False) as db:
            db.manualConnect()
            res = db.getTempFileLocation()
            if len(res) < 1:
                p = os.path.expanduser('~')
                db.insertTempFileLocation(p)
                db.commit()
                db.close()
                return p
            else:
                return str(res[0][1])


    def getHomePath(self):
        return os.path.expanduser('~')

    def cleanFiletypeString(self, filing_type):
        if 'linux' in str(self.file_system):
            return filing_type
        else:
            if '\\' in str(filing_type):
                temp = str(filing_type).split('\\')
                return '\\'.join(temp)
            else:
                return filing_type

    def getAccessionNumbers(self, entity, filing_type):
        file_type = str(filing_type)[str(filing_type).find("_") + 1:].lower()
        if '\\' in self.getHomePath():
            file_string1 = self.temp_folder_directory + "\\EdgarAppTempFolders\\" + entity + "\\" + file_type + "\\" + "*.txt"
        else:
            file_string1 = self.temp_folder_directory + "/EdgarAppTempFolders/" + entity + "/" + file_type + "/" + "*.txt"
        file_names = glob.glob(file_string1)
        temp_list = []
        for filename in file_names:
            t_index = filename.find(file_type) + len(file_type) + 1
            dot_index = filename.find('.txt')
            temp_list.append(filename[t_index:dot_index])
        print(temp_list)
        return temp_list

    def getFileText(self, acc_number, name, filing_type):
        if ("\\" not in self.file_system):
            glob_string = f"{self.temp_folder_directory}/EdgarAppTempFolders/{name}/{filing_type}/{str(acc_number)}.txt"
        else:
            glob_string = f"{self.temp_folder_directory}\\EdgarAppTempFolders\\{name}\\{filing_type}\\{str(acc_number)}.txt"
        print(f'glob string: {glob_string}')
        file_name = glob.glob(glob_string)
        file_text = Path(file_name[0]).read_text()
        return file_text

    def deleteTempFilesandFolders(self):
        # remove files
        if ("//" not in self.file_system):
            glob_strings = [self.temp_folder_directory + "/EdgarAppTempFolders/*/*/*.txt",
                            self.temp_folder_directory + "/EdgarAppTempFolders/*/*",
                            self.temp_folder_directory + "/EdgarAppTempFolders/*"]
        else:
            glob_strings = [ self.temp_folder_directory + "\\EdgarAppTempFolders\\*\\*\\*.txt",
                             self.temp_folder_directory + "\\EdgarAppTempFolders\\*\\*",
                             self.temp_folder_directory + "\\EdgarAppTempFolders\\*"]

        file_names = glob.glob(glob_strings[0])
        for file in file_names:
            if os.path.exists(file):
                os.remove(file)

        # remove filing type folders
        filing_type_folder_names = glob.glob(glob_strings[1])

        for folder in filing_type_folder_names:
            folder_path = Path(folder)
            if folder_path.is_dir():
                os.rmdir(folder)

        # remove entity folders
        folder_names = glob.glob(glob_strings[2])
        for folder in folder_names:
            folder_path = Path(folder)
            if folder_path.is_dir():
                os.rmdir(folder)
