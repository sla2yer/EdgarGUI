import mariadb


# import sys
class EdgarDatabase:
    def __init__(self, clead_db):
        self.con = mariadb.connect(user="edgarUser",
                                   password="ZeEdgarPass",
                                   host="localhost")
        self.cursor = self.con.cursor()
        self.cursor.execute('SET GLOBAL connect_timeout = 10')
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS EdgarDatabase")
        self.cursor.execute("USE EdgarDatabase")
        if clead_db:
            self.dropTables()
            self.createTables()
        self.close()

    def dropTables(self):
        self.cursor.execute("DROP TABLE IF EXISTS TrackedEntityFilings")
        self.cursor.execute("DROP TABLE IF EXISTS FilingSignatureBlock")
        self.cursor.execute("DROP TABLE IF EXISTS FilingOtherManagers")
        self.cursor.execute("DROP TABLE IF EXISTS EntityMailingAddress")
        self.cursor.execute("DROP TABLE IF EXISTS EntityFormerName")
        self.cursor.execute("DROP TABLE IF EXISTS EntityBusinessAddress")
        self.cursor.execute("DROP TABLE IF EXISTS InfoTable13FData")
        self.cursor.execute("DROP TABLE IF EXISTS Security")
        self.cursor.execute("DROP TABLE IF EXISTS InfoTable13F")
        self.cursor.execute("DROP TABLE IF EXISTS Filing")
        self.cursor.execute("DROP TABLE IF EXISTS FilingEntity")
        self.commit()

    def manualConnect(self):
        self.con = mariadb.connect(user="edgarUser",
                                   password="ZeEdgarPass",
                                   host="localhost")
        self.cursor = self.con.cursor()
        self.cursor.execute("USE EdgarDatabase")

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_tb):
        return

    def commit(self):
        self.cursor.execute("COMMIT")

    def close(self):
        self.cursor.close()
        self.con.close()

    def createTables(self):
        sql_list = self.getCreateTableSQL()
        for statement in sql_list:
            self.cursor.execute(statement)
        self.commit()

    def getSummedValuesForPosition(self, acc, pcl, cusip, otm):
        sql = '''SELECT 
                    SUM(tf.value), SUM(tf.shares_principle_amount), SUM(tf.sole_voting_authority), SUM(tf.shared_voting_authority), SUM(tf.none_voting_authority)
                   
                FROM
                    Security, InfoTable13FData AS tf,  InfoTable13F AS tf_info, Filing AS tf_filing
                WHERE
                    (   (tf.infotable_id = tf_info.infotable_id)
                            AND 
                        (tf_info.filing_id = tf_filing.filing_id)
                            AND
                        (tf_filing.accession_number = %(acc)s)
                    )
                AND 
                    
                    (   (tf.cusip = %(cusip)s) 
                            AND
                        (Security.cusip = %(cusip)s)
                    )
                AND
                    (tf.put_long_call = %(pcl)s)               
                AND
                    (tf.other_manager_sequence_numbers = %(otm)s) 

        '''
        self.cursor.execute(sql, {'acc': acc, 'pcl': pcl, 'cusip': cusip, 'otm': otm})
        return self.cursor.fetchall()

    def getInfoTableID(self, filing_id):
        sql = "SELECT infotable_id FROM InfoTable13F WHERE filing_id = %(filing_id)s"
        self.cursor.execute(sql, {'filing_id': filing_id})
        result = self.cursor.fetchone()
        return result[0]

    def getEntityIRSNumber(self, entity):
        sql = "SELECT irs_number FROM FilingEntity WHERE entity_name = %(entity)s"
        self.cursor.execute(sql, {'entity': entity})
        result = self.cursor.fetchone()
        return result[0]

    def getEntityCIK(self, entity):
        sql = "SELECT cik FROM FilingEntity WHERE entity_name = %(entity)s"
        self.cursor.execute(sql, {'entity': entity})
        result = self.cursor.fetchone()
        return result[0]

    def getEntityIDFromName(self, name):
        sql = "SELECT entity_id FROM FilingEntity WHERE entity_name = %(name)s"
        self.cursor.execute(sql, {'name': name})
        result = self.cursor.fetchone()
        return result[0]

    def getEntityIDFromCIK(self, cik):
        sql = "SELECT entity_id FROM FilingEntity WHERE cik = %(cik)s"
        self.cursor.execute(sql, {'cik': str(cik)})
        result = self.cursor.fetchone()
        return result[0]

    def updateFilingEntity(self, entity_id, irs_number, state, cik):
        if cik is None:
            sql = ''' UPDATE FilingEntity SET  irs_number =%(irs_number)s, state_of_incorperation = %(state)s WHERE entity_id=%(entity_id)s'''
            self.cursor.execute(sql, {'irs_number': str(irs_number), 'entity_id': entity_id, 'state': state})
        else:
            sql = ''' UPDATE FilingEntity SET cik = %(cik)s, irs_number =%(irs_number)s, state_of_incorperation = %(state)s WHERE entity_id=%(entity_id)s'''
            self.cursor.execute(sql,
                                {'irs_number': str(irs_number), 'entity_id': entity_id, 'state': state, 'cik': cik})

    def isAccessionNumberInDatabase(self, number):
        sql = "SELECT accession_number FROM Filing WHERE accession_number = %(number)s"
        self.cursor.execute(sql, {'number': str(number)})
        result = self.cursor.fetchone()
        if result is None:
            return False
        else:
            return True

    def isEntityCIKInDatabase(self, entity_cik):
        sql = "SELECT entity_id FROM FilingEntity WHERE cik = %(entity_cik)s"
        self.cursor.execute(sql, {'entity_cik': str(entity_cik)})
        result = self.cursor.fetchone()
        if result is None:
            return False
        else:
            return True

    def isEntityInDatabase(self, entity):
        sql = "SELECT entity_id FROM FilingEntity WHERE entity_name = %(entity)s"
        self.cursor.execute(sql, {'entity': entity})
        result = self.cursor.fetchone()
        if result is None:
            return False
        else:
            return True

    def getFiledOnDate(self, acc_num):
        sql = "SELECT filed_as_of_date FROM Filing WHERE accession_number = %(acc_num)s"
        self.cursor.execute(sql, {'acc_num': str(acc_num)})
        result = self.cursor.fetchone()
        return str(result[0])

    def getFilingNumber(self, acc_num):
        print("getting filing number with acc_num: " + str(acc_num))
        sql = "SELECT sec_file_number FROM Filing WHERE accession_number = %(acc_num)s"
        self.cursor.execute(sql, {'acc_num': str(acc_num)})
        result = self.cursor.fetchone()
        return result[0]

    def getFilingID(self, acc_num):
        sql = "SELECT filing_id FROM Filing WHERE accession_number = %(acc_num)s"
        self.cursor.execute(sql, {'acc_num': str(acc_num)})
        result = self.cursor.fetchone()
        return result[0]

    def getInfoTable13FTableEntryTotal(self, infotable_id):
        sql = "SELECT table_entry_total FROM InfoTable13F WHERE infotable_id = %(infotable_id)s"
        self.cursor.execute(sql, {'infotable_id': str(infotable_id)})
        result = self.cursor.fetchone()
        return result[0]

    def getAllFilingEntityDetailsFromAccessionNumber(self, acc_num):
        print(str(acc_num))
        sql = ''' SELECT 
                    FilingEntity.entity_name, FilingEntity.cik, FilingEntity.state_of_incorperation, 
                    EntityBusinessAddress.street_1, EntityBusinessAddress.city, EntityBusinessAddress.state, EntityBusinessAddress.zip, EntityBusinessAddress.business_phone_number,
                    EntityMailingAddress.street_1, EntityMailingAddress.city, EntityMailingAddress.state, EntityMailingAddress.zip,  
                    FilingSignatureBlock.name_of_signer , FilingSignatureBlock.title_of_signer , FilingSignatureBlock.phone_number , FilingSignatureBlock.city , FilingSignatureBlock.state_or_county , FilingSignatureBlock.signature_date,
                    EntityFormerName.former_name, EntityFormerName.date_name_changed
                FROM 
                    Filing, FilingEntity, EntityBusinessAddress, EntityMailingAddress, FilingSignatureBlock, EntityFormerName
                WHERE
                    (Filing.accession_number = %(acc_num)s)
                AND (Filing.filing_entity_id = FilingEntity.entity_id )
                AND (Filing.filing_entity_id = EntityBusinessAddress.filing_entity_id)
                AND (Filing.filing_entity_id = EntityMailingAddress.filing_entity_id)
                AND (Filing.filing_id        = FilingSignatureBlock.filing_id)
                AND (Filing.filing_entity_id = EntityFormerName.entity_id )
        '''
        self.cursor.execute(sql, {'acc_num': acc_num})
        return self.cursor.fetchall()

    def getAllFilingEntityDetailsFromAccessionNumberNoFormerName(self, acc_num):
        print(str(acc_num))
        sql = ''' SELECT 
                    FilingEntity.entity_name, FilingEntity.cik, FilingEntity.state_of_incorperation, 
                    EntityBusinessAddress.street_1, EntityBusinessAddress.city, EntityBusinessAddress.state, EntityBusinessAddress.zip, EntityBusinessAddress.business_phone_number,
                    EntityMailingAddress.street_1, EntityMailingAddress.city, EntityMailingAddress.state, EntityMailingAddress.zip,  
                    FilingSignatureBlock.name_of_signer , FilingSignatureBlock.title_of_signer , FilingSignatureBlock.phone_number , FilingSignatureBlock.city , FilingSignatureBlock.state_or_county , FilingSignatureBlock.signature_date
                    
                FROM 
                    Filing, FilingEntity, EntityBusinessAddress, EntityMailingAddress, FilingSignatureBlock
                WHERE
                    (Filing.accession_number = %(acc_num)s)
                AND (Filing.filing_entity_id = FilingEntity.entity_id )
                AND (Filing.filing_entity_id = EntityBusinessAddress.filing_entity_id)
                AND (Filing.filing_entity_id = EntityMailingAddress.filing_entity_id)
                AND (Filing.filing_id        = FilingSignatureBlock.filing_id)
        '''
        self.cursor.execute(sql, {'acc_num': acc_num})
        return self.cursor.fetchall()

    def getCusipsInEitherFiling(self, acc_num_1, acc_num_2):
        sql = ''' SELECT DISTINCT InfoTable13FData.cusip
                    FROM InfoTable13FData
                    WHERE (InfoTable13FData.infotable_id = (SELECT InfoTable13F.infotable_id 
                                                            FROM InfoTable13F 
                                                            WHERE InfoTable13F.filing_id = (SELECT Filing.filing_id 
                                                                                            FROM Filing 
                                                                                            WHERE (Filing.accession_number =  %(acc_num_1)s ) OR (Filing.accession_number =  %(acc_num_2)s)
                                                                                            )
                                                            ) 
                            ) '''
        self.cursor.execute(sql, {'acc_num_1': acc_num_1, 'acc_num_2': acc_num_2})
        return self.cursor.fetchall()

    def getCusipsInFiling(self, acc_num):
        sql = ''' SELECT DISTINCT InfoTable13FData.cusip
                    FROM InfoTable13FData
                    WHERE (InfoTable13FData.infotable_id = (SELECT InfoTable13F.infotable_id 
                                                            FROM InfoTable13F 
                                                            WHERE InfoTable13F.filing_id = (SELECT Filing.filing_id 
                                                                                            FROM Filing 
                                                                                            WHERE (Filing.accession_number =  %(acc_num)s )
                                                                                            )
                                                            ) 
                            ) '''
        self.cursor.execute(sql, {'acc_num': acc_num})
        return self.cursor.fetchall()

    def checkForOtherManagerSeqNums(self, acc_num, cusip):
        sql = '''SELECT DISTINCT
                    InfoTable13FData.other_manager_sequence_numbers
                FROM
                    InfoTable13FData, FilingEntity, FilingOtherManagers, Filing, InfoTable13F
                WHERE
                        (InfoTable13FData.infotable_id =  InfoTable13F.infotable_id)
                    AND 
                        (InfoTable13F.filing_id = Filing.filing_id)
                    AND 
                        (Filing.accession_number = %(acc_num)s)
                    AND 
                        (InfoTable13FData.cusip = %(cusip)s)
                '''
        self.cursor.execute(sql, {'acc_num': acc_num, 'cusip': cusip})
        return self.cursor.fetchall()

    def checkForOtherManager(self, acc_num):

        sql = '''
        select  FilingEntity.entity_name 
        from FilingEntity, FilingOtherManagers, Filing 
        where (FilingOtherManagers.manager_entity_id = FilingEntity.entity_id) 
        and (FilingOtherManagers.filing_id = Filing.filing_id) 
        and (Filing.accession_number = %(acc_num)s);
        
        '''
        sql2 = '''SELECT 
                    FilingEntity.entity_name 
                FROM
                    FilingEntity, FilingOtherManagers, Filing
                WHERE
                
                    
                    (FilingEntity.entity_id = FilingOtherManagers.manager_entity_id ) 
                    AND 
                    (FilingOtherManagers.filing_id =  Filing.filing_id)
                    AND 
                    (Filing.accession_number = %(acc_num)s)'''
        self.cursor.execute(sql, {'acc_num': acc_num})
        return self.cursor.fetchall()

    def getPositionValueSum(self, cusip, acc_num, put_call_long, other_manager):
        sql = ''' SELECT    
                                SUM(InfoTable13FData.value)
                            FROM 
                                InfoTable13FData, Security, FilingEntity, FilingOtherManagers, Filing
                            WHERE 
                                (InfoTable13FData.infotable_id = (  SELECT 
                                                                        InfoTable13F.infotable_id 
                                                                    FROM 
                                                                        InfoTable13F 
                                                                    WHERE 
                                                                        InfoTable13F.filing_id =( SELECT 
                                                                                                        Filing.filing_id 
                                                                                                    FROM 
                                                                                                        Filing 
                                                                                                    WHERE 
                                                                                                        (Filing.accession_number =  %(acc_num_1)s )
                                                                                                    
                                                                                                )
                                                                ) 
                                ) 
                            AND ( InfoTable13FData.cusip = %(cusip_var)s )
                            AND ( InfoTable13FData.put_long_call = %(PCL)s)
                            AND (  InfoTable13FData.other_manager_sequence_numbers = %(other_manager)s)
                            '''
        # AND ( FilingEntity.entity_id = FilingOtherManagers.manager_entity_id )
        self.cursor.execute(sql, {'acc_num_1': acc_num, 'cusip_var': str(cusip), 'PCL': put_call_long,
                                  'other_manager': str(other_manager)})
        return self.cursor.fetchall()

    def getNameAndTitleOfSecurity(self, cusip, acc_num):
        sql = '''SELECT
                    name_of_issuer, title_of_class 
                 FROM 
                    Security
                 WHERE
                    (Security.cusip = %(cusip_var)s)'''

        self.cursor.execute(sql, {'cusip_var': str(cusip)})
        return self.cursor.fetchone()

    def getPositionDetails(self, cusip, acc_num, put_call_long, other_manager):
        sql = ''' SELECT    
                        Security.name_of_issuer, Security.title_of_class, InfoTable13FData.value, InfoTable13FData.shares_principle_amount, InfoTable13FData.shares_or_principle, 
                        InfoTable13FData.put_long_call, InfoTable13FData.sole_voting_authority, InfoTable13FData.shared_voting_authority, InfoTable13FData.none_voting_authority,
                        InfoTable13FData.other_manager_sequence_numbers
                    FROM 
                        InfoTable13FData, Security, FilingEntity, FilingOtherManagers
                    WHERE 
                        (InfoTable13FData.infotable_id = (  SELECT 
                                                                InfoTable13F.infotable_id 
                                                            FROM 
                                                                InfoTable13F 
                                                            WHERE 
                                                                InfoTable13F.filing_id =( SELECT 
                                                                                                Filing.filing_id 
                                                                                            FROM 
                                                                                                Filing 
                                                                                            WHERE 
                                                                                                (Filing.accession_number =  %(acc_num_1)s ) 
                                                                                        )
                                                        ) 
                        ) 
                    AND ( Security.cusip = %(cusip_var)s )
                    AND ( Security.cusip = InfoTable13FData.cusip )
                    AND ( InfoTable13FData.put_long_call = %(PCL)s)
                    AND ( FilingEntity.entity_id = FilingOtherManagers.manager_entity_id )
                    AND (  InfoTable13FData.other_manager_sequence_numbers = %(other_manager)s)
                    '''
        self.cursor.execute(sql, {'acc_num_1': acc_num, 'cusip_var': str(cusip), 'PCL': put_call_long,
                                  'other_manager': str(other_manager)})
        return self.cursor.fetchall()

    def getPositionDetailsNoOtherManager(self, cusip, acc_num, put_call_long):
        sql = ''' SELECT    
                        Security.name_of_issuer, Security.title_of_class, InfoTable13FData.value, InfoTable13FData.shares_principle_amount, InfoTable13FData.shares_or_principle, 
                        InfoTable13FData.put_long_call, InfoTable13FData.sole_voting_authority, InfoTable13FData.shared_voting_authority, InfoTable13FData.none_voting_authority
                    FROM 
                        InfoTable13FData, Security, FilingEntity
                    WHERE 
                        (InfoTable13FData.infotable_id =(   SELECT 
                                                                InfoTable13F.infotable_id 
                                                            FROM 
                                                                InfoTable13F 
                                                            WHERE 
                                                                InfoTable13F.filing_id =( SELECT 
                                                                                                Filing.filing_id 
                                                                                            FROM 
                                                                                                Filing 
                                                                                            WHERE 
                                                                                                (Filing.accession_number = %(acc_num_1)s ) 
                                                                                        )
                                                        ) 
                        ) 
                    AND ( Security.cusip = %(cusip_var)s )
                    AND ( Security.cusip = InfoTable13FData.cusip )
                    AND ( InfoTable13FData.put_long_call = %(PCL)s)
              '''
        self.cursor.execute(sql, {'acc_num_1': acc_num, 'cusip_var': str(cusip), 'PCL': put_call_long})
        return self.cursor.fetchall()

    def getSecondOnlyCusips(self, acc_num):
        sql = '''   SELECT DISTINCT cusip 
                    FROM InfoTable13FData 
                    WHERE infotable_id =   (SELECT infotable_id 
                                            FROM InfoTable13F 
                                            WHERE filing_id =  (SELECT filing_id 
                                                                FROM Filing 
                                                                WHERE accession_number = %(acc_num)s
                                                                )
                                            ) 
            '''
        self.cursor.execute(sql, {'acc_num': acc_num})
        return self.cursor.fetchall()

    def getPositionShprin(self, cusip, acc_num, put_call_long, other_manager):
        sql = ''' SELECT    
                                        SUM(InfoTable13FData.shares_principle_amount)
                                    FROM 
                                        InfoTable13FData, Security, FilingEntity, FilingOtherManagers
                                    WHERE 
                                        (InfoTable13FData.infotable_id = (  SELECT 
                                                                                InfoTable13F.infotable_id 
                                                                            FROM 
                                                                                InfoTable13F 
                                                                            WHERE 
                                                                                InfoTable13F.filing_id =( SELECT 
                                                                                                                Filing.filing_id 
                                                                                                            FROM 
                                                                                                                Filing 
                                                                                                            WHERE 
                                                                                                                (Filing.accession_number =  %(acc_num_1)s ) 
                                                                                                        )
                                                                        ) 
                                        ) 
                                    AND ( InfoTable13FData.cusip = %(cusip_var)s )
                                    AND ( InfoTable13FData.put_long_call = %(PCL)s)
                                    AND ( FilingEntity.entity_id = FilingOtherManagers.manager_entity_id )
                                    AND (  InfoTable13FData.other_manager_sequence_numbers = %(other_manager)s)
                                    '''
        self.cursor.execute(sql, {'acc_num_1': acc_num, 'cusip_var': str(cusip), 'PCL': put_call_long,
                                  'other_manager': str(other_manager)})
        return self.cursor.fetchall()

    def isFilingReportingHoldings(self, acc_num):
        sql = "SELECT is_reported_by_another_manager FROM Filing WHERE accession_number = %(acc_num)s"
        self.cursor.execute(sql, {'acc_num': str(acc_num)})
        result = self.cursor.fetchone()
        if len(result) > 0:
            if result[0] is True:
                return False
            else:
                return True

    def insertFilingEntity(self, data):
        print(f'insert filing entity---------------------{data}')
        sql = ''' INSERT INTO FilingEntity(
                    entity_name, cik, irs_number, state_of_incorperation)
                    VALUES (  %(entity_name)s,  %(cik)s,  %(irs_number)s,  %(state_of_incorperation)s);  '''
        self.cursor.execute(sql, {'entity_name': data[0], 'cik': str(data[1]), 'irs_number': data[2],
                                  'state_of_incorperation': data[3]})
        self.commit()

    def insertFiling(self, entity_id, data, is_reported_by_another_manager):
        sql = ''' INSERT INTO Filing( filing_entity_id, accession_number, form_type, sec_file_number, period_of_report, filed_as_of_date, date_as_of_change, effectiveness_date, is_amendment, amendment_type, is_reported_by_another_manager)
                    VALUES (  %(filing_entity_id)s,  %(accession_number)s,  %(form_type)s,  %(sec_file_number)s,  %(period_of_report)s,  %(filed_as_of_date)s,  %(date_as_of_change)s,  %(effectiveness_date)s,  %(is_amendment)s,  %(amendment_type)s, %(is_reported_by_another_manager)s)  '''
        if "not" in data[7]:
            is_amend = False
        else:
            is_amend = True
        self.cursor.execute(sql, {'filing_entity_id': entity_id, 'accession_number': str(data[0]), 'form_type': data[1],
                                  'sec_file_number': data[6], 'period_of_report': data[2], 'filed_as_of_date': data[3],
                                  'date_as_of_change': data[4], 'effectiveness_date': data[5], 'is_amendment': is_amend,
                                  'amendment_type': data[7],
                                  'is_reported_by_another_manager': is_reported_by_another_manager})
        self.commit()

    def insertInfoTable13F(self, filing_id, data):
        print("insert info table 13F")
        print("data ", end="")
        print(data)
        sql = ''' INSERT INTO InfoTable13F(
                    filing_id, other_managers, table_entry_total, table_value_total, is_confidential_omitted)
                    VALUES ( %(filing_id)s,  %(other_managers)s,  %(table_entry_total)s,  %(table_value_total)s,  %(is_confidential_omitted)s)  '''
        self.cursor.execute(sql, {'filing_id': filing_id, 'other_managers': data[0], 'table_entry_total': data[1],
                                  'table_value_total': data[2], 'is_confidential_omitted': data[3]})

    def insertInfoTable13FData(self, infotable_id, data):
        #        print("cusip:" + str(data[2]))
        sql = '''  INSERT INTO InfoTable13FData(
                    infotable_id, cusip, value, shares_principle_amount, shares_or_principle, put_long_call, investment_discretion, other_manager_sequence_numbers, sole_voting_authority, shared_voting_authority, none_voting_authority)
                    VALUES ( %(infotable_id)s,  %(cusip)s,  %(value)s,  %(shares_principle_amount)s,  %(shares_or_principle)s,  %(put_long_call)s,  %(investment_discretion)s,  %(other_manager_sequence_numbers)s,  %(sole_voting_authority)s,  %(shared_voting_authority)s,  %(none_voting_authority)s) '''
        self.cursor.execute(sql, {'infotable_id': infotable_id, 'cusip': str(data[2]), 'value': data[3],
                                  'shares_principle_amount': data[4], 'shares_or_principle': data[5],
                                  'put_long_call': data[6], 'investment_discretion': data[7],
                                  'other_manager_sequence_numbers': data[8], 'sole_voting_authority': data[9],
                                  'shared_voting_authority': data[10], 'none_voting_authority': data[11]})

    def insertSecurity(self, data):
        sql = ''' INSERT INTO Security(
                cusip, name_of_issuer, title_of_class)
                VALUES ( %(cusip)s, %(name_of_issuer)s,  %(title_of_class)s
                )'''
        self.cursor.execute(sql, {'cusip': str(data[0]), 'name_of_issuer': data[1], 'title_of_class': data[2]})

    def isSecurityInDatabase(self, cusip):
        sql = ''' SELECT name_of_issuer FROM Security WHERE cusip = %(cusip)s '''
        self.cursor.execute(sql, {'cusip': str(cusip)})
        result = self.cursor.fetchone()
        if result is None:
            return False
        else:
            return True

    def getSecurityInfo(self, cusip):
        sql = ''' SELECT name_of_issuer FROM Security WHERE cusip = %(cusip)s '''
        self.cursor.execute(sql, {'cusip': str(cusip)})
        result = self.cursor.fetchall()
        return result

    def insertEntityBusinessAddress(self, entity_id, data):
        sql = '''INSERT INTO EntityBusinessAddress(
                    filing_entity_id, street_1, street_2, city, state, zip, business_phone_number)
                    VALUES ( %(filing_entity_id)s,  %(street_1)s,  %(street_2)s,  %(city)s,  %(state)s,  %(zip)s,  %(business_phone_number)s)  '''
        self.cursor.execute(sql,
                            {'filing_entity_id': entity_id, 'street_1': data[0], 'street_2': data[1], 'city': data[2],
                             'state': data[3], 'zip': data[4], 'business_phone_number': data[5]})

    def insertEntityMailingAddress(self, entity_id, data):
        sql = '''INSERT INTO EntityMailingAddress(
                    filing_entity_id, street_1, street_2, city, state, zip)
                    VALUES ( %(filing_entity_id)s,  %(street_1)s, %(street_2)s, %(city)s,  %(state)s,  %(zip)s);  '''
        self.cursor.execute(sql,
                            {'filing_entity_id': entity_id, 'street_1': data[0], 'street_2': data[1], 'city': data[2],
                             'state': data[3], 'zip': data[4]})

    def insertEntityFormerName(self, entity_id, data):
        sql = ''' INSERT INTO EntityFormerName(
                    entity_id, former_name, date_name_changed)
                    VALUES ( %(entity_id)s,  %(former_name)s,  %(date_name_changed)s) '''
        self.cursor.execute(sql, {'entity_id': entity_id, 'former_name': data[0], 'date_name_changed': data[1]})

    def insertFilingOtherManagers(self, data):
        print(f'inserting filing other managers with :  {data} ')
        sql = ''' INSERT INTO FilingOtherManagers(
                    filing_id, manager_entity_id, sequence_number)
                    VALUES ( %(filing_id)s,   %(manager_entity_id)s, %(sequence_number)s)   '''
        self.cursor.execute(sql, {'filing_id': data[0], 'manager_entity_id': data[1], 'sequence_number': data[2]})

    def insertFilingSignatureBlock(self, filing_id, data):
        sql = '''INSERT INTO FilingSignatureBlock(
                    filing_id, name_of_signer, title_of_signer, phone_number, signature, city, state_or_county, signature_date)
                    VALUES ( %(filing_id)s,   %(name_of_signer)s,   %(title_of_signer)s,   %(phone_number)s,   %(signature)s,   %(city)s,   %(state_or_county)s,   %(signature_date)s) '''
        print('sig data')
        print(data)
        self.cursor.execute(sql, {'filing_id': filing_id, 'name_of_signer': data[0], 'title_of_signer': data[1],
                                  'phone_number': data[2], 'signature': data[3], 'city': data[4],
                                  'state_or_county': data[5], 'signature_date': data[6]})

    def getCreateTableSQL(self):
        statements = []
        statements.append('''CREATE TABLE IF NOT EXISTS FilingEntity(
                                            entity_id INT NOT NULL AUTO_INCREMENT,
                                            entity_name VARCHAR(80)   NOT NULL,
                                            cik VARCHAR(20)   NOT NULL,
                                            irs_number VARCHAR(20),
                                            state_of_incorperation VARCHAR(5),
                                            PRIMARY KEY (entity_id)
                                            )''')

        statements.append(''' CREATE TABLE IF NOT EXISTS Filing(
                                                filing_id INT NOT NULL AUTO_INCREMENT, 
                                                filing_entity_id INT NOT NULL,
                                                accession_number VARCHAR(25)   NOT NULL,
                                                form_type VARCHAR(10)   NOT NULL,
                                                sec_file_number VARCHAR(14)   NOT NULL,
                                                period_of_report date NOT NULL,
                                                filed_as_of_date date NOT NULL,
                                                date_as_of_change date NOT NULL,
                                                effectiveness_date date NOT NULL,
                                                is_amendment boolean NOT NULL,
                                                amendment_type VARCHAR(15),
                                                is_reported_by_another_manager boolean NOT NULL,
                                                PRIMARY KEY (filing_id),
                                                FOREIGN KEY (filing_entity_id) REFERENCES FilingEntity (entity_id)
                                                )''')
        statements.append(''' CREATE TABLE IF NOT EXISTS InfoTable13F(  
                                                infotable_id INT NOT NULL AUTO_INCREMENT,
                                                filing_id INT NOT NULL,
                                                other_managers INT NOT NULL,
                                                table_entry_total BIGINT NOT NULL,
                                                table_value_total BIGINT NOT NULL,
                                                is_confidential_omitted VARCHAR(5) NOT NULL,
                                                PRIMARY KEY (infotable_id),
                                                FOREIGN KEY (filing_id) REFERENCES Filing (filing_id)
                                            )''')
        statements.append('''CREATE TABLE IF NOT EXISTS Security(
                                            cusip VARCHAR(9) NOT NULL,
                                            name_of_issuer VARCHAR(40)   NOT NULL,
                                            title_of_class VARCHAR(40)   NOT NULL,
                                            PRIMARY KEY (cusip)
                                        )''')
        statements.append(''' CREATE TABLE IF NOT EXISTS InfoTable13FData
                                            (
                                                share_issue_id INT NOT NULL AUTO_INCREMENT,
                                                infotable_id INT NOT NULL,
                                                cusip VARCHAR(9) NOT NULL,
                                                value BIGINT NOT NULL,
                                                shares_principle_amount BIGINT NOT NULL,
                                                shares_or_principle VARCHAR(4)   NOT NULL,
                                                put_long_call VARCHAR(4)   NOT NULL,
                                                investment_discretion VARCHAR(10)   NOT NULL,
                                                other_manager_sequence_numbers VARCHAR(10),
                                                sole_voting_authority BIGINT NOT NULL,
                                                shared_voting_authority BIGINT NOT NULL,
                                                none_voting_authority BIGINT NOT NULL,
                                                PRIMARY KEY (share_issue_id),
                                                FOREIGN KEY (infotable_id) REFERENCES InfoTable13F (infotable_id),
                                                FOREIGN KEY (cusip) REFERENCES Security (cusip)
                                            )''')
        statements.append(''' CREATE TABLE IF NOT EXISTS EntityBusinessAddress
                                            ( 
                                                business_address_id INT NOT NULL AUTO_INCREMENT,
                                                filing_entity_id INT NOT NULL,
                                                street_1 VARCHAR(80)   NOT NULL,
                                                street_2 VARCHAR(80) NULL,
                                                city VARCHAR(40)   NOT NULL,
                                                state VARCHAR(2)   NOT NULL,
                                                zip VARCHAR(10)   NOT NULL,
                                                business_phone_number VARCHAR(40)   NOT NULL,
                                                PRIMARY KEY (business_address_id),
                                                FOREIGN KEY (filing_entity_id) REFERENCES FilingEntity (entity_id) 
                                            )''')
        statements.append(''' CREATE TABLE IF NOT EXISTS EntityFormerName
                                            ( 
                                                former_name_id INT NOT NULL AUTO_INCREMENT,
                                                entity_id INT NOT NULL,
                                                former_name VARCHAR(40)   NOT NULL,
                                                date_name_changed date NOT NULL,
                                                PRIMARY KEY (former_name_id),
                                                FOREIGN KEY (entity_id) REFERENCES FilingEntity (entity_id) 
                                            )''')
        statements.append(''' CREATE TABLE IF NOT EXISTS EntityMailingAddress
                                            ( 
                                                mailng_address_id INT NOT NULL AUTO_INCREMENT,
                                                filing_entity_id INT NOT NULL,
                                                street_1 VARCHAR(80) NOT NULL,
                                                street_2 VARCHAR(80) NULL,
                                                city VARCHAR(40)   NOT NULL,
                                                state VARCHAR(2)   NOT NULL,
                                                zip VARCHAR(10)  NOT NULL,
                                                PRIMARY KEY (mailng_address_id),
                                                FOREIGN KEY (filing_entity_id) REFERENCES FilingEntity (entity_id) 
                                            )''')
        statements.append('''CREATE TABLE IF NOT EXISTS FilingOtherManagers
                                            ( 
                                                other_manager_id INT NOT NULL AUTO_INCREMENT,
                                                filing_id INT NOT NULL,
                                                manager_entity_id INT NOT NULL,
                                                sequence_number INT NOT NULL,
                                                PRIMARY KEY (other_manager_id),
                                                FOREIGN KEY (manager_entity_id)  REFERENCES FilingEntity (entity_id), 
                                                FOREIGN KEY (filing_id) REFERENCES Filing(filing_id) 
                                            ) ''')
        statements.append(''' CREATE TABLE IF NOT EXISTS FilingSignatureBlock
                                            (
                                                signature_block_id INT NOT NULL AUTO_INCREMENT,
                                                filing_id INT NOT NULL,
                                                name_of_signer VARCHAR(100)   NOT NULL,
                                                title_of_signer VARCHAR(100)   NOT NULL,
                                                phone_number VARCHAR(20)   NOT NULL,
                                                signature VARCHAR(100)   NOT NULL,
                                                city VARCHAR(100)   NOT NULL,
                                                state_or_county VARCHAR(6)   NOT NULL,
                                                signature_date date NOT NULL,
                                                PRIMARY KEY (signature_block_id),
                                                FOREIGN KEY (filing_id) REFERENCES Filing (filing_id) 
                                            )''')
        statements.append('''CREATE TABLE IF NOT EXISTS TrackedEntityFilings
                                            (
                                                track_id  INT NOT NULL AUTO_INCREMENT,
                                                filing_entity_id INT NOT NULL,
                                                filing_type VARCHAR(10)  NOT NULL, 
                                                last_file_date DATE NOT NULL,  
                                                PRIMARY KEY (track_id),
                                                FOREIGN KEY (filing_entity_id) REFERENCES FilingEntity (entity_id)
                                            )''')
        return statements

    def insertTrackedEntityFiling(self, filing_entity_id, filing_type, last_file_date):
        sql = '''INSERT INTO TrackedEntityFilings(
                    filing_entity_id, filing_type,last_file_date)
                    VALUES ( %(filing_entity_id)s,   %(filing_type)s,   %(last_file_date)s) '''
        self.cursor.execute(sql, {'filing_entity_id': filing_entity_id, 'filing_type': filing_type,
                                  'last_file_date': last_file_date})
