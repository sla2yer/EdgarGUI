from Edgar_database import EdgarDatabase
from datetime import datetime
from decimal import *
import threading
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
            for thread in threads:
                thread.join()
            self.result_lines[0].extend(self.result_lines_1)
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
            self.sortResults('All', 'alphabetical', False, parameters['res per page'], 'All')

        try:
            t = self.result_lines[0][parameters['page'] - 1]
            return t
        except IndexError:
            print(f"INDEX ERROR ---- len res_line = {len(self.result_lines)}")
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
        x = 1
        for cusip in cusips_both_filings:
            if (x % 40) == 0 and '-10' in threading.currentThread().getName():
                print(str(x))
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
        return [from_index, until_index]

    def generatePositionLines(self, cusip, acc_num_from, acc_num_until):
        # this method takes a single CUSIP and the gets the put, call, and long holdings from each accession number
        # the first accession number is the earlier holding and the second accession number is the more recent

        with EdgarDatabase(False) as db:
            db.manualConnect()
            other_managers1 = set(db.checkForOtherManagerSeqNums(acc_num_from, cusip))
            other_managers2 = set(db.checkForOtherManagerSeqNums(acc_num_until, cusip))

            name_and_title = db.getNameAndTitleOfSecurity(cusip, acc_num_from)
            if name_and_title is None:
                name_and_title = db.getNameAndTitleOfSecurity(cusip, acc_num_until)
            if name_and_title is None:
                print(f"ERROR: name_and_title is None\ncusip: {cusip}\nacc_f: {acc_num_from}\nacc_u: {acc_num_until}")
            other_managers = []
            if 'set' in str(other_managers1) and 'set' in str(other_managers2):
                other_managers.append('None')
            elif 'set' in str(other_managers1):
                other_managers2.update(set(other_managers1))
                for i in other_managers2:
                    other_managers.append(i[0])
            else:
                other_managers1.update(set(other_managers2))
                for i in other_managers1:
                    other_managers.append(i[0])

            del other_managers1
            del other_managers2

            pos_lines = []
            if 'CDATA' in name_and_title[0]:
                formatted_name = self.formatName(name_and_title[0][9:-3])
            else:
                formatted_name = self.formatName(name_and_title[0])
            ftitle = self.formatTitle(name_and_title[1])

            for ot in other_managers:
                res = self.formatLine('Put ', formatted_name, ftitle, ot, db, acc_num_from, acc_num_until, cusip)
                if res is not None:
                    pos_lines.append(res)

                res = self.formatLine('Call', formatted_name, ftitle, ot, db, acc_num_from, acc_num_until, cusip)
                if res is not None:
                    pos_lines.append(res)

                res = self.formatLine('Long', formatted_name, ftitle, ot, db, acc_num_from, acc_num_until, cusip)
                if res is not None:
                    pos_lines.append(res)

            db.close()
        return pos_lines

    def formatLine(self, pos, name, title, ot, db, acc_num_from, acc_num_until, cusip):
        #                       0                           1                           2                                  3                                4
        # summed_values[0] = [  SUM(tf.value), SUM(tf.shares_principle_amount), SUM(tf.sole_voting_authority), SUM(tf.shared_voting_authority), SUM(tf.none_voting_authority) ]
        #
        # summed_values = db.getSummedValuesForPosition(acc_num_from, acc_num_until, pos, cusip, ot)

        summed_values_from = db.getSummedValuesForPosition(acc_num_from, pos, cusip, ot)
        summed_values_until = db.getSummedValuesForPosition(acc_num_until, pos, cusip, ot)
        summed_pos_value_until = summed_values_until[0][0]
        summed_pos_shprin_until = summed_values_until[0][1]

        summed_pos_value_from = summed_values_from[0][0]
        summed_pos_shprin_from = summed_values_from[0][1]

        if (summed_pos_value_from is None) and (summed_pos_value_until is None):
            return None

        if summed_pos_value_until is None:
            ot_name = db.getOtherManagerName(acc_num=acc_num_from, ot_seq=ot)
            summed_pos_value_until = 0
        else:
            ot_name = db.getOtherManagerName(acc_num=acc_num_until, ot_seq=ot)
        if summed_pos_shprin_until is None:
            summed_pos_shprin_until = 0
        if summed_pos_value_from is None:
            summed_pos_value_from = 0
        if summed_pos_shprin_from is None:
            summed_pos_shprin_from = 0

        temp_ot_name = ''
        if len(ot_name) == 1:
            if len(ot_name[0]) == 1:
                temp_ot_name = str(ot_name[0][0])
            elif len(ot_name[0]) > 1:
                temp_ot_name = str(ot_name[0])
            else:
                temp_ot_name = str(ot_name)

        position_string = name + title + self.formatSummedValue(summed_pos_value_until,
                                                                self.getPercentChange(summed_pos_value_until,
                                                                                      summed_pos_value_from), True) + \
                          self.formatSummedValue(summed_pos_shprin_until,
                                                 self.getPercentChange(summed_pos_shprin_until, summed_pos_shprin_from),
                                                 False) + \
                          pos + "  | " + temp_ot_name
        return position_string

    def formatSummedValue(self, summed_value, percent_change, is_value):
        number_string = str(summed_value)
        new_string = '0'
        num_front_characters = len(number_string) % 3
        num_of_commas = int((len(number_string) / 3)) - 1
        if len(number_string) > 3 and num_of_commas == 0:
            num_of_commas = 1
        # 58,745
        if len(number_string) < 4:
            new_string = number_string
        else:
            if num_front_characters == 0:
                if num_of_commas > 1:
                    for x in range(num_of_commas):
                        if x < num_of_commas - 1:
                            new_string = number_string[(x * 3):(x * 3) + 3] + \
                                         ',' + \
                                         number_string[(x + 1):((x + 1) * 3) + 3]
                        else:
                            new_string = number_string[(x * 3):(x * 3) + 3]
                else:
                    new_string = number_string[(0 * 3):(0 * 3) + 3] + ',' + number_string[(1 * 3):(1 * 3) + 3]

            else:
                new_string = number_string[0:num_front_characters] + ','
                for x in range(num_of_commas):
                    if x < num_of_commas - 1:
                        new_string = new_string + \
                                     number_string[((x*3) + num_front_characters):((x*3) + num_front_characters) + 3] + \
                                     ',' + \
                                     number_string[(((x + 1) * 3) + num_front_characters):((x + 1) * 3 + num_front_characters)]
                    else:
                        new_string = new_string + number_string[
                                                  ((x * 3) + num_front_characters):((x * 3) + num_front_characters) + 3]
        if is_value:
            new_string = '$' + new_string + ',000'
        ts = new_string + " (" + percent_change + "%)"
        if len(ts) < 25:
            for i in range(25 - len(ts)):
                ts = ts + ' '
        return ts + '|'

    def formatTitle(self, title):
        if len(title) < 19:
            for i in range(20 - len(title)):
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
        details = self.db.getAllFilingEntityDetailsFromAccessionNumberNoFormerName(self.filings[0][0])

        former_name_details = self.db.getFormerNames(self.filings[0][0])
        self.db.close()

        detail_string = 'Details about the filings and the filer:\n\n' \
                        'Entitry name:\t\t{name}\n' \
                        'CIK:\t\t\t{cik}\n' \
                        'State of incorperation:\t{state_inc}\n' \
                        'Business Address:\t\t{b_addy1},  {b_addy2}, {b_addy3}, {b_addy4}\n' \
                        'Business phone number:\t{b_phone}\n' \
                        'Mailing Address:\t\t{m_addy1},  {m_addy2}, {m_addy3}, {m_addy4}\n' \
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
        if len(former_name_details) > 0:
            detail_string = detail_string + '\n\nFormer name:\t\tDate of name change:'
            for former_name in former_name_details:
                detail_string = detail_string + '\n' + former_name[0] + '\t\t' + str(former_name[1])
        else:
            detail_string = detail_string + '\n\nFormer name:\t\tNone'
            detail_string = detail_string + '\nDate of name change:\tNone'
        return detail_string

    def getNumberOfPages(self):
        return len(self.result_lines[0])

    def getPageNumberString(self):
        # if next page is -1 then page is 0

        last_page_res_len = len(self.result_lines[0][(len(self.result_lines[0])) - 1])
        num_of_full_res_pages = len(self.result_lines[0]) - 1
        num_of_res = (num_of_full_res_pages * 50) + last_page_res_len

        page_string = " of " + str(len(self.result_lines[0])) + " for " + str(num_of_res) + " results"

        return page_string
        # else the values variable will contain ['cstring' : current_string, 'page_num':page_num]

    def sortResults(self, pcla, sort_by, is_desc, res_per_page, other_manager):
        unchunked = []
        if len(self.result_lines) > 1:
            unchunked.extend(self.result_lines[1])
        for page in self.result_lines[0]:
            unchunked.extend(page)
        del self.result_lines
        self.result_lines = [[],[]]
        if 'alpha' in sort_by:
            self.result_lines[0] = sorted(unchunked, reverse=is_desc)

        elif 'shrs/prn amount' in sort_by:
            self.result_lines[0] = sorted(unchunked, reverse=is_desc,
                                          key=lambda x: int(''.join(x.split('|')[3].split('(')[0].strip().split(','))))

        elif 'shrs/prn change' in sort_by:
            self.result_lines[0] = sorted(unchunked, reverse=is_desc, key=lambda x: float(
                ''.join(x.split('|')[3].split('(')[1].split('%')[0].split(','))))
        elif 'value change' in sort_by:
            self.result_lines[0] = sorted(unchunked, reverse=is_desc,
                                          key=lambda x: float(x.split('|')[2].split('(')[1].split('%')[0]))
        elif 'value' in sort_by:
            self.result_lines[0] = sorted(unchunked, reverse=is_desc, key=lambda x: int(
                ''.join(x.split('|')[2].split('(')[0].strip().split('$')[1].split(','))))

        del unchunked
        print(other_manager)
        if ('All' not in pcla and 'All' not in other_manager) or ('All' not in pcla or 'All' not in other_manager):
            num_popped = 0
            popped = False
            for line in range(len(self.result_lines[0])):
                if len(self.result_lines[0]) < 1:
                    print("ERROR EFH481 resline len==0")
                if pcla not in self.result_lines[0][line - num_popped] and 'All' not in pcla:
                    print('popped pcla')
                    print(f"popped: {self.result_lines[0][line - num_popped]}")
                    popped = True
                    self.result_lines[1].append(self.result_lines[0].pop(line - num_popped))
                    num_popped = num_popped + 1

                elif other_manager not in self.result_lines[0][line - num_popped] and not popped and 'All' not in other_manager:
                    self.result_lines[1].append(self.result_lines[0].pop(line - num_popped))
                    num_popped = num_popped + 1

                else:
                    print(f"not popped: {self.result_lines[0][line - num_popped]}")
                popped = False
        self.result_lines[0] = list(self.chunks(self.result_lines[0], res_per_page))

    def sortFilings(self):
        dates = self.getFilingDates()
        dates.sort(key=lambda date: datetime.strptime(date, "%Y-%m-%d"))
        temp = []
        for date in dates:
            for x in range(len(self.filings)):
                if str(date) in self.filings[x][2]:
                    temp.append(self.filings[x])
        self.filings = temp

    def searchFilingPositons(self, search_string, res_per_page):
        search_string = search_string.upper()
        print('searching in handler: ' + search_string)
        temp = []
        for page in self.result_lines[0]:
            temp.extend(page)

        # if the code below is not commented then the search function will search all
        # of the positions instead of the current filtration
        #----------------------------------------------------------------------
        # if len(self.result_lines) > 1:
        #     print('res lines len > 1')
        #     temp.extend(self.result_lines[1])
        # del self.result_lines
        self.result_lines[0] = []
        for position_line in temp:
            if search_string in str(position_line).split('|')[0]:
                self.result_lines[0].append(position_line)
            else:
                self.result_lines[1].append(position_line)
        self.result_lines[0] = list(self.chunks(self.result_lines[0], res_per_page))

    def getOtherManagers(self, from_date, until_date):
        with EdgarDatabase(False) as db:
            db.manualConnect()
            date_indexes = self.getFilingListIndexs(from_date=from_date, until_date=until_date)
            names1 = set(db.checkForOtherManager(self.filings[date_indexes[0]][0]))
            names2 = set(db.checkForOtherManager(self.filings[date_indexes[1]][0]))
            if 'set' not in str(names2):
                names2.update(names1)
                temp = ["All"]
                for n in list(names2):
                    temp.append(n[0])
                return temp
            elif 'set' not in str(names1):
                names1.update(names2)
                temp = ["All"]
                for n in list(names1):
                    temp.append(n[0])
                return temp
            else:
                return ['None']

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
        header = self.formatName("name of issuer") + self.formatTitle(
            "class title") + "    value          |  shrs/ prn amount  | p/c/l | Other Manager"
        return header

    def parseDetails(self, filings):
        details = []
        for f in filings:
            details.append(f.split(" | "))
        return details
