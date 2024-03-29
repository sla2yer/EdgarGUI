import os
from Edgar_filingviewer import FilingViewer
from Edgar_database import EdgarDatabase
from Edgar_downloader import EdgarDownloader
from File_manager import FileManager
from Edgar_parser import Parser
from datetime import datetime
import re


class GUI_handler:
    def __init__(self):
        self.downloader = EdgarDownloader()
        self.database = EdgarDatabase(False)
        self.handler_files = FileManager()
        self.result_message_list = []
        self.found_entity = False

    def getMostRecentFilingDate_search(self, entity_name, filing_type):
        """
        attempts download and parse of filings to ensure database has most recent filings
        before retrieving and returning the latest filing date from the database
        :type entity_name: str
        :returns latest_file_date: str
        """
        print('get most recent filing date')
        filing_type_string = str(filing_type)[str(filing_type).find('_') + 1:len(str(filing_type))]
        self.database.manualConnect()
        # if there are any filings in the database filed by the specified entity and filing type
        if self.database.isEntityAndFilingTypeInDatabase(entity_name=entity_name, filing_type=filing_type_string):
            print('entty is in the database with the filing type')

            # at this point there for sure is a filing n the database
            # grab the most recent filings file date from the database and set start_date = to it
            res = self.database.getMostRecentFilingDateForFilingType(entity_name, filing_type_string)
            start_date = str(res[0][0])
        else:
            # set start_date to '' to get all filings from the entity
            start_date = ''
        print(f'start  date: {start_date}')
        if len(start_date) > 0:
            start_date_int = self.dateToInt(start_date)
        else:
            start_date_int = start_date
        self.database.manualConnect()
        ua = self.database.getSecID()
        self.database.close()
        ua = f"{ua[0][0]} ({ua[0][1]})"
        search_results = self.downloader.searchForInstitute(
                                                    institute=entity_name,
                                                    filing_type=filing_type,
                                                    start_date=start_date_int,
                                                    end_date='',
                                                    temp_folder_directory=self.handler_files.getTempFolderDirectory(),
                                                    count=1,
                                                    user_agent=ua)

        # ---------------it is possible that the error returned indicates a vpn error or a 'didn't find entity' error
        # ---------------The vpn error will be dealt with later, the 'didn't find entity' error shouldnt happen
        # ---------------but should be accounted for late with a popup


        # if != '1' then filings were not found, so the value in start_date is the earliest filing date
        if search_results != '1':
            return start_date
        else:
            self.database.manualConnect()
            self.parseResults(entity=entity_name, filing_type=filing_type)
            self.database.commit()
            res = self.database.getMostRecentFilingDateForFilingType(entity_name, filing_type_string)
            self.database.close()
            return res[0][0]

    # the date parameters are passed over as strings of dateTime objects or are "" if not being used
    def searchForFiling(self, institute, filing_type, start_date, end_date):
        self.found_entity = False
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
        print('searched for filng')
        self.database.manualConnect()
        ua = self.database.getSecID()
        print(ua)
        self.database.close()
        ua = f"{ua[0][0]} ({ua[0][1]})"
        result = self.downloader.searchForInstitute(institute,
                                                    filing_type,
                                                    start_date_int,
                                                    end_date_int,
                                                    self.handler_files.getTempFolderDirectory(),
                                                    count=100,
                                                    user_agent=ua)
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


    def openFilings(self, filings, toplevel):
        FilingViewer(filings, toplevel)
        return

    def isSecIdSet(self):
        """
        :return: true if SEC ID is set
        """
        self.database.manualConnect()
        res = self.database.getSecID()
        self.database.close()
        return len(res) > 0

    def checkForNewTrackedFilings(self, original_strings, filing_dict):
        # original strings are in the following format
        #      Entity Name          |       Filing Type      |      Last file Date'
        self.database.manualConnect()
        new_strings = ['     Entity Name          |       Filing Type      |      Last file Date']
        for tracked_string in original_strings:
            split_tracked = tracked_string.split('|')
            filing_type = 'FILING_' + split_tracked[1].strip()
            new_last_file_date = self.getMostRecentFilingDate_search(entity_name=split_tracked[0].strip(),
                                                                     filing_type=filing_dict[filing_type])
            new_last_file_date = datetime.strptime(new_last_file_date, '%Y-%m-%d')
            current_last_file_date = datetime.strptime(split_tracked[2].strip(), '%d %B %Y')

            if new_last_file_date > current_last_file_date:
                temp_string = f"(NEW FILING)\t{split_tracked[0]}\t|{split_tracked[1]}|\t{new_last_file_date.strftime('%d %B %Y')}"
                new_strings.append(temp_string)
                entity_id = self.database.getEntityIDFromName(split_tracked[0].strip())
                self.database.updateTrackedLastFileDate(filing_entity_id=entity_id,
                                                        filing_type=split_tracked[1].strip(),
                                                        last_file_date=str(new_last_file_date))
                self.database.commit()
            else:
                new_strings.append(tracked_string)
        self.database.close()
        return new_strings

    def trackButtonActions(self, entity_list, filing_type):
        print('tracked button actions')
        print(f'entity list: {entity_list}')
        filing_type_string = str(filing_type)
        filing_type_string = filing_type_string[filing_type_string.find('_') + 1:len(filing_type_string)]
        for entity_name in entity_list:
            # entity_id = self.database.getEntityIDFromName(entity_name)
            # check if being tracked
            last_file_date = self.getMostRecentFilingDate_search(entity_name=entity_name, filing_type=filing_type)
            self.database.manualConnect()
            entity_id = self.database.getEntityIDFromName(entity_name)
            if not self.database.isEntityAndFilingTypeTracked(entity_name, filing_type_string):
                # then insert into the tracked table
                self.database.insertTrackedEntityFiling(filing_entity_id=entity_id, filing_type=filing_type_string, last_file_date=last_file_date)
            else: # the entity is already being tracked,
                self.database.updateTrackedLastFileDate(filing_entity_id=entity_id, filing_type=filing_type_string, last_file_date=last_file_date)

                # get the most recent filing date currently in the database
                # run this to ensure database is up-to-date
        self.database.commit()
        self.database.close()
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
        """
        parses the filings that were downloaded as a result of a search
        any and only files in the temp folder's directory for the given entity and filing_type are parsed
        nothing is returned, and results are stored in the database
        :type filing_type: str
        :type entity: str
        """
        filing_type_getText = str(filing_type)[str(filing_type).find('_')+1:len(str(filing_type))]
        # use the handler_files to get the accession numbers from the file names
        list_of_accession_numbers = self.handler_files.getAccessionNumbers(entity, filing_type)

        # first check if the entity searched for is in the database,
        if self.database.isEntityInDatabase(entity):
            # if the entity is in the database but the IRS number is null then the FilingEntity
            # database entry needs to be completed
            if self.database.getEntityIRSNumber(entity) is None:
                with Parser(self.handler_files.getFileText(list_of_accession_numbers[0], entity, filing_type_getText), filing_type) as p:
                    p.completeFilingEntity(self.database, entity)
            # if the entity is already in the database then check each filing with the accession numbers
            # to find if they need to be parsed or not
        else:
            # else the entity is not in the database then for the first accession number parse the entity
            print(f"gui handler 214: filing type: {filing_type}")
            with Parser(self.handler_files.getFileText(list_of_accession_numbers[0], entity, filing_type_getText), filing_type) as p:
                p.parseFilingAndEntity(self.database)
        # now just get the details from the rest of the filings
        for number in list_of_accession_numbers:
            # check if the accession number is in the database
            if not self.database.isAccessionNumberInDatabase(self.formatAccNumber(number)):
                parser = Parser(self.handler_files.getFileText(number, entity, filing_type_getText), filing_type)
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
        with EdgarDatabase(False) as db:
            db.manualConnect()
            res = db.getTrackedEntities()
        if len(res) < 1:
            return 'None'
        else:
            tracking_strings = ['     Entity Name          |       Filing Type      |      Last file Date']
            for r in res:
                print(r)
                tracking_strings.append(r[0] + '      |     ' + r[1] + '      |     ' + r[2].strftime("%d %B %Y"))
            return tracking_strings

    def clearResultMessage(self):
        self.result_message_list.clear()

    def dateToInt(self, date):
        # the date  is a string in the format of yyyy-mm-dd, with a zero in the first position for single digit numbers (e.g 01).
        string_list = date.split("-")
        int_list = []
        for s in string_list:
            int_list.append(int(s))
        return int_list

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
