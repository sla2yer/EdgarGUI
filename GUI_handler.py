import os

from Edgar_filingviewer import FilingViewer
from Edgar_database import EdgarDatabase
from Edgar_downloader import EdgarDownloader
from File_manager import FileManager
from Edgar_parser import Parser
import re


class GUI_handler:

    def __init__(self):
        self.downloader = EdgarDownloader()
        self.database = EdgarDatabase(True)
        self.handler_files = FileManager()
        self.result_message_list = []
        self.found_entity = False

    # the date parameters are passed over as strings of dateTime objects or are "" if not being used
    def searchForFiling(self, institute, filing_type, start_date, end_date):
        # check length of date strings to see if dates are provided
        # date is returned as a list of int values [ yyyy, mm, dd]
        if len(start_date) > 0:
            start_date_int = self.dateToInt(start_date)
        else:
            start_date_int = start_date
        if len(end_date) > 0:
            end_date_int = self.dateToInt(end_date)
        else:
            end_date_int = end_date

        result = self.downloader.searchForInstitute(institute, filing_type, start_date_int, end_date_int, self.handler_files.getTempFolderDirectory())
        res_string = str(result)
        if ("will be skipped" in res_string):
            self.result_message_list.append("could not find the instituitons given, Please select one of the following")
            for name in self.formatMatchingCompanies(res_string):
                self.result_message_list.append(name)
            self.found_entity = False
            return False

        elif ("No results" in res_string):
            self.result_message_list.append(str(res_string))
            self.found_entity = False
            return False

        elif ("Only 0 of" in res_string):
            index_num_filings = res_string.find("of ") + 3
            self.result_message_list.append("Found the institution, No filings of the specified type were found\n")
            self.result_message_list.append(
                res_string[index_num_filings:(index_num_filings + 2)] + " other filings were found")
            self.found_entity = True
            return True

        # ELSE FILINGS WERE FOUND
        else:
            self.result_message = res_string
            # this method calls the parser to get the details from filings, check if they are already inserted into the database and insert if not
            # and then construct a list of strings (saved to self.result_message)
            self.database.manualConnect()
            self.parseResults(institute, filing_type)
            self.database.commit()
            self.generateFormattedResult(institute, filing_type)
            self.handler_files.deleteTempFilesandFolders()
            self.database.close()
            self.found_entity = True
            return True

    def foundEntity(self):
        return self.found_entity

    def compareButtonActions(self):
        return

    def openFilings(self, filings, toplevel):
        fv = FilingViewer(filings, toplevel)
        return

    def trackButtonActions(self, entity_list):
        # for each entity in the list grab their entity_id using their name

        return

    def scrub(self, text):
        text = re.sub(r'(^[ \t]+|[ \t]+(?=:))', '', text, flags=re.M)
        return text

    def formatMatchingCompanies(self, res_string):
        res_string = res_string[res_string.find(":") + 4:]
        res_string = res_string.split("\n")
        res_string[0] = self.scrub(res_string[0])
        return (res_string)

    def isEntityComplete(self, entity):
        result = self.database.getEntityIRSNumber(entity)
        if result is None:
            return False
        else:
            return True

    def parseResults(self, entity, filing_type):
        # use the handler_files to get the accession numbers from the file names
        list_of_accession_numbers = self.handler_files.getAccessionNumbers(entity, filing_type)

        # first check if the entity searched for is in the database,
        if self.database.isEntityInDatabase(entity):
            if self.database.getEntityIRSNumber(entity) is None:
                with Parser(self.handler_files.getFileText(list_of_accession_numbers[0]), str(filing_type)) as p:
                    p.completeFilingEntity(self.database, entity)
            # if the entity is already in the database then check each filing with the accession numbers
            # to find if they need to be parsed or not

            for number in list_of_accession_numbers:
                # check if the accession number is not in the database
                if not self.database.isAccessionNumberInDatabase(self.formatAccNumber(number)):
                    parser = Parser(self.handler_files.getFileText(number), str(filing_type))
                    parser.parseFiling(self.database, entity)
        else:
            # else the entity is not in the database then for the first accession number parse the entity
            with Parser(self.handler_files.getFileText(list_of_accession_numbers[0]), str(filing_type)) as p:
                p.parseFilingAndEntity(self.database)

            # now just get the details from the rest of the filings
            for number in list_of_accession_numbers:
                # check if the accession number is in the database
                if not self.database.isAccessionNumberInDatabase(self.formatAccNumber(number)):
                    parser = Parser(self.handler_files.getFileText(number), str(filing_type))
                    parser.parseFiling(self.database, entity)

    def formatAccNumber(self, acc_num):
        acc_num = acc_num[:4] + "-" + acc_num[4:6] + "-" + acc_num[6:]
        return acc_num

    def generateFormattedResult(self, entity, filing_type):
        # from here all info from the filings should be in the database
        temp_list = ["accession #  | Filing type | Filed on "]
        list_of_accession_numbers = self.handler_files.getAccessionNumbers(entity, filing_type)
        for num in list_of_accession_numbers:
            num = self.formatAccNumber(num)
            # find if the num reports holdings or not
            # file_number = self.database.getFilingNumber(num)
            if self.database.isFilingReportingHoldings(num):
                temp_string = str(num) + " | 13F-HR | "
            else:
                temp_string = str(num) + " | 13F-NT | "
                # find the filed date
            temp_string = temp_string + self.database.getFiledOnDate(num)
            temp_list.append(temp_string)
        self.result_message_list = temp_list

    def getResultMessage(self):
        return self.result_message_list

    def getTrackedEntities(self):
        temp = []
        with EdgarDatabase(False) as db:
            db.manualConnect()
            temp = db.getTrackedEntities()

    def clearResultMessage(self):
        self.found_entity = False
        self.result_message_list.clear()

    def dateToInt(self, date):
        # the date  is a string in the format of yyy-mm-dd, with a zero in the first position for single digit numbers (e.g 01).
        string_list = date.split("-")
        int_list = []
        for s in string_list:
            int_list.append(int(s))
        return int_list

    def setSecID_messageBox(self):

        return

    def clearDB_messageBox(self):
        self.database.manualConnect()
        self.database.clear_database()
        self.database.close()
        return

    def getTempFileLocation(self):
        self.database.manualConnect()
        res = self.database.getTempFileLocation()
        if len(res) < 1:
            p = os.path.expanduser('~')
            self.database.insertTempFileLocation(p)
            self.database.commit()
            self.database.close()
            return p
        else:
            return str(res[0][1])

