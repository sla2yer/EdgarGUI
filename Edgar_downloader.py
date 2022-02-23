from secedgar.filings import Filing
#from secedgar.cik_lookup import CIKLookup
from secedgar.exceptions import EDGARQueryError
from datetime import date
import warnings
import platform
# my_filings = Filing(cik_lookup=['SUSQUEHANNA INTERNATIONAL GROUP, LLP'],
#                     filing_type=FilingType.FILING_13F,
#                     count=15,
#                     user_agent='YOUR COMPANY NAME HERE')
#lookups = CIKLookup(['SUSQUEHANNA INTERNATIONAL GROUP'])
#print(len(my_filings))
#print(my_filings)
#urls = my_filings.get_urls()
#print(urls['SUSQUEHANNA INTERNATIONAL GROUP, LLP'])
#print(lookups.tex)
#my_filings.save('/home/pi/EdgarAppTempFolders')

#in the 13f-HR/A document each of the holdings is wraped by <infoTable> and starts with <nameOfIssuer>

class EdgarDownloader:
    def __init__(self):
        self.user_agent = 'jr'
        self.file_system = platform.system()
        
    def searchForInstitute(self, institute, filing_type, start_date, end_date):   #'SUSQUEHANNA INTERNATIONAL GROUP, LLP'
        with warnings.catch_warnings(record=True) as w:
            print("searching with " + institute)
            print("start date: " + str(start_date) + "  end date:" + str(end_date))
            warnings.simplefilter("always")
            try:
                #check if there are dates and and if so do the relevant search
                if len(start_date) == 0 and len(end_date) == 0:
                    my_filings = Filing(cik_lookup=[institute],
                                        filing_type=filing_type,
                                        count=15,
                                        user_agent=self.user_agent)
                   
                
                elif  len(start_date) > 0 and len(end_date)  == 0:
                    my_filings = Filing(cik_lookup=[institute],
                                        filing_type=filing_type,
                                        count=15,
                                        user_agent=self.user_agent,
                                        start_date = date(start_date[0], start_date[1], start_date[2]))
                   
                
                elif  len(start_date) > 0 and len(end_date)  > 0:
                    my_filings = Filing(cik_lookup=[institute],
                                        filing_type=filing_type,
                                        count=15,
                                        start_date = date(start_date[0], start_date[1], start_date[2]),
                                        end_date = date(end_date[0], end_date[1], end_date[2]),
                                        user_agent=self.user_agent)
                   
                    
                elif  len(start_date)  == 0 and len(end_date)  > 0:
                    my_filings = Filing(cik_lookup=[institute],
                                        filing_type=filing_type,
                                        count=15,
                                        end_date = date(end_date[0], end_date[1], end_date[2]),
                                        user_agent=self.user_agent)
                #my_filings.get_urls()
            except (EDGARQueryError):
                return "Error: No results found, please check spelling"
         
         #this is the else to the 'try:' for the section above the 'except:'
            else:
                #if the length of the url list is > 0 there filings were found for the given institute, there may not be filings of the specified type however
                try:
                    if (len(my_filings.get_urls()) > 0):
                        #this will cause an error if executed when there was no result
                        #If there are filings of the specifed type for the given institution
                        if (len(my_filings.get_urls()[institute]) > 0):
                            if("Linux" in self.file_system):
                                my_filings.save('/home/pi/EdgarAppTempFolders')
                            elif("Windows" in self.file_system):
                                my_filings.save('C:\\Users\\rubio\\Documents\\EdgarAppTempFolders')
                            return"1"

                        #else filings were found but not of the specified type
                        else:
                            return w[0].message

                    #else a cik was not find that matched the institute given but there are recomendations
                    else:
                        print('print line 74 ed downloader')
                        return w[0].message
                except(EDGARQueryError):
                    return w[0].message
    
