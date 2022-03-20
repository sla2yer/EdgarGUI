# EdgarGUI
This is still a work in progress. For the app to work the mysql user needs to be made prior to first launch, this won't be necessary in the near future

A multithrreaded GUI for the SEC edgar filing system which stores parsed data in a local SQL database so that the application gets faster with each use. 
The positions held in each filing can then be opened in a seperate window. This seperate window allows for the comparison of positions between any two 13F filings that one company has filed, as well as sorting the positons by value/principle or the percent change of the values. 
For example the change in positions for susquehanna international from the january 2021 filing and the june 2021 filing can be compared, and in the same window the user can easily have the positions from january 2020 and january 2021 displayed and sorted by largest dollar value percent increase.

When finshed this appllication will periodically check for new filing from entities that are specified ('tracked') and then inform the user of the new filing and the biggest changes in the positons.

This application allows for sorting and tracking of positions in a 13F filing by an 'other manager'. sometimes one entity has their positions reported by their parent, 
susquehanna international is an example of such parent as they report for several smaller/child firms. What this means is that if "susquehanna international" reports "susquehanna LLC" positions, and the user has tracked "susquehanna LLC", then when "susquehanna international" files a new 13F filing the user will only get an alert if if the positions in the filing that specifically belong to "susquehanna LLC" have changed since the last filing. 

The SQL database is made with the mariadb mysql python library.

Currently the application only has a parser made for 13F filings.

This is made using the secedgar library to download filings from the the SEC edgar website, the Tkinter python library is used for the GUI
