import pandas as pd
import pyodbc
import logging
from time import time
from unicodedata import normalize, combining
from requests import post

class SQLMessagesReader:

    def __init__(self, sql_conn, begin_date, end_date, bot_id, full_information = False):
        self.sql_conn = sql_conn
        self.begin_date = begin_date
        self.end_date = end_date
        self.bot_id = bot_id
        self.full_information = full_information
        self.log_file_name_old = bot_id +'_old.log'
        self.log_file_name_current = bot_id +'_current.log'
        logging.basicConfig(filename = self.log_file_name_old, filemode='w', level=logging.DEBUG,
                           format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        #logging.FileHandler(bot_id + '-debug.log', mode='w')

    def generate_sql_full_select(self):
        self.select = """ SELECT M.[SequentialId] ,M.[Id],M.[InternalId],M.[ContentMediaType],M.[FromIdentity],M.[Metadata],AC.[Email],AC.[Extras]
                              ,CAST(M.[StorageDate] AT TIME ZONE 'E. South America Standard Time' AS NVARCHAR(MAX)) AS MessageDate
              ,CAST(M.[Content] AS NVARCHAR(MAX)) AS Content
            FROM [ArchiveIRIS_MessagingHub].[dbo].[Messages] M """
    
    def generate_sql_select(self):
        self.select = """ SELECT M.[SequentialId] ,M.[FromIdentity],M.[ToIdentity], CAST(M.[StorageDate] AT TIME ZONE 'E. South America Standard Time' AS NVARCHAR(MAX)) AS MessageDate
              ,CAST(M.[Content] AS NVARCHAR(MAX)) AS Content
            FROM [ArchiveIRIS_MessagingHub].[dbo].[Messages] M """
        
    def generate_sql_join(self):
        self.join = """ LEFT JOIN [StagingIRIS_MessagingHub].[dbo].[AccountContacts] AC
            ON M.FromIdentity COLLATE SQL_Latin1_General_CP1_CI_AS = AC.[Identity] 
                AND M.ToIdentity COLLATE SQL_Latin1_General_CP1_CI_AS = AC.[Owner]  
            LEFT JOIN [StagingIRIS_MessagingHub].[dbo].[Accounts] A
                ON M.ToIdentity COLLATE SQL_Latin1_General_CP1_CI_AS = A.[Identity] """
   
    def generate_sql_where(self):
        self.where = """  
            WHERE M.[ToIdentity] = '{0}'
            AND M.[StorageDate] AT TIME ZONE 'E. South America Standard Time' >= CAST(CAST('{1}' AS DATE) AS DATETIME) AT TIME ZONE 'E. South America Standard Time'
            AND M.[StorageDate] AT TIME ZONE 'E. South America Standard Time'  < CAST(CAST('{2}' AS DATE) AS DATETIME) AT TIME ZONE 'E. South America Standard Time'
            AND M.FromDomain NOT IN ('omnize.gw.msging.net','desk.msging.net','msging.net','httpreceiver.msging.net','broadcast.msging.net')
            AND M.Id IS NOT NULL
            AND M.ContentMediaType NOT IN ('application/vnd.lime.chatstate+json','application/vnd.lime.redirect+json','application/vnd.omni.attendance+json')
            AND (AC.[Group] IS NULL OR AC.[Group] <> 'testers') 
        """.format(self.bot_id, self.begin_date, self.end_date)
        
    def generate_query(self):
        try:
            if self.full_information:
                self.generate_sql_full_select()
                self.generate_sql_join()
                self.generate_sql_where()
                self.query = self.select + self.join + self.where
                logging.debug('Query Building Success')
            else:
                self.generate_sql_select()
                self.generate_sql_join()
                self.generate_sql_where()
                self.query = self.select + self.join + self.where
                logging.debug('Query Building Success')
        except:
            logging.exception('Query Building Exception')

    def execute(self):
        try:
            logging.debug('Query Started')
            self.generate_query()
            start = time()
            self.data = pd.read_sql(self.query, self.sql_conn)
            logging.debug('Query Finished Successfully')
            end = time()
            print('Time elapsed = ' + str(end - start) + ' seconds')
            self.sql_conn.close()
        except:
            print('Exception Occurred')
            self.sql_conn.close()
        #self.erase_older_log(self.log_file_name_old, self.log_file_name_current)
    
    def get_query(self):
        return self.query
    
    def get_data(self):
        return self.data
    
    def erase_older_log(self, older_log, new_log):
        with open(older_log, "r+") as f:
            with open(new_log, "w") as f1:
                for line in f.readlines(): 
                    print(line)
                    f1.write(line)
                f.seek(0)
                f.truncate()