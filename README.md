
# jbg-ipro-file-etl
Extract Files from J.B Gottstein iPro portal in bulk to your hard drive automatically

**Video Demo**
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/1wgAUTUw4oU/0.jpg)](https://www.youtube.com/watch?v=1wgAUTUw4oU)


**Requirements:** 
You will need Firefox installed on Windows to proceed.  

**Warning:**
This program uses and stores your iPro password in plain-text, please only use on trusted computers. This can be changed but is currently not a feature



**Configuration:**
If you have python you can run the code directly, otherwise download the exe file

Create a config.txt file in the same folder as the exe file that contains the following:

    USERNAME=ross@login.com
    PASSWORD=my ipro password
    DESTINATION_DIRECTORY=G:\final_destination_of_files
    DOWNLOAD_DIRECTORY=C:\Users\Ross\Downloads 

DESTINATION_DIRECTORY will contain the files after running, while DOWNLOAD_DIRECTORY is the default download directory for Firefox, typically in Users/Username/Downloads

Once the exe is run (or scheduled to run in Task Scheduler), Firefox will be opened. The list of files on iPro is compared to the contents of the DESTINATION_DIRECTORY and only files missing are downloaded.

After all files are downloaded, the program will copy them from the DOWNLOAD_DIRECTORY to the DESTINATION_DIRECTORY and remove the download.
