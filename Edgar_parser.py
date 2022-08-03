import threading
import asyncio
from Parser_13F import Parser_13f
from Edgar_downloader import EdgarDownloader
from Edgar_database import EdgarDatabase
from File_manager import FileManager
from secedgar.cik_lookup import CIKLookup
from secedgar.exceptions import EDGARQueryError

class Parser:
    def __init__(self, file_text, filing_type):
        self.text = file_text
        self.filing_type = filing_type

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_tb):
        return

    def insertFilingSignature(self, db, filing_id, parser):
        sig_start = self.text.find("signatureBlock")
        sig_end = self.text.find("signatureBlock", sig_start + 10)
        db.insertFilingSignatureBlock(filing_id, parser.getFilingSignatureBlock(self.text[sig_start:sig_end]))

    def worker(self, name, event_loop):
        asyncio.set_event_loop(event_loop)
        event_loop.run_until_complete(self.lookUpCik(name))

    # use _get_cik_from_html on error---------------------------------
    def lookUpCik(self, name):
        asyncio.set_event_loop(asyncio.new_event_loop())
        downloader = EdgarDownloader()
        db = EdgarDatabase(False)
        db.manualConnect()
        ua = db.getSecID()
        db.close()
        ua = f"{ua[0][0]} ({ua[0][1]})"
        file_manager = FileManager()
        search_results = downloader.searchForInstitute(
            institute=name,
            filing_type=self.filing_type,
            start_date='',
            end_date='',
            temp_folder_directory=file_manager.getTempFolderDirectory(),
            count=1,
            user_agent=ua)

        search_results = str(search_results)
        if ("will be skipped" in search_results):
            # for name in self.formatMatchingCompanies(search_results):
            #     self.result_message_list.append(name)
            print('ERROR:multiple')

        elif ("No results" in search_results):
            print('ERROR:none')

        elif ("Only 0 of" in search_results):
            print('ERROR:noneOfType')

            # ELSE FILINGS WERE FOUND
        else:
            db.manualConnect()
            acc_num = file_manager.getAccessionNumbers(name, str(self.filing_type))
            with Parser(file_manager.getFileText(acc_num[0], name, str(self.filing_type)[str(self.filing_type).find('_')+1:len(str(self.filing_type))]), str(self.filing_type)) as p:
                p.parseFilingAndEntity(db)
                db.commit()
            db.close()
            del db
            del downloader
            del file_manager

        # if 'LIMITED' in name:
        #     name.replace('LIMITED', 'LTD')
        # if "INC." in name:
        #     com_i = name.find(',', -7)
        #     if com_i > -1:
        #         name = name[0:com_i] + name[com_i:]



        # with CIKLookup(name) as cik_lookup:
        #     try:
        #         cik_dic = cik_lookup.get_ciks()
        #         return cik_dic[name]
        #     except EDGARQueryError as e:
        #         print(f"EQE: {str(e)}")
        #
        #         print(f"ERROR parser lookUpCik 404: ,{name},{str(e)}")
        #         return "Error par29"
    def parseFiling(self, db, entity):
        if '13F' in str(self.filing_type):
            parser = Parser_13f()
            filing_data = parser.getFilingInfo(self.text)
            entity = filing_data[len(filing_data) - 1]

            index = self.text.find('otherManagersInfo')
            entity_id = db.getEntityIDFromName(entity)
            # if index is > -1 then there are no positions reported on this filing
            if index > -1:
                # get the filing manager info
                manager_strings = parser.getFilingManagerInfo(self.text[index:])
                # the filing needs to be entered into the database before the manager can be
                # from here grab the filing info and insert into db with the 'is_reposrted_by_another_manager' set to true
                db.insertFiling(entity_id, filing_data, is_reported_by_another_manager=True)
                filing_id = db.getFilingID(filing_data[0])
                self.insertFilingSignature(db, filing_id, parser)
                # sometimes CIK's are not listed for other managers, in this case look them up.

                if manager_strings[0] is None and db.isEntityInDatabase(manager_strings[2]):
                    manager_strings[0] = db.getEntityCIK(manager_strings[2])
                if manager_strings[0] is None:
                    # event_loop = asyncio.new_event_loop()
                    # t = (target=self.worker, args=(manager_strings[2], event_loop,))
                    t = threading.Thread(target=self.lookUpCik, args=(manager_strings[2],))
                    t.start()
                    t.join()
                    db.commit()
                    db.close()
                    db.manualConnect()
                    # event_loop.run_until_complete(self.lookUpCik(manager_strings[2]))
                    manager_strings[0] = db.getEntityCIK(entity)
                # before the manager is inserted a check has to be done to make sure it is in 'FilingEntity'
                if not db.isEntityInDatabase(manager_strings[2]):
                    # use the name and cik to insert into FilingEntity
                    list = [manager_strings[2], manager_strings[0], None, None]
                    db.insertFilingEntity(list)
                    db.commit()

                # now that the reporting manager is in the FilingEntity table get the ID of the filing and the manager
                if manager_strings[0] is None or 'None' in str(manager_strings[1]):
                    db.insertFilingOtherManagers([filing_id, db.getEntityIDFromName(manager_strings[2]), 1])
                else:
                    print(f"-------cik not none:{manager_strings[0]}----------------")
                    db.insertFilingOtherManagers([filing_id, db.getEntityIDFromCIK(manager_strings[0]), 1])
                db.commit()
            else:
                # else this filing reports positions so check for other managers in this filing
                db.insertFiling(entity_id, filing_data, False)
                filing_id = db.getFilingID(filing_data[0])
                self.insertFilingSignature(db, filing_id, parser)
                other_managers = parser.getOtherManagerInfo(self.text)
                if len(other_managers) > 0:
                    for manager in other_managers:
                        if manager[1] is None and db.isEntityInDatabase(manager[3]):
                            manager[1] = db.getEntityCIK(manager[3])
                        if manager[1] is None:
                            # in this function the most recent filing of the 'other manager' is downloaded and parsed
                            # this inserts them into the database in the process
                            # event_loop = asyncio.new_event_loop()
                            # t = threading.Thread(target=self.worker, args=(manager[3], event_loop,))
                            t = threading.Thread(target=self.lookUpCik, args=(manager[3],))
                            t.start()
                            t.join()
                            db.commit()
                            db.close()
                            db.manualConnect()
                            # event_loop.run_until_complete(self.lookUpCik(manager[3]))
                            manager[1] = db.getEntityCIK(manager[3])
                        if not db.isEntityInDatabase(manager[3]):
                             # use the name and cik to insert into FilingEntity
                            db.insertFilingEntity([manager[3], manager[1], None, None])
                        #     # insert()
                        #     # now that the other manager is in the FilingEntity table get the ID of the filing and the manager
                        if manager[1] is None or 'None' in str(manager[1]):
                            db.insertFilingOtherManagers([filing_id, db.getEntityIDFromName(manager[3]), manager[0]])
                        else:
                            print(f"-------cik not none:{manager[1]}----------------")
                            db.insertFilingOtherManagers([filing_id, db.getEntityIDFromCIK(manager[1]), manager[0]])
                        db.commit()
                db.insertInfoTable13F(filing_id, parser.getInfoTableInfo(self.text))
                infotable_id = db.getInfoTableID(filing_id)
                infotable_num_entries = db.getInfoTable13FTableEntryTotal(infotable_id)
                # IF IT ISN'T INSERT IT
                # THEN ONCE CONFIRMED IT IS IN THE DATA BASE THE SHAREISSUE CAN BE INSERTED
                # THE CUSIP ACTS AS THE PRIMARY KEY SO THERE IS NO NEED TO QUERY FROM THE SECURITY TABLE HERE
                for share_issue in parser.getInfoTableData(self.text, infotable_num_entries):
                    self.checkForAndInsertSecurity([share_issue[2], share_issue[0], share_issue[1]], db)
                    db.insertInfoTable13FData(infotable_id, share_issue)

    def checkForAndInsertSecurity(self, data, db):
        if db.isSecurityInDatabase(data[0]):
            return
        else:
            db.insertSecurity(data)

    def completeFilingEntity(self, db, entity):
        parser = Parser_13f()
        entity_id = db.getEntityIDFromName(entity)
        entity_info = parser.getFilingEntityInfo(self.text)
        db.updateFilingEntity(entity_id, cik=entity_info[1], irs_number=entity_info[2], state=entity_info[3])
        db.insertEntityBusinessAddress(entity_id, parser.getBusinessAddressInfo(self.text))
        db.insertEntityMailingAddress(entity_id, parser.getMailingAddressInfo(self.text))
        former_name_info = parser.getFormerNameInfo(self.text)
        if len(former_name_info) > 0:
            for name_info in former_name_info:
                db.insertEntityFormerName(entity_id, name_info)

    def parseFilingAndEntity(self, db):
        if '13F' in str(self.filing_type):
            parser = Parser_13f()
            # first you need to check if this filing contains any position info or if the positions for this entity are filed by another manager
            # if the parser contains '<otherMangersInfo>' then this is filed by another institute
            # first enter the entity into the database
            entity_info = parser.getFilingEntityInfo(self.text)
            db.insertFilingEntity(entity_info)
            entity_id = db.getEntityIDFromCIK(entity_info[1])
            # then get the other details about the entity and insert them into the database as well
            db.insertEntityBusinessAddress(entity_id, parser.getBusinessAddressInfo(self.text))
            db.insertEntityMailingAddress(entity_id, parser.getMailingAddressInfo(self.text))
            # there could be multiple former names returned so cycle through and send each one to the insert---------------------------
            former_name_info = parser.getFormerNameInfo(self.text)
            if len(former_name_info) > 0:
                for name_info in former_name_info:
                    # first check if the name is already in the db as some entities list duplicate former names
                    if not db.isFormerNameInDb(entity_id, name_info):
                        db.insertEntityFormerName(entity_id, name_info)
            # do this just to pass a bit less uneccesarry data
            filing_data = parser.getFilingInfo(self.text)
            index = self.text.find('otherManagersInfo')
            if index > -1:
                # get the filing manager info
                manager_strings = parser.getFilingManagerInfo(self.text[index:])
                # the filing needs to be entered into the database before the manager can be
                # from here grab the filing info and insert into db with the 'is_reposrted_by_another_manager' set to true
                db.insertFiling(entity_id, filing_data, True)
                filing_id = db.getFilingID(filing_data[0])
                self.insertFilingSignature(db, filing_id, parser)
                # before the manager is inserted a check has to be done to make sure it is in 'FilingEntity'
                if manager_strings[0] is None and db.isEntityInDatabase(manager_strings[2]):
                    manager_strings[0] = db.getEntityCIK(manager_strings[2])

                if manager_strings[0] is None:
                    # event_loop = asyncio.new_event_loop()
                    # t = threading.Thread(target=self.worker, args=(manager_strings[2], event_loop,))
                    t = threading.Thread(target=self.lookUpCik, args=(manager_strings[2],))
                    t.start()
                    t.join()
                    db.commit()
                    db.close()
                    db.manualConnect()
                    # event_loop.run_until_complete(self.lookUpCik(manager_strings[2]))
                    manager_strings[0] = db.getEntityCIK(manager_strings[2])
                if not db.isEntityInDatabase(manager_strings[2]):
                    # use the name and cik to insert into FilingEntity
                    list = [manager_strings[2], manager_strings[0], None, None]
                    db.insertFilingEntity(list)
                    db.commit()

                # now that the reporting manager is in the FilingEntity table get the ID of the filing and the manager
                if manager_strings[0] is None or 'None' in str(manager_strings[0]):
                    db.insertFilingOtherManagers([filing_id, db.getEntityIDFromName(manager_strings[2]), 1])
                else:
                    print(f"-------cik not none:{manager_strings[0]}----------------")
                    db.insertFilingOtherManagers([filing_id, db.getEntityIDFromCIK(manager_strings[0]), 1])
                db.commit()

            else:
                # else this filing reports positions so check for other managers in this filing
                db.insertFiling(entity_id, filing_data, False)
                filing_id = db.getFilingID(filing_data[0])
                self.insertFilingSignature(db, filing_id, parser)
                other_managers = parser.getOtherManagerInfo(self.text)
                if len(other_managers) > 0:
                    for manager in other_managers:
                        # if the cik is none from parsing but the manager is in the db, try to get cik from db
                        if manager[1] is None and db.isEntityInDatabase(manager[3]):
                            manager[1] = db.getEntityCIK(manager[3])
                        # if the cik is still none then parse the most recent filing for that manager to put cik in db
                        if manager[1] is None:
                            print("looking up cik 225 EP")
                            # event_loop = asyncio.new_event_loop()
                            # t = threading.Thread(target=self.worker, args=(manager[3], event_loop,))
                            t = threading.Thread(target=self.lookUpCik, args=(manager[3],))
                            t.start()
                            t.join()
                            db.commit()
                            db.close()
                            db.manualConnect()
                            # event_loop.run_until_complete(self.lookUpCik(manager[3]))
                            # event_loops.append(event_loop)
                            manager[1] = db.getEntityCIK(manager[3])
                        if not db.isEntityInDatabase(manager[3]):
                            print("inserting, not in db 228 EP")
                            # use the name and cik to insert into FilingEntity
                            list = [manager[3], manager[1], None, None]
                            db.insertFilingEntity(list)
                            db.commit()
                        else:
                            print('not inserting, in db, 233 EP')
                            # now that the reporting manager is in the FilingEntity table get the ID of the filing and the manager
                        if manager[1] is None or 'None' in str(manager[1]):
                            db.insertFilingOtherManagers([filing_id, db.getEntityIDFromName(manager[3]), manager[0]])
                        else:
                            print(f"-------cik not none:{manager[1]}----------------")
                            db.insertFilingOtherManagers([filing_id, db.getEntityIDFromCIK(manager[1]), manager[0]])
                        db.commit()
                db.insertInfoTable13F(filing_id, parser.getInfoTableInfo(self.text))
                db.commit()
                infotable_id = db.getInfoTableID(filing_id)
                infotable_num_entries = db.getInfoTable13FTableEntryTotal(infotable_id)
                for share_issue in parser.getInfoTableData(self.text, infotable_num_entries):
                    self.checkForAndInsertSecurity([share_issue[2], share_issue[0], share_issue[1]], db)
                    db.insertInfoTable13FData(infotable_id, share_issue)
                db.commit()
