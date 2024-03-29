import pymssql
import os
import keyboard
import datetime
import time
import traceback
import copy
import configparser
import ftplib
import logging
import smtplib
##
from datetime import datetime, date
##################################################################
from dateutil.relativedelta import relativedelta, FR, TU
from dateutil.easter import easter
from dateutil.parser import parse
from dateutil import rrule
###################################################################
##
from progress.bar import ShadyBar
#import sqlite3
####
from rich.console import Console
from rich.table import Table
from rich import print
from rich.traceback import install
from rich.panel import Panel
from rich import box
from rich.prompt import Prompt, IntPrompt
from rich.console import Group
####
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
#####################


##############
#rich setting#

install() #for tracebacks


console = Console()
rich_ok = "bright_green on black"
rich_error = "bright_red on black"
rich_yellow = "bright_yellow on black"
rich_sky_blue = "sky_blue3 on black"

#rich settings end#
###################

########
#config#
config = configparser.ConfigParser()
config.read("/root/dbtodb_auto/config.cnf")


#msg.attach(MIMEText('hello world!', 'plain'))
#msg['Subject'] = 'test_1'
#email.send_message(msg)
#end config#
############

###########
#functions#
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def press_any_key():
    os.system('pause' if os.name=='nt' else "read -n 1 -s -r -p 'press any key'")
#functions end#
###############

database_num = 1
error = False
bool_to_main_while = True
##
#datetime_now = datetime.now()

#get logfile from ftp
ftp = ftplib.FTP(config.get('FTP', 'ftp_server'), config.get('FTP', 'ftp_login'), config.get('FTP', 'ftp_password'))
ftp.cwd('/IT/RogerB')
filename = 'PREvents.rcp'
file = open(filename, 'wb')
ftp.retrbinary('RETR '+ filename, file.write, 1024)
file.close()
ftp.quit()

#create logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='/root/dbtodb_auto/log')
logging.info('=============')
logging.info('start program')

#get test bool variable
test_mode = config.getboolean("TEST_MODE", "test mode")
if test_mode == True:
    logging.warning('test mode its on')

#connect to viso
host_to_viso = config.get("ROGER", "server") #'192.168.71.253\ROGER_ZABRZE'
user_to_viso = config.get("ROGER", "user") #'roger-ro'
password_to_viso = config.get("ROGER", "password") #'QE4tWEG#$5'
database_to_viso = config.get("ROGER", "database") #'Viso'
####
try:
    connection_to_viso = pymssql.connect(
            host=host_to_viso,
            user=user_to_viso,
            password=password_to_viso,
            database=database_to_viso)
    cursor_to_viso = connection_to_viso.cursor()
    logging.info('connect to viso ok')
except:
    logging.error('error connect to viso')
    logging.exception('except')
    bool_to_main_while = False

#main while start
while database_num < 5 and bool_to_main_while == True: #bool_to_main_while == True:

    #######
    #mssql#

    #######
    #enova#

    if test_mode == False:
        table_name_for_insert = 'WejsciaWyjsciaI'
        table_name_duplicate_for_insert = 'WejsciaWyjsciaO'
        #
        if database_num == 1:
            database_name_for_enova = config.get("ENOVA", "database_1") #'DromaSC78' #main base 
        elif database_num == 2:
            database_name_for_enova = config.get("ENOVA", "database_2") #'Droma'
        elif database_num == 3:
            database_name_for_enova = config.get("ENOVA", "database_3") #'DromaZW'
        elif database_num == 4:
            database_name_for_enova = config.get("ENOVA", "database_4") #'Faher'
    ##
    elif test_mode == True:
        table_name_for_insert = config.get("TEST_MODE", "table_for_test") #'test_copy_2'
        database_name_for_enova = config.get("TEST_MODE", "database_for_test") #'for_test_import'
    ####
    host_to_enova = config.get("ENOVA", "server") #'192.168.40.24\ENOVA'
    user_to_enova = config.get("ENOVA", "user") #'DJ'
    password_to_enova = config.get("ENOVA", "password") #'KREma.234.luka'
    database_to_enova = database_name_for_enova#'for_test_import'
    ##
    try:
        connection_to_enova = pymssql.connect(
                    host=host_to_enova,
                    user=user_to_enova,
                    password=password_to_enova,
                    database=database_to_enova)
        cursor_to_enova = connection_to_enova.cursor()
        logging.info('connect to '+database_name_for_enova+' ok')
    except:
        console.print(Panel("error connect to enova"), style=rich_error)

    #enova end#
    ###########

    ################################
    #import data from viso to enova#

    finish_rows = []
    finish_rows_duplicate = []
    def import_data_from_viso_to_enova():
        global finish_rows
        global finish_rows_duplicate
        #
        datetime_now = datetime.now()
        #
        try:
            cursor_to_viso.execute("SELECT MAX(id) FROM AccessUserPersons")
            rows = cursor_to_viso.fetchall()
        except:
            logging.error('error to get max_ID')
            logging.exception('except')
            return 0
        #
        max_id = rows[0][0] + 1
        ####
        datetime_now = datetime_now + relativedelta(days=(-1))
        date1 = datetime_now.strftime('%Y-%m-%d')
        date2 = datetime_now.strftime('%Y-%m-%d')
        #if datetime_now.day >= 1 and datetime_now.day < 16:
            #datetime_now = datetime_now + relativedelta(days=(-datetime_now.day))
            ###
            #if datetime_now.month < 10:
                #datetime_now_month = '0'+str(datetime_now.month)
            #else:
                #datetime_now_month = str(datetime_now.month)
            ###
            #date1 = str(datetime_now.year)+'-'+datetime_now_month+'-16'
            #date2 = datetime_now.strftime('%Y-%m-%d')
        #else:
            #if datetime_now.month < 10:
                #datetime_now_month = '0'+str(datetime_now.month)
            #else:
                #datetime_now_month = str(datetime_now.month)
            ###
            #date1 = str(datetime_now.year)+'-'+datetime_now_month+'-01'
            #date2 = str(datetime_now.year)+'-'+datetime_now_month+'-15'
        ####
        date1_datetime = datetime.strptime(date1, '%Y-%m-%d')
        date2_datetime = datetime.strptime(date2, '%Y-%m-%d')
        ##
        date_buff = datetime.strptime(date2, "%Y-%m-%d")
        date_buff = date_buff + relativedelta(days=+1)
        date3 = date_buff.strftime("%Y-%m-%d")

        #################
        #while in import#

        while_for_import = 4#1478
        errors = False
        #progress bar
        while while_for_import < max_id:
            #console.print(while_for_import)

            ########
            #step 1#

            ############################
            #get UserExternalIdentifier#
            ############################

            try:
                cursor_to_viso.execute("SELECT AccessUserPersons.UserExternalIdentifier, "
                            "AccessUserPersons.ID "
                            "FROM AccessUserPersons "
                            "WHERE "
                            "AccessUserPersons.id = "+str(while_for_import))
                rows = cursor_to_viso.fetchall()
                user_external_id = copy.copy(rows[0][0])
            except:
                errors = True
                console.print(Panel("error get external id"), style=rich_error)
                console.print(Panel(traceback.format_exc()), style=rich_error)
                logging.error('get external id error')
                logging.exception('except')
                return False
            #end step 1#
            ############

            ##########
            #step 1.1#

            ##################
            #get RCP <---> ID#
            ##################

            if errors == False:
                if test_mode == False:
                    try:
                        cursor_to_enova.execute("""SELECT
                            KartyRCP.Pracownik
                            FROM KartyRCP
                            WHERE
                            KartyRCP.Numer = '"""+user_external_id+"'")
                        rows = cursor_to_enova.fetchall()
                        ##
                        if rows:
                            pracownik_in_enova = copy.copy(rows[0][0])
                        else:
                            errors = True
                    ##
                    except:
                        errors = True
                        logging.error('get RCP -> ID')
                        logging.exception('except')
                        return False
                ##
                elif test_mode == True:
                    pracownik_in_enova = user_external_id
            #end step 1.1#
            ##############

            ########
            #step 2#

            #################
            #get log entries#
            #################
            if errors == False:
                try:
                    cursor_to_viso.execute("SELECT EventLogEntries.LoggedOn, "
                            "EventLogEntries.ControllerID "
                            "FROM "
                            "EventLogEntries "
                            "WHERE "
                            "EventLogEntries.PersonID = '"+str(while_for_import)+"' AND "
                            "EventLogEntries.LoggedOn >= '"+date1+"' AND EventLogEntries.LoggedOn <= '"+date3+"'") 
                    rows = cursor_to_viso.fetchall()
                except:
                    errors = True
                    logging.error('get logs entries')
                    logging.exception('except')
                    return False
            #end step 2#
            ############

            #if not empty#
            if rows:
                ########
                #step 3#

                ###########################
                #leave only log in log out#
                ###########################

                if errors == False:
                    i_in_while = 1
                    while i_in_while < len(rows)-1:
                        if rows[i_in_while][0].day == rows[i_in_while+1][0].day:
                            del rows[i_in_while]
                        else:
                            i_in_while += 2
                #end step 3#
                ############

                ########
                #step 4#

                ###################################
                #create rows for table in database#
                ###################################

                if errors == False:
                    i_in_while = 0
                    bool_for_typ = False
                    while i_in_while < len(rows):
                        ##
                        timestamp_buff = datetime.timestamp(rows[i_in_while][0])
                        time_sum_in_min = rows[i_in_while][0].hour*60+rows[i_in_while][0].minute
                        ##
                        typ = 0
                        operacia = 0
                        #
                        if bool_for_typ == False:
                            typ = 1
                            operacia = 0
                            bool_for_typ = True
                        else:
                            typ = 2
                            operacia = 16
                            bool_for_typ = False
                        ##
                        finish_row = [pracownik_in_enova, rows[i_in_while][0], time_sum_in_min, typ, operacia, 0, 0, 10, 0]
                        finish_row_duplicate = [pracownik_in_enova, rows[i_in_while][0], time_sum_in_min, typ, operacia, 10, 0]
                        ##
                        finish_rows.append(tuple(finish_row))
                        finish_rows_duplicate.append(tuple(finish_row_duplicate))
                        ##
                        i_in_while += 1

                #end step 4#
                ############

                ########
                #step 5#

                ########################
                #write data in database#
                ########################

                if errors == False:
                    try:
                        buff_tuple = tuple(finish_rows)
                       #enova_columns: str = "Pracownik, Data, Godzina, Typ, Operacja, Zaimportowany, Stan, CzytnikRCP, Stamp, Zmodyfikowany"
                        cursor_to_enova.executemany("""INSERT INTO """+table_name_for_insert+"""
                            (Pracownik, Data, Godzina, Typ, Operacja, Zaimportowany, Stan, CzytnikRCP, Zmodyfikowany)
                            VALUES (%s, %d, %d, %d, %d, %d, %d, %d, %d)""", buff_tuple)
                        connection_to_enova.commit()
                        #duplicate#
                        if test_mode == False:
                            buff_tuple = tuple(finish_rows_duplicate)
                            cursor_to_enova.executemany("""INSERT INTO """+table_name_duplicate_for_insert+"""
                                (Pracownik, Data, Godzina, Typ, Operacja, CzytnikRCP)
                                VALUES (%s, %d, %d, %d, %d, %d)""", buff_tuple)
                            connection_to_enova.commit()
                        ##
                    except:
                        errors = True
                        logging.error('insert to table')
                        logging.exception('except')
                        return False
                #end step 5#
                ############
            #end if not empty#

            #if user pressed continue#
            if errors == True:
                errors = False
            #
            finish_rows.clear()
            finish_rows_duplicate.clear()
            while_for_import += 1
            #
        #while in import end#
        #####################
        return True

    #end import data from viso to enova#
    ####################################

    #####################################
    #import data from bojkowska to enova#
    def import_data_from_bojkowska_to_enova():
        ##
        buff_str = ''
        list_for_data_from_bojkowska = []
        ##
        datetime_now = datetime.now()
        ##
        datetime_now = datetime_now + relativedelta(days=(-1))
        date1 = datetime_now.strftime('%Y-%m-%d')
        date2 = datetime_now.strftime('%Y-%m-%d')
        #if datetime_now.day >= 1 and datetime_now.day < 16:
            #datetime_now = datetime_now + relativedelta(days=(-datetime_now.day))
            ###
            #if datetime_now.month < 10:
                #datetime_now_month = '0'+str(datetime_now.month)
            #else:
                #datetime_now_month = str(datetime_now.month)
            ###
            #date1 = str(datetime_now.year)+'-'+datetime_now_month+'-16'
            #date2 = datetime_now.strftime('%Y-%m-%d')
        #else:
            #if datetime_now.month < 10:
                #datetime_now_month = '0'+str(datetime_now.month)
            #else:
                #datetime_now_month = str(datetime_now.month)
            ###
            #date1 = str(datetime_now.year)+'-'+datetime_now_month+'-01'
            #date2 = str(datetime_now.year)+'-'+datetime_now_month+'-15'
        ####
        #check datetime#
        date1_datetime = datetime.strptime(date1, '%Y-%m-%d')
        date2_datetime = datetime.strptime(date2, '%Y-%m-%d')
        #open text file#
        try:
            #logfile = open(config.get("LOG_FILES", "filename from bojkowska"), 'r') 
            logfile = open(filename, 'r')
        except:
            logging.error('open file')
            logging.exception('except')
            return False

        ########
        #step 1# 

        ##################################
        #its step get list from text file#
        ##################################


        list_from_file = []
        ##
        try:
            #write text file to list#
            for i_for_file in logfile:
                list_from_file.append(i_for_file)
            del list_from_file[0]
            ##
            #delete spaces in end rows#
            i_in_while = 0
            while i_in_while < len(list_from_file):
                #row_for_data_from_bojkowska.clear()
                list_from_file[i_in_while] = list_from_file[i_in_while].strip()
                #
                row_for_data_from_bojkowska = []
                for symbol in list_from_file[i_in_while]:
                    #
                    if symbol != ';' and symbol != 'T' and symbol != '/':
                        buff_str += symbol
                    #
                    else:
                        row_for_data_from_bojkowska.append(buff_str)
                        buff_str = ''
                #
                list_for_data_from_bojkowska.append(row_for_data_from_bojkowska)
                del row_for_data_from_bojkowska
                i_in_while += 1
        except:
            logging.error('read from file')
            logging.exception('except')
            return False
        #end step 1#
        ############

        ########
        #step 2#

        ################
        #create id list#
        ################
        buff_id_list = []

        try:
            i_in_while = 0
            while i_in_while < len(list_for_data_from_bojkowska):
                buff_id_list.append(list_for_data_from_bojkowska[i_in_while][2])
                i_in_while += 1
        except:
            logging.error('create id list')
            logging.exception('except')
            return False

        ##############################
        #delete douplicate in id_list#

        buff_id_list = set(buff_id_list)
        id_list = list(buff_id_list)
        #end delete doublicate in id_list#
        ##################################

        #end step 2#
        ############

        ##########
        #step 2.1#

        ################################
        #create dictionary RCP <---> ID#
        ################################
        id_list_dictionary = {}
        ####
        try:
            if test_mode == False:
                ##
                i_in_while = 0
                while i_in_while < len(id_list):
                    cursor_to_enova.execute("""
                            SELECT KartyRCP.Pracownik 
                            FROM KartyRCP
                            WHERE
                            KartyRCP.Numer =  
                            '"""+id_list[i_in_while]+"'") 
                    row = cursor_to_enova.fetchall()
                    ##
                    if row:
                        id_list_dictionary[id_list[i_in_while]] = row[0][0]
                    else:
                        del id_list[i_in_while]
                        continue
                    ##
                    i_in_while += 1
            ##
            else:
                i_in_while = 0
                while i_in_while < len(id_list):
                    id_list_dictionary[id_list[i_in_while]] = id_list[i_in_while]
                    i_in_while += 1
        except:
            logging.error('create dictionary RCP <---> ID')
            logging.exception('except')
            return False

        #end step 2.1#
        ##############

        ##########
        #step 2.2#

        ######################
        #delete row if no RCP#
        ######################

        i_in_while = 0
        while i_in_while < len(list_for_data_from_bojkowska):
            if id_list_dictionary.get(list_for_data_from_bojkowska[i_in_while][2]) == None:
                del list_for_data_from_bojkowska[i_in_while]
                continue
            else:
                i_in_while += 1

        #end step 2.2#
        ##############

        ########
        #step 3#

        ##########################################
        #create datetime columns and summ columns#
        ##########################################
        try:
            i_in_while = 0
            while i_in_while < len(list_for_data_from_bojkowska):
                list_for_data_from_bojkowska[i_in_while][0] = datetime.strptime(list_for_data_from_bojkowska[i_in_while][0], "%Y-%m-%d")
                buff_datetime = datetime.strptime(list_for_data_from_bojkowska[i_in_while][1], "%H:%M:%S")
                list_for_data_from_bojkowska[i_in_while][1] = str(buff_datetime.hour * 60 + buff_datetime.minute)
                i_in_while += 1 
            ##
            buff_list_for_data_from_bojkowska = []
            i_in_while = 0
        except:
            logging.error('create datetime columns and summ columns')
            logging.exception('except')
            return False

        #################
        #datetime sample#
        #################
        try:
            while i_in_while < len(list_for_data_from_bojkowska):
                #
                if (list_for_data_from_bojkowska[i_in_while][0] >= date1_datetime and
                        list_for_data_from_bojkowska[i_in_while][0] <= date2_datetime):
                    #
                    buff_list_for_data_from_bojkowska.append(list_for_data_from_bojkowska[i_in_while])
                i_in_while += 1
            ##
            list_for_data_from_bojkowska = buff_list_for_data_from_bojkowska
            del buff_list_for_data_from_bojkowska
        except:
            logging.error('datetime sample')
            logging.exception('except')
            return False

        ##########################################
        #sorting list by id and delete duplicates#
        ##########################################
        buff_list_for_sorted_data = []

        i_in_while = 0
        try:
            while i_in_while < len(id_list):
                #
                block = []
                j_in_while = 0
                while j_in_while < len(list_for_data_from_bojkowska):
                    if id_list[i_in_while] == list_for_data_from_bojkowska[j_in_while][2]:
                        block.append(list_for_data_from_bojkowska[j_in_while])
                    j_in_while += 1
                #
                j_in_while = 1
                while j_in_while < len(block)-1:
                    if block[j_in_while][0] == block[j_in_while+1][0]:
                        del block[j_in_while]
                    else:
                        j_in_while += 2
                #
                j_in_while = 0
                while j_in_while < len(block):
                    buff_list_for_sorted_data.append(block[j_in_while])
                    j_in_while += 1
                #
                i_in_while += 1
            ##
            list_for_data_from_bojkowska = buff_list_for_sorted_data
            del buff_list_for_sorted_data
        except:
            logging.error('sorting list by id and delete duplicate')
            logging.exception('except')
            return False
        ##
        #end step 3#
        ############

        ########
        #step 4#

        ####################
        #create finish list#
        ####################
        finish_list = []
        finish_row = []
        #
        finish_list_duplicate = []
        finish_row_duplicate = []
        #
        bool_for_typ = False
        #
        i_in_while = 0
        while i_in_while < len(list_for_data_from_bojkowska):
            try:
                typ =  0
                operacja = 0
                #
                if bool_for_typ == False:
                    typ = 1
                    operacja = 0
                    bool_for_typ = True
                else:
                    typ = 2
                    operacja = 16
                    bool_for_typ = False
                #
                finish_row = [id_list_dictionary.get(list_for_data_from_bojkowska[i_in_while][2]),
                        list_for_data_from_bojkowska[i_in_while][0],
                        list_for_data_from_bojkowska[i_in_while][1],
                        typ,
                        operacja,
                        0,
                        0,
                        0,
                        11]
                #
                finish_list.append(tuple(finish_row))
                finish_row.clear()
                ##
                if test_mode == False:
                    finish_row_duplicate = [id_list_dictionary.get(list_for_data_from_bojkowska[i_in_while][2]),
                                    list_for_data_from_bojkowska[i_in_while][0],
                                    list_for_data_from_bojkowska[i_in_while][1],
                                    typ,
                                    operacja,
                                    11]
                    #
                    finish_list_duplicate.append(tuple(finish_row_duplicate))
                    finish_row_duplicate.clear()
                ##
                i_in_while += 1
            except:
                logging.error('create finish list')
                logging.exception('except')
                return False
        #end while
        #end step 4#
        ############

        ########
        #step 5#

        #################
        #insert to enova#
        #################
        buff_tuple = tuple(finish_list)
        ##
        try:
            cursor_to_enova.executemany("""INSERT INTO """+table_name_for_insert+"""
                (Pracownik, Data, Godzina, Typ, Operacja, Zaimportowany, Stan, Zmodyfikowany, CzytnikRCP)
                VALUES (%s, %d, %d, %d, %d, %d, %d, %d, %d)""", buff_tuple)
            connection_to_enova.commit()
            ##
            if test_mode == False:
                #duplicate#
                buff_tuple = tuple(finish_list_duplicate)
                cursor_to_enova.executemany("""INSERT INTO """+table_name_duplicate_for_insert+"""
                    (Pracownik, Data, Godzina, Typ, Operacja, CzytnikRCP)
                    VALUES (%s, %d, %d, %d, %d, %d)""", buff_tuple)
                connection_to_enova.commit()
        except:
            logging.error('insert to enova')
            logging.exception('except')
            return False
        ##
        return True
        #end step 5#
        ############

    #end import data from bojkowska to enova#
    #########################################

    #mssql end#
    ###########

    #######
    #menus#

    ###########
    #main menu#

    #main menu end#
    ###############

    #menus end#
    ###########

    ######
    #main#

    if import_data_from_bojkowska_to_enova():
        logging.info('bojkowska to '+database_name_for_enova+' end')
    else:
        error = True
        logging.error('bojkowska to '+database_name_for_enova+' error')
    ##
    if import_data_from_viso_to_enova():
        logging.info('viso to '+database_name_for_enova+' end')
    else:
        error = True
        logging.error('viso to '+database_name_for_enova+' error')

    try:
        connection_to_enova.close()
    except:
        logging.error('error connection to close')

    database_num += 1

##
msg = MIMEMultipart()
msg['From'] = config.get('MAIL', 'addr_from')
msg['To'] = config.get('MAIL', 'addr_to')

email = smtplib.SMTP(config.get('MAIL', 'server'), config.getint('MAIL', 'port'))
email.starttls()
email.login(config.get('MAIL', 'addr_from'), config.get('MAIL', 'password'))#config.get('MAIL', 'password'))

if error == True:
    error_message = '''warning! error import to enova. read log. check enova. if the error occurs again - check configuration,
check databases, try running manual version program.'''
    msg.attach(MIMEText(error_message, 'plain'))
    msg['Subject'] = '!ERROR IMPORT TO ENOVA!'
    email.send_message(msg)
    logging.error('improt error')
else:
    msg.attach(MIMEText('complete import to enova', 'plain'))
    msg['Subject'] = 'complete import to enova'
    email.send_message(msg)
    logging.info('import complete')
##
connection_to_viso.close()
email.quit()
#main end#
##########
