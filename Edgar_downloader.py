from secedgar.filings import Filing
from secedgar.exceptions import EDGARQueryError
from datetime import date
import warnings
import platform


class EdgarDownloader:
    def __init__(self):
        self.user_agent = 'jr'
        self.file_system = platform.system()

    def searchForInstitute(self, institute, filing_type, start_date, end_date, temp_folder_directory, count, user_agent):   #'SUSQUEHANNA INTERNATIONAL GROUP, LLP'
        """
        Searches for filings based on the given parameters
        :returns '1' if filings were found and saved, otherwise the error message

        """
        print(f'searched filing type:{filing_type}')
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                #check if there are dates and and if so do the relevant search
                if len(start_date) == 0 and len(end_date) == 0:
                    my_filings = Filing(cik_lookup=[institute],
                                        filing_type=filing_type,
                                        count=count,
                                        user_agent=user_agent)
                   
                
                elif  len(start_date) > 0 and len(end_date)  == 0:
                    my_filings = Filing(cik_lookup=[institute],
                                        filing_type=filing_type,
                                        count=count,
                                        user_agent=user_agent,
                                        start_date=date(start_date[0], start_date[1], start_date[2]))
                   
                
                elif  len(start_date) > 0 and len(end_date)  > 0:
                    my_filings = Filing(cik_lookup=[institute],
                                        filing_type=filing_type,
                                        count=count,
                                        start_date=date(start_date[0], start_date[1], start_date[2]),
                                        end_date=date(end_date[0], end_date[1], end_date[2]),
                                        user_agent=user_agent)
                   
                    
                elif  len(start_date)  == 0 and len(end_date)  > 0:
                    my_filings = Filing(cik_lookup=[institute],
                                        filing_type=filing_type,
                                        count=count,
                                        end_date=date(end_date[0], end_date[1], end_date[2]),
                                        user_agent=user_agent)
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
                            my_filings.save(temp_folder_directory + '/EdgarAppTempFolders')
                            return "1"

                        #else filings were found but not of the specified type
                        else:
                            return w[0].message

                    #else a cik was not find that matched the institute given but there are recomendations
                    else:
                        return w[0].message
                #else there were no filings found
                except(EDGARQueryError):
                    return "Error: No results found, please check spelling"
    
