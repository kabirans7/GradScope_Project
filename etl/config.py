#Configuration
CSV_FILE = "data/2019-23_IT_Jobs.csv"

#Database Details Hidden for Privacy Reasons
DB_NAME = dbname
DB_USER = dbuser
DB_PASSWORD = dbpwd
DB_HOST = dbhost
DB_PORT = dbport

#Star Schema Tables
#Main Table
FACT_JOB_POSTING_TABLE = "FACT_Job_Posting"

#Dimension Tables
DIM_COMPANY_TABLE = "DIM_Company"
DIM_JOB_TITLE_TABLE = "DIM_Job_Title"
DIM_JOB_TYPE_TABLE = "DIM_Job_Type"
DIM_EXPERIENCE_LEVEL_TABLE = "DIM_Experience_Level"
DIM_DATE_POSTED_TABLE = "DIM_Date_Posted"
DIM_LOCATION_TABLE = "DIM_Location"
DIM_INDUSTRY_TABLE = "DIM_Industry"
DIM_SKILL_TABLE = "DIM_Skill"

#Bridge Tables
FACT_JOB_SKILL_TABLE = "FACT_Job_Skill"
FACT_JOB_LOCATION_TABLE = "FACT_Job_Location"
FACT_COMPANY_INDUSTRY_TABLE = "FACT_Company_Industry"
