from Parser_13F import Parser_13f
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

    def lookUpCik(self, name):
        with CIKLookup(name) as cik_lookup:
            try:
                cik_dic = cik_lookup.get_ciks()
                return cik_dic[name]
            except EDGARQueryError:
                return None

    def parseFiling(self, db, entity):
        if '13F' in self.filing_type:
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
                db.insertFiling(entity_id, filing_data, is_reposrted_by_another_manager=True)
                filing_id = db.getFilingID(filing_data[0])
                self.insertFilingSignature(db, filing_id, parser)
                # sometimes CIK's are not listed for other managers, in this case look them up.
                if manager_strings[0] is None:
                    manager_strings[0] = self.lookUpCik(manager_strings[2])
                # before the manager is inserted a check has to be done to make sure it is in 'FilingEntity'
                if db.isEntityInDatabase(manager_strings[2]) == False:
                    # use the name and cik to insert into FilingEntity
                    list = [manager_strings[2], manager_strings[0], None, None]
                    db.insertFilingEntity(list)

                # now that the reporting manager is in the FilingEntity table get the ID of the filing and the manager
                dlist = [filing_id, db.getEntityIDFromCIK(manager_strings[0]), 0]
                db.insertFilingOtherManagers(dlist)

            else:
                # else this filing reports positions so check for other managers in this filing
                db.insertFiling(entity_id, filing_data, False)
                filing_id = db.getFilingID(filing_data[0])
                self.insertFilingSignature(db, filing_id, parser)
                other_managers = parser.getOtherManagerInfo(self.text)
                if len(other_managers) > 0:
                    for manager in other_managers:
                        if manager[1] is None:
                            manager[1] = self.lookUpCik(manager[3])
                        if not db.isEntityInDatabase(manager[3]):
                            # use the name and cik to insert into FilingEntity
                            db.insertFilingEntity([manager[3], manager[1], None, None])
                            # insert()
                            # now that the other manager is in the FilingEntity table get the ID of the filing and the manager
                        db.insertFilingOtherManagers([filing_id, db.getEntityIDFromCIK(manager[1]), manager[0]])
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
            db.insertEntityFormerName(entity_id, former_name_info)

    def parseFilingAndEntity(self, db):
        if '13F' in self.filing_type:
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
            former_name_info = parser.getFormerNameInfo(self.text)
            if len(former_name_info) > 0:
                db.insertEntityFormerName(entity_id, former_name_info)
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
                if not db.isEntityInDatabase(manager_strings[3]):
                    # use the name and cik to insert into FilingEntity
                    list = [manager_strings[2], manager_strings[0], None, None]
                    db.insertFilingEntity(list)

                # now that the reporting manager is in the FilingEntity table get the ID of the filing and the manager
                dlist = [filing_id, db.getEntityIDFromCIK(manager_strings[0]), 0]
                db.insertFilingOtherManagers(dlist)

            else:
                # else this filing reports positions so check for other managers in this filing
                db.insertFiling(entity_id, filing_data, False)
                filing_id = db.getFilingID(filing_data[0])
                self.insertFilingSignature(db, filing_id, parser)
                other_managers = parser.getOtherManagerInfo(self.text)
                if len(other_managers) > 0:
                    for manager in other_managers:
                        if manager[1] is None:
                            manager[1] = self.lookUpCik(manager[3])
                        if not db.isEntityInDatabase(manager[3]):
                            # use the name and cik to insert into FilingEntity
                            list = [manager[3], manager[1], None, None]
                            db.insertFilingEntity(list)
                            # now that the reporting manager is in the FilingEntity table get the ID of the filing and the manager
                        dlist = [filing_id, db.getEntityIDFromCIK(manager[1]), manager[0]]
                        db.insertFilingOtherManagers(dlist)
                db.insertInfoTable13F(filing_id, parser.getInfoTableInfo(self.text))

                infotable_id = db.getInfoTableID(filing_id)
                infotable_num_entries = db.getInfoTable13FTableEntryTotal(infotable_id)
                for share_issue in parser.getInfoTableData(self.text, infotable_num_entries):
                    self.checkForAndInsertSecurity([share_issue[2], share_issue[0], share_issue[1]], db)
                    db.insertInfoTable13FData(infotable_id, share_issue)
