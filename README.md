# Cmpe321-Project3
MovieDB System <br />
This tutorial assumes you are in a MacOS environment. Similar procedure applies to Linux/Windows with equivalent commands. <br />

## Install postgresql@14 and run default server
First, one should install and start postgresql in the local environment  <br />
Install postgresql@14 with command: <br />
`$ brew install postgresql@14` <br />
Insert this line to your <b>.zshrc</b> file: <br />
<i>"export PATH="/usr/local/opt/postgresql@14/bin:$PATH" </i>

Make sure the server is started by running: <br />
`$ brew services start postgresql@14` <br />
Then open the database with: <br />
`$ sudo psql -U postgres postgres` <br />

If user postgres does not exist, run: <br />
`$ /usr/local/opt/postgresql@14/bin/createuser -s postgres` <br />
Then open the database. <br />

Then execute `\conninfo`. The result should be: <br />
_"You are connected to database "postgres" as user "postgres" via socket in "/tmp" at port "5432"."_

## Create new database and tables for the app
**WE NOW ASSUME THAT SERVER IS CONNECTED TO THE PORT "5432", IF NOT MODIFY _"port=5432"_ VARIABLE.** <br />
**(All possible files to be modified for this case are the same as in the case you want to change the password.)** <br />
**(The procedures for changing the password are explained below.)** <br />


We use psycopg module in order to connect to postgresql database. <br />
Please check if module is already installed, if not run: <br />
`$ pip3 install psycopg`

<b> If postgresql was installed previously and password for the user "postgres" was set by the user, 
open <b>db.py</b> file and make these changes: <br /> </b>
At lines 4 and 15, modify **_password=<user_password>_** in the **_psycopg.connect()_** function.  
Default is as followed: <br />
_conn = psycopg.connect(host="localhost", port=5432, user="postgres", password="") <br />_
_conn = psycopg.connect(host="localhost", port=5432, user="postgres", password="", dbname="moviedb") <br />_

Also make sure that <b>postgre.sql</b> file is in the same directory with the <b>db.py</b> file 

Finally, to create a new database called "MovieDB" and create the tables, triggers for our schema; run: <br />
`$ python3 db.py`<br /> 

## Import the data to the database
This part assumes that our data would be in the same format as in the Project1. <br />
<b> If postgresql was installed previously and password for the user **"postgres"** was set by the user, 
open <b>read_data.py</b> file and make these changes:</b> <br />
At line 10 modify **_password=<your_password>_** <br />
Default is as followed: <br />
_conn = psycopg.connect(host="127.0.0.1", port="5432", dbname="moviedb", user="postgres", password="")_

Now, in order to import to database run: <br />
`$ python3 read_data.py` 

## Run the Django application

<b>If postgresql was installed previously and password for the user **"postgres"** was set by the user, 
go to the directory "movie_site/movie_site" with the command:</b> <br />
`$ cd movie_site/movie_site` <br /> 
Open the **settings.py** file and modify the password of default database in the DATABASE variable, at line 83. <br />
Default is as followed: <br />
_DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "moviedb",
        "USER": "postgres",
        "PASSWORD": "",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}_ <br />
**(If you modified the password in the "movie_site/movie_site/settings.py" file just go to the outer directory with `$ cd ../..`)**

In order to run the server go to the directory "movie_site/" by command: <br />
`$ cd movie_site` <br /> 
And run the command: <br />
`$ python3 manage.py runserver`

To see the app, open the browser and go to **"http://127.0.0.1:8000/movie_app"** and enjoy.

## Additional Notes
### Storage of the Time in the Database:
Due to a bug in the _read_data.py_ file, time1 column in the occupience_info relation stored as follows:
"time 00:00:00" (e.g. 2023-03-15 00:00:00)
Since we handled this in backend, this **DOES NOT AFFECT UI**. Users can still write input and view output as (e.g. 2023-03-15) whenever needed.

### About View Operations in UI:
For view operations of database manager and director user types, we put all operations into one page for these user types. In the dropdown table (select tag) there exists also string R<operation_number> which refers to requirement <operation_number> from project description. Since two views of audience user type are in separate pages we didn't specify the operation number because the names are explicit enough. Lastly, all other operations are also in separate pages with explicit naming conventions.   

### About ORM (Object Relational Modeling):
A better implementation would include the ORM feature of Django, but we are NOT permitted to use it, according to the project description.


