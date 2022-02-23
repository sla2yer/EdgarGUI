from Edgar_database import EdgarDatabase
from datetime import datetime
from decimal import *
import threading
from threading import Lock
import re


class FilingViewerHandler:
    def __init__(self, filings):
        self.filings = self.parseDetails(filings)
        if len(self.filings) > 1:
            self.sortFilings()
        self.db = EdgarDatabase(False)
        self.result_lines = [[], []]
        self.result_lines_1 = []
        self.result_lines_2 = []
        self.result_lines_3 = []
        self.result_lines_4 = []
        self.result_lines_5 = []
        self.result_lines_6 = []
        self.result_lines_7 = []
        self.result_lines_8 = []
        self.result_lines_9 = []
        self.result_lines_10 = []
        self.result_lines_11 = []
        self.result_lines_12 = []
        self.result_lines_13 = []
        self.result_lines_14 = []
        self.result_lines_15 = []
        self.result_lines_16 = []
        self.result_lines_17 = []
        self.result_lines_18 = []
        self.result_lines_19 = []
        self.result_lines_20 = []

    # If the handler does not have result lines stored in it this function will generate them
    # OTHERWISE this function will simply return the lines from the page given in the parameters
    # parameters = {from date':self.cbox_date_from.get(),  'until date':self.cbox_date_until.get(), 'next page':(-1),  'other manager': self.cbox_other_managers.get(),  'bool only managers':self.bool_other_manager.get(),  'res per page'50}
    def getResults(self, parameters):
        # use parameters['from date'] and self.filings[x][0] (where x=(len(self.filings)-1) is the most recent accession number)
        # to get the Filing_id
        if (len(self.result_lines[0]) == 0):
            # get the indexes of the dates from the self.filings list to be able to send the accession numbers
            date_indexs = self.getFilingListIndexs(parameters['start date'], parameters['end date'])
            print("date indexes " + str(date_indexs))
            print(str(self.filings))
            print("start date: " + str(self.filings[date_indexs[0]][2]) + "end date: " + str(
                self.filings[date_indexs[1]][2]))
            # this will give the cusips (whether its in either one), order here is irrelevant as the results will be sorted
            with EdgarDatabase(False) as db:
                db.manualConnect()
                cusips_first_filing = db.getCusipsInFiling(self.filings[date_indexs[0]][0])
                cusips_second_filings = db.getCusipsInFiling(self.filings[date_indexs[1]][0])
                cusips_both_filings = set(cusips_first_filing).union(set(cusips_second_filings))
                cusips_both_filings = list(cusips_both_filings)
                db.close()
            del cusips_first_filing
            del cusips_second_filings
            num_cusips = len(cusips_both_filings)
            chuncked_cusips = list(self.chunks(list(cusips_both_filings), int((num_cusips / 15) + 1)))

            threads = []

            for i in range(len(chuncked_cusips)):
                threads.append(
                    threading.Thread(target=self.generateResultLines, args=(chuncked_cusips[i], date_indexs)))
                threads[i].start()

            for t in threads:
                t.join()

            self.result_lines[0].extend(self.result_lines_1)
            # print(self.result_lines[0][0])
            self.result_lines[0].extend(self.result_lines_2)
            self.result_lines[0].extend(self.result_lines_3)
            self.result_lines[0].extend(self.result_lines_4)
            self.result_lines[0].extend(self.result_lines_5)
            self.result_lines[0].extend(self.result_lines_6)
            self.result_lines[0].extend(self.result_lines_7)
            self.result_lines[0].extend(self.result_lines_8)
            self.result_lines[0].extend(self.result_lines_9)
            self.result_lines[0].extend(self.result_lines_10)
            self.result_lines[0].extend(self.result_lines_11)
            self.result_lines[0].extend(self.result_lines_12)
            self.result_lines[0].extend(self.result_lines_13)
            self.result_lines[0].extend(self.result_lines_14)
            self.result_lines[0].extend(self.result_lines_15)
            self.result_lines[0].extend(self.result_lines_16)
            self.result_lines[0].extend(self.result_lines_17)
            self.result_lines[0].extend(self.result_lines_18)
            self.result_lines[0].extend(self.result_lines_19)
            self.result_lines[0].extend(self.result_lines_20)
            self.result_lines[0] = list(self.chunks(self.result_lines[0], parameters['res per page']))
            self.sortResults('All', 'alphabetical', False, parameters['res per page'])
            print(len(self.result_lines))
            print(len(self.result_lines[0]))
            print(len(self.result_lines[0][0]))
            print(len(self.result_lines[0][0][0]))
            # print(self.result_lines[0][0][0])
            # for i in range(30):
            #     if len(self.result_lines[0][i]) < 5:
            #         self.result_lines.pop(i)

        return self.result_lines[0][parameters['page']]

    def chunks(self, lst, n):
        for i in range(0, len(lst), n):
            yield lst[i: i + n]

    def deleteExtraResultLines(self):
        del self.result_lines_1
        del self.result_lines_2
        del self.result_lines_3
        del self.result_lines_4
        del self.result_lines_5
        del self.result_lines_6
        del self.result_lines_7
        del self.result_lines_8
        del self.result_lines_9
        del self.result_lines_10
        del self.result_lines_11
        del self.result_lines_12
        del self.result_lines_13
        del self.result_lines_14
        del self.result_lines_15
        del self.result_lines_16
        del self.result_lines_17
        del self.result_lines_18
        del self.result_lines_19
        del self.result_lines_20

    def generateResultLines(self, cusips_both_filings, date_indexs):
        num_cusips = len(cusips_both_filings)
        start_string = 'gen res line cusips. thread:' + str(
            threading.currentThread().getName()) + ', num cusips: ' + str(num_cusips)
        print(start_string)
        x = 1
        for cusip in cusips_both_filings:
            if (x % 20) == 0 and '-10' in threading.currentThread().getName():
                s = str(cusip[0]) + ', ' + str(x) + '/ ' + str(num_cusips) + "  Thread: " + str(
                    threading.currentThread().getName())
                print(s)
            if '-1' in str(threading.currentThread().getName()):
                self.result_lines_1.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-2' in str(threading.currentThread().getName()):
                self.result_lines_2.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-3' in str(threading.currentThread().getName()):
                self.result_lines_3.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-4' in str(threading.currentThread().getName()):
                self.result_lines_4.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-5' in str(threading.currentThread().getName()):
                self.result_lines_5.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-6' in str(threading.currentThread().getName()):
                self.result_lines_6.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-7' in str(threading.currentThread().getName()):
                self.result_lines_7.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-8' in str(threading.currentThread().getName()):
                self.result_lines_8.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-9' in str(threading.currentThread().getName()):
                self.result_lines_9.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-10' in str(threading.currentThread().getName()):
                self.result_lines_10.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                       self.filings[date_indexs[1]][0]))
            elif '-11' in str(threading.currentThread().getName()):
                self.result_lines_11.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-12' in str(threading.currentThread().getName()):
                self.result_lines_12.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-13' in str(threading.currentThread().getName()):
                self.result_lines_13.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-14' in str(threading.currentThread().getName()):
                self.result_lines_14.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-15' in str(threading.currentThread().getName()):
                self.result_lines_15.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-16' in str(threading.currentThread().getName()):
                self.result_lines_16.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-17' in str(threading.currentThread().getName()):
                self.result_lines_17.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-18' in str(threading.currentThread().getName()):
                self.result_lines_18.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-19' in str(threading.currentThread().getName()):
                self.result_lines_19.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                      self.filings[date_indexs[1]][0]))
            elif '-20' in str(threading.currentThread().getName()):
                self.result_lines_20.extend(self.generatePositionLines(cusip[0], self.filings[date_indexs[0]][0],
                                                                    self.filings[date_indexs[1]][0]))

            x = x + 1

    def getFilingListIndexs(self, from_date, until_date):
        x = range(len(self.filings))
        from_index = 0
        until_index = 0
        for f in x:
            if from_date in self.filings[f][2]:
                from_index = f
            if until_date in self.filings[f][2]:
                until_index = f
        print(str([from_index, until_index]))
        return [from_index, until_index]

    def generatePositionLines(self, cusip, acc_num_from, acc_num_until):
        # this method takes a single CUSIP and the gets the put, call, and long holdings from each accession number
        # the first accession number is the earlier holding and the second accession number is the more recent

        # ---------------------INSTEAD OF WHATS HERE---------------------------------
        # Search for any other managers on the given CUSIP as there could be several for any one postion or CUSIP
        # then make the lines for each other manager as postions that are for the same CUSIP but not for the same othermanager can not be summed

        # print("Gen position lines ")

        # for the given CUSIP do search for put, then call, then long positions
        # EXAMPLE first_sets[0] will be all put positions for the given CUSIP from acc_num_1
        # if there are no put positions them the length of first_sets[0] will be 0
        # first_sets[0] = [put1, ... , putn] | n = len(first_sets[0])                                               (y tho)
        # first_sets[0][0] = [issuer name, title of class, value, shrs/prn amount, shrs or pr, put/long/call, filing entity name, sol_va, shared_va, none_va ]
        #                           0               1        2          3               4             5                 6              7      8          9
        # db = EdgarDatabase(False)
        # if '-10' in threading.currentThread().getName():
        #     print("thread 10 generating position line")
        with EdgarDatabase(False) as db:
            db.manualConnect()
            #   other_managers = list(set(db.checkForOtherManagerSeqNums(acc_num_from, cusip)).union(set(db.checkForOtherManagerSeqNums(acc_num_until, cusip))))
            other_managers1 = set(db.checkForOtherManagerSeqNums(acc_num_from, cusip))
            other_managers2 = set(db.checkForOtherManagerSeqNums(acc_num_until, cusip))

            name_and_title = db.getNameAndTitleOfSecurity(cusip, acc_num_from)
            if name_and_title is None:
                name_and_title = db.getNameAndTitleOfSecurity(cusip, acc_num_until)

            other_managers = []
            if 'set' in str(other_managers1):
                set(other_managers2).update(set(other_managers1))
                for i in other_managers2:
                    other_managers.append(i[0])
            else:
                set(other_managers1).update(set(other_managers2))
                for i in other_managers1:
                    other_managers.append(i[0])

            # print("ot 1 \n" + str(other_managers1) + "\not 2\n" + str(other_managers2) + "\not\n" + str(other_managers))
            del other_managers1
            del other_managers2
            if 'None' not in other_managers:
                other_managers.append('None')
            pos_lines = []
            formatted_name = self.formatName(name_and_title[0])
            ftitle = self.formatTitle(name_and_title[1])
            # if '-10' in threading.currentThread().getName():
            #     print("thread 10 formatting position name and title")

            for ot in other_managers:
                # pos_lines.append(self.formatLine('Put ', formatted_name, ftitle, ot, db.getSummedValuesForPosition(acc_num_from, acc_num_until, 'Put', cusip, ot)))
                # pos_lines.append(self.formatLine('Call', formatted_name, ftitle, ot, db.getSummedValuesForPosition(acc_num_from, acc_num_until, 'Call', cusip, ot)))
                # pos_lines.append(self.formatLine('Long', formatted_name, ftitle, ot, db.getSummedValuesForPosition(acc_num_from, acc_num_until, 'Long', cusip, ot)))
                pos_lines.append(self.formatLine('Put ', formatted_name, ftitle, ot, db, acc_num_from, acc_num_until, cusip))
                pos_lines.append(self.formatLine('Call', formatted_name, ftitle, ot, db, acc_num_from, acc_num_until, cusip))
                pos_lines.append(self.formatLine('Long', formatted_name, ftitle, ot, db, acc_num_from, acc_num_until, cusip))

            db.close()
            # if '-10' in threading.currentThread().getName():
            #     print("thread 10 done with the line for " + str(cusip))

        return pos_lines

    def formatLine(self, pos, name, title, ot, db, acc_num_from, acc_num_until, cusip):
        #                       0                           1                           2                                  4                                5
        # summed_values[0] = [  SUM(tf.value), SUM(tf.shares_principle_amount), SUM(tf.sole_voting_authority), SUM(tf.shared_voting_authority), SUM(tf.none_voting_authority),
        #                      SUM(tu.value), SUM(tu.shares_principle_amount), SUM(tu.sole_voting_authority), SUM(tu.shared_voting_authority), SUM(tu.none_voting_authority)
        #                           6                       7                           8                               9                                   10
        # summed_values = db.getSummedValuesForPosition(acc_num_from, acc_num_until, pos, cusip, ot)

        summed_values = db.getSummedValuesForPosition(acc_num_from, acc_num_until, pos, cusip, ot)

        second_summed_value = summed_values[0][6]

        second_summed_shprin = summed_values[0][7]

        if second_summed_value is None:
            second_summed_value = 0
        if second_summed_shprin is None:
            second_summed_shprin = 0

        position_string = name + title + self.formatSummedValue(second_summed_value, self.getPercentChange(second_summed_value, summed_values[0][0])) + \
                          self.formatSummedValue(second_summed_shprin, self.getPercentChange(second_summed_shprin, summed_values[0][1])) + \
                          pos + "  | " + str(ot)
        return position_string

    def formatSummedValue(self, summed_value, percent_change ):
        ts = str(summed_value) + " (" + percent_change + "%)"
        if len(ts) < 20:
            for i in range(20 - len(ts)):
                ts = ts + ' '
        return ts + '|'


    def formatTitle(self, title):
        if len(title) < 19:
            for i in range(20-len(title)):
                title = title + ' '
            return title + '|'
        else:
            return title + '|'

    def getPercentChange(self, second, first):
        if first is None or first == 0:
            return '100'
        if second is None or second == 0:
            return '-100'
        ts = str((((second - first) / first) * Decimal('100.0')))
        return ts[0:ts.find('.') + 3]

    def formatName(self, name):
        self.scrub(name)
        if (len(name) >= 40):
            name = name + "|"
        else:
            for i in range(40 - len(name)):
                name = name + " "
            name = name + "|"
        return name

    def scrub(self, text):
        text = re.sub(r'(^[ \t]+|[ \t]+(?=:))', '', text, flags=re.M)
        return text

    def getPositionNameTitleOtherManager(self, first_sets, second_sets):
        # all sets of put/call/long for a cusip are the same class
        # if there are no put positions them the length of first_sets[0] will be 0
        # first_sets[0] = [put1, ... , putn] | n = len(first_sets[0])                                             (other mgr name)         
        # first_sets[0][0] = [issuer name, title of class, value, shrs/prn amount, shrs or pr, put/long/call,       sol_va,         shared_va, none_va,    filing entity name,] 
        #                           0               1        2          3               4             5                 6              7           8          9
        # first_sets[0][0][0] =  issuer name
        # for each [put, call, long]
        for x in range(3):
            # check if the length is more than 0 for the put/call/long
            # the operation only needs to work once and then returns/breaks
            if len(first_sets[x]) > 0:
                name = first_sets[x][0][0]
                class_title = first_sets[x][0][1]
                if len(first_sets[x]) > 9:
                    other_manager = first_sets[x][0][9]
                else:
                    other_manager = "None"

                return [name, class_title, other_manager]

            elif len(second_sets[x]) > 0:
                name = second_sets[x][0][0]
                class_title = second_sets[x][0][1]
                if len(second_sets[x]) > 9:
                    other_manager = second_sets[x][0][9]
                else:
                    other_manager = "None"
                return [name, class_title, other_manager]

    def getCompanyDetailsString(self):
        self.db.manualConnect()
        details = self.db.getAllFilingEntityDetailsFromAccessionNumber(self.filings[0][0])
        former_name = True
        if (len(details) == 0):
            former_name = False
            details = self.db.getAllFilingEntityDetailsFromAccessionNumberNoFormerName(self.filings[0][0])
        self.db.close()
        detail_string = 'Details about the filings and the filer:\n\n' \
                        'Entitry name:\t\t{name}\n' \
                        'CIK:\t\t\t{cik}\n' \
                        'State of incorperation:\t{state_inc}\n' \
                        'Business Address: {b_addy1},  {b_addy2}, {b_addy3}, {b_addy4}\n' \
                        'Business phone number:\t{b_phone}\n' \
                        'Mailing Address:\t{m_addy1},  {m_addy2}, {m_addy3}, {m_addy4}\n' \
                        'Filing signed off by:\t{sign_1}, {sign_2}\n' \
                        'Phone number:\t\t{p_num}\n' \
                        'Signed in:\t\t{sign_loc_1}, {sign_loc_2}\n' \
                        'Signature date:\t\t{sign_date}\n'.format(name=details[0][0], cik=details[0][1],
                                                                  state_inc=details[0][2], b_addy1=details[0][3],
                                                                  b_addy2=details[0][4], b_addy3=details[0][5],
                                                                  b_addy4=details[0][6], b_phone=details[0][7],
                                                                  m_addy1=details[0][8], m_addy2=details[0][9],
                                                                  m_addy3=details[0][10], m_addy4=details[0][11],
                                                                  sign_1=details[0][12], sign_2=details[0][13],
                                                                  p_num=details[0][14], sign_loc_1=details[0][15],
                                                                  sign_loc_2=details[0][16],
                                                                  sign_date=details[0][17])
        if former_name:
            detail_string = detail_string + '\n\nFormer name:\t\t' + details[0][18]
            detail_string = detail_string + '\nDate of name change:\t' + str(details[0][19])
        else:
            detail_string = detail_string + '\n\nFormer name:\t\tNone'
            detail_string = detail_string + '\nDate of name change:\tNone'
        return detail_string

    def getPageNumberString(self):
        # if next page is -1 then page is 0

        last_page_res_len = len(self.result_lines[0][(len(self.result_lines[0])) - 1])
        num_of_full_res_pages = len(self.result_lines[0]) - 1
        num_of_res = (num_of_full_res_pages * 50) + last_page_res_len

        page_string = " of " + str(len(self.result_lines[0])) + " for " + str(num_of_res) + " results"

        return page_string
        # else the values variable will contain ['cstring' : current_string, 'page_num':page_num]

    def sortResults(self, pcla, sort_by, is_desc, res_per_page):
        print('sorting')
        print(sort_by)
        unchunked = []
        if len(self.result_lines) > 1:
            unchunked.extend(self.result_lines[1])
        for page in self.result_lines[0]:
            unchunked.extend(page)
        # "alphabetical", "shrs/prn amount",  "shrs/prn change", "value", "value change"

        if 'alpha' in sort_by:
            self.result_lines[0] = sorted(unchunked, reverse=is_desc)

        elif 'shrs/prn amount' in sort_by:
            self.result_lines[0] = sorted(unchunked, reverse=is_desc, key=lambda x: x.split('|')[3].split('(')[0])

        elif 'shrs/prn change' in sort_by:
            self.result_lines[0] = sorted(unchunked, reverse=is_desc, key=lambda x: x.split('|')[3].split('(')[1].split('%')[0])
        elif 'value' in sort_by:
            print('sorting value')
            self.result_lines[0] = sorted(unchunked, reverse=is_desc, key=lambda x: x.split('|')[2].split('(')[0])
        elif 'value change' in sort_by:
            self.result_lines[0] = sorted(unchunked, reverse=is_desc, key=lambda x: x.split('|')[3].split('(')[1].split('%')[0])
        del unchunked
        if 'All' not in pcla:
            for line in range(len(self.result_lines[0])):
                if pcla not in self.result_lines[0][line]:
                    self.result_lines[1].append(self.result_lines[0].pop(line))
        self.result_lines[0] = list(self.chunks(self.result_lines[0], res_per_page))

    def sortFilings(self):
        dates = self.getFilingDates()
        dates.sort(key=lambda date: datetime.strptime(date, "%Y-%m-%d"))
        temp = []
        for date in dates:
            for x in range(len(self.filings)):
                if str(date) in self.filings[x][2]:
                    temp.append(self.filings[x])
        print("sorted dates")
        print(str(temp))
        self.filings = temp

    def getFilingAscNumbers(self):
        temp = []
        for f in self.filings:
            temp.append(f[0])
        return temp

    def getFilingDates(self):
        temp = []
        for f in self.filings:
            temp.append(f[2])
        return temp

    def generateResultHeader(self):

        header = self.formatName("name of issuer") + self.formatTitle("class title") + "    value          |  shrs/ prn amount  | p/c/l | Other Manager"
        return header

    def parseDetails(self, filings):
        details = []
        print(filings)
        for f in filings:
            print(f)
            details.append(f.split(" | "))
        print(details)
        return details
