import re


class Parser_13f:

    def __intit__(self):
        print("init")

    def scrub(self, text):
        text = re.sub(r'(^[ \t]+|[ \t]+(?=:))', '', text, flags=re.M)
        text = text.strip()
        return text

    def formatDate(self, date_string):
        year = date_string[:4]
        month = date_string[4:6]
        day = date_string[6:]
        formatted_date = year + '-' + month + '-' + day
        return formatted_date

    def formatSignatureDate(self, date_string):
        year = date_string[6:]
        month = date_string[0:2]
        day = date_string[3:5]
        formatted_date = year + '-' + month + '-' + day
        return formatted_date
        return

    def getFilingEntityInfo(self, text):
        filing_detail_search_strings = ['COMPANY CONFORMED NAME:', 'CENTRAL INDEX KEY:', 'IRS NUMBER:']
        start_index = 0
        info_strings = []
        for detail in filing_detail_search_strings:
            start_index = text.find(detail, start_index) + len(detail)
            eol_index = text.find('\n', start_index)
            result_string = text[start_index:eol_index]
            result_string = self.scrub(result_string)
            info_strings.append(result_string)
        start_index = text.find('STATE OF INCORPORATION:', start_index)
        if start_index == -1:
            start_index = text.find('STATE:', 0) + len('STATE:')
        else:
            start_index = start_index + len('STATE OF INCORPORATION:')
        eol_index = text.find('\n', start_index)
        result_string = text[start_index:eol_index]
        result_string = self.scrub(result_string)
        info_strings.append(result_string)
        return info_strings

    # ------------------------------------------------to check if the filng contains holdings or has their holdings reported in a nother filing all you need to do is
    # ------------------------------------check for '<otherMangersInfo>' as this is in 13F filings that are simply to state which filing is reporting for them while the 13f
    # ----------------------------------------filings that report for multiple instituions other than themselves will contain '<otherMangers2Info>'

    def getFilingInfo(self, text):
        filing_detail_search_strings = ['ACCESSION NUMBER:', 'CONFORMED SUBMISSION TYPE:',
                                        'CONFORMED PERIOD OF REPORT:', 'FILED AS OF DATE:',
                                        'DATE AS OF CHANGE:', 'EFFECTIVENESS DATE:', 'SEC FILE NUMBER:']
        start_index = 0
        info_strings = []
        for detail in filing_detail_search_strings:
            start_index = text.find(detail, start_index) + len(detail)
            eol_index = text.find('\n', start_index)
            result_string = text[start_index:eol_index]
            result_string = self.scrub(result_string)
            if 'DATE' or 'PERIOD' in detail:
                result_string = self.formatDate(result_string)
            info_strings.append(result_string)
        # find if the filing is an ammendment and if so which type
        start_index = text.find('isAmendment>', start_index) + len('isAmendment>')
        eoAnswer_index = text.find('<', start_index)
        result_string = text[start_index:eoAnswer_index]
        if result_string == 'true':
            start_index = text.find('amendmentType>', start_index) + len('amendmentType>')
            eoAnswer_index = text.find('<', start_index)
            result_string = text[start_index:eoAnswer_index]
            info_strings.append(result_string)
        else:
            info_strings.append('not')

        start_index = text.find('COMPANY CONFORMED NAME:', 0) + len('COMPANY CONFORMED NAME:')
        eoAnswer_index = text.find('\n', start_index)
        result_string = text[start_index:eoAnswer_index]
        info_strings.append(self.scrub(result_string))
        return info_strings

    def getBusinessAddressInfo(self, text):
        info_strings = []
        start_index = text.find('BUSINESS ADDRESS:')
        detail_strings = ['STREET 1:', 'STREET 2:', 'CITY:', 'STATE:', 'ZIP:', 'BUSINESS PHONE:']
        for detail in detail_strings:
            if 'STREET 2' in detail:
                og_index = start_index
                start_index = text.find(detail, start_index)
                next_index = text.find('CITY:', start_index)
                if (start_index < next_index) and (start_index != -1):
                    eol_index = text.find('\n', start_index)
                    result_string = text[(start_index + len(detail)):eol_index]
                    result_string = self.scrub(result_string)
                    info_strings.append(result_string)
                else:
                    start_index = og_index
                    info_strings.append(None)
            else:
                start_index = text.find(detail, start_index) + len(detail)
                eol_index = text.find('\n', start_index)
                result_string = text[start_index:eol_index]
                result_string = self.scrub(result_string)
                info_strings.append(result_string)
        return info_strings

    def getMailingAddressInfo(self, text):
        info_strings = []
        start_index = text.find('MAIL ADDRESS:')
        detail_strings = ['STREET 1:', 'STREET 2:', 'CITY:', 'STATE:', 'ZIP:']
        for detail in detail_strings:
            if 'STREET 2:' in detail:
                og_index = start_index
                start_index = text.find(detail, start_index)
                next_index = text.find('CITY:', og_index)
                if ((start_index < next_index) and (start_index != -1)):
                    eol_index = text.find('\n', start_index)
                    result_string = text[(start_index + len(detail)):eol_index]
                    result_string = self.scrub(result_string)
                    info_strings.append(result_string)
                else:
                    start_index = og_index
                    info_strings.append(None)
            else:
                start_index = text.find(detail, start_index) + len(detail)
                eol_index = text.find('\n', start_index)
                result_string = text[start_index:eol_index]
                result_string = self.scrub(result_string)
                info_strings.append(result_string)
        return info_strings

    def getFormerNameInfo(self, text):
        info_strings = []
        start_index = text.find('FORMER COMPANY:')
        if start_index < 0:
            return info_strings
        detail_strings = ['NAME:', 'CHANGE:']
        for detail in detail_strings:
            start_index = text.find(detail, start_index) + len(detail)
            eol_index = text.find('\n', start_index)
            result_string = text[start_index:eol_index]
            result_string = self.scrub(result_string)
            info_strings.append(result_string)
        return info_strings

    def getFilingManagerInfo(self, text):
        print("getting filing manager info")
        start_index = 0
        info_strings = []
        detail_strings = ['cik', 'form13FFileNumber', 'name']
        for detail in detail_strings:
            temp_original_start = start_index
            start_index = text.find(detail, start_index)
            eol_index = text.find(detail, start_index + len(detail) + 1) - 2
            if start_index > -1:
                start_index = start_index + len(detail) + 1
                result_string = text[start_index :eol_index]
            else:
                result_string = None
                start_index = temp_original_start
            info_strings.append(result_string)
            print(detail + ", index:" + str(start_index) + " : " + str(result_string))
        return info_strings

    def getOtherManagerInfo(self, text):
        print("getting other manager info")
        list_of_all_managers = []
        start_index = text.find('<summaryPage>')
        detail_strings = ['sequenceNumber', 'cik', 'form13FFileNumber', 'name']
        start_index = text.find('otherIncludedManagersCount', start_index) + len('otherIncludedManagersCount') + 1
        eol_index = text.find('otherIncludedManagersCount', start_index) - 2
        num_of_managers = text[start_index:eol_index]
        num_of_managers = int(num_of_managers)
        # print("number of other managers: " + str(num_of_managers))
        loopcount = 0
        if num_of_managers > 0:
            while start_index > 0:
                loopcount = loopcount + 1
                if loopcount > num_of_managers:
                    break
                manager_info_list = []
                for detail in detail_strings:
                    temp_original_index = start_index
                    start_index = text.find(detail, start_index)
                    if start_index < 0:
                        start_index = temp_original_index
                        manager_info_list.append(None)
                    else:
                        start_index = start_index + len(detail) + 1
                        eol_index = text.find(detail, start_index) - 2
                        result_string = text[start_index:eol_index]
                        result_string = self.scrub(result_string)
                        manager_info_list.append(result_string)
                list_of_all_managers.append(manager_info_list)
                start_index = text.find('<otherManager2', start_index)
        return list_of_all_managers


    def getFilingSignatureBlock(self, text):
        info_strings = []
        start_index = 0
        detail_strings = ['name', 'title', 'phone', 'signature', 'city', 'stateOrCountry', 'signatureDate']
        for detail in detail_strings:
            start_index = text.find(detail, start_index) + len(detail) + 1
            eoAnswer_index = text.find(detail, start_index) - 2
            result_string = text[start_index:eoAnswer_index]
            if 'Date' in detail:
                result_string = self.formatSignatureDate(result_string)
            info_strings.append(result_string)
        return info_strings

    def getInfoTableInfo(self, text):
        info_list = []
        start_index = text.find('summaryPage')
        detail_strings = ['otherIncludedManagersCount', 'tableEntryTotal', 'tableValueTotal']
        do_isCon = False
        for detail in detail_strings:
            start_index = text.find(detail, start_index) + len(detail) + 1
            eoAnswer_index = text.find(detail, start_index) - 2
            result_string = text[start_index:eoAnswer_index]
            if 'otherInclud' in detail:
                if '0' not in result_string:
                    do_isCon = True
                else:
                    do_isCon = False
            info_list.append(result_string)
        if do_isCon:
            detail = 'isConfidentialOmitted'
            start_index = text.find(detail, start_index)
            if start_index < 0:
                info_list.append('false')
            else:
                start_index = start_index + 1 + len(detail)
                eoAnswer_index = text.find(detail, start_index) - 2
                info_list.append(text[start_index:eoAnswer_index])
        else:
            info_list.append('false')
        return info_list

    def getInfoTableData(self, text, num_entries):
        list_of_positions = []
        start_index = text.find('DESCRIPTION')
        detail_strings = ['nameOfIssuer', 'titleOfClass', 'cusip', 'value', 'sshPrnamt', 'sshPrnamtType', 'putCall',
                          'investmentDiscretion', 'otherManager', 'Sole', 'Shared', 'None']
        counter = 0
        while counter < num_entries:
            counter = counter + 1
            position_info_list = []
            for detail in detail_strings:
                if ('putCall' in detail) or ('otherManager' in detail):
                    # store the currnt index
                    og_index = start_index
                    # look for the index of the next putcall/otherManager tag
                    start_index = text.find(detail, start_index)
                    # find the index of the detail after putcall/otherManager

                    next_index = text.find(detail_strings[detail_strings.index(detail) + 1], og_index)
                    # if start_index is less then the current stock posion is a put/call or has an other manager listed
                    if (start_index < next_index) and (start_index != -1):
                        eoAnswer_index = text.find('</', start_index + 1)
                        # the length of the detail needs to be added to the start_index here as the index is at the start f the detail to ensure the above check passes
                        result_string = text[start_index + len(detail) + 1:eoAnswer_index]
                        position_info_list.append(result_string)
                    # else there is no putcall/otherManager data for this stock positon and therefor it is a long positon
                    else:
                        if ('putCall' in detail):
                            position_info_list.append('Long')
                            start_index = og_index
                        else:
                            position_info_list.append('None')
                            start_index = og_index
                else:
                    start_index = text.find(detail, start_index) + len(detail)
                    if start_index == -1:
                        print("start index = -1")
                        print("detail: " + detail + "counter: " + str(counter) + "num entries: " + str(num_entries))
                        break
                    start_index = start_index + 1
                    # find if the line ends with a '<' or a \n
                    eol_index = text.find('\n', start_index)
                    close_index = text.find('</', start_index)
                    if eol_index < close_index:
                        result_string = text[start_index:eol_index]
                    else:
                        result_string = text[start_index:close_index]
                    result_string = self.scrub(result_string)
                    position_info_list.append(result_string)

            list_of_positions.append(position_info_list)

        return list_of_positions
