# THESE IMPORTS ARE NECESSARY FOR THE BREVO API
from __future__ import print_function
import time
import brevo_python
from brevo_python.rest import ApiException
from pprint import pprint

# THIS IMPORTS ARE NECESSARY TO EXPLORE AND PARSE BROWSER HISTORY
from browser_history import get_history
from datetime import datetime, timedelta, timezone

# THIS IMPORT IS NECESSARY TO LOAD ENVIRONMENT VARIABLES
import os
from dotenv import load_dotenv

# THESE ARE NECESSARY FOR THE SPLASH SCREEN TO WORK PROPERLY
import getpass
import platform

# REGEX LIBRARY FOR DATA VALIDATION
import re

# THIS IMPORT IS NECESSARY TO SLEEP THE PROGRAM
import time

# THIS IMPORT IS NECESSARY TO EXIT GRACEFULLY
import sys



#####################################################################################
#####################################################################################
#####################################################################################
# LOAD ENVIRONMENT VARIABLES 
#####################################################################################
#####################################################################################
#####################################################################################

#####################################################################################
# THIS LOADS THE ENVIRONMENT VARIABLES FROM THE .env FILE SPECIFICALLY
#####################################################################################

load_dotenv()

#####################################################################################
# ASSIGN ENVIRONMENT VARIABLES TO PYTHON VARIABLES
#####################################################################################


# THESE VARIABLES ARE USED TO CONFIGURE THE BREVO API
API_KEY = os.getenv("API_KEY")
PORT = os.getenv("PORT")


# THIS CONSTANT WILL DEFINE THE REFRESH RATE IN MINUTES
# LOWERING THIS VALUE MAY CAUSE THE PROGRAM TO RUN SLOWER
# RAISING THIS VALUE MAY CAUSE THE PROGRAM TO GIVE LATENT RESULTS
# MUST BE CAST AS AN INTEGER, BE CAUTIOUS WHEN CHANGING THIS VALUE
TIME_INTERVAL = os.getenv("TIME_INTERVAL")
FROM_EMAIL = os.getenv("FROM_EMAIL")
try:
    TIME_INTERVAL = int(TIME_INTERVAL)
except ValueError:
    print("  [!] TIME_INTERVAL must be an integer")
    print("  [!] Defaulting to 1 minute")
    TIME_INTERVAL = 1

# THESE ARE REGEX PATTERNS FOR DATA VALIDATION
NAME_REGEX = r"^[A-Za-z\- ]+$"
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
WEBSITE_REGEX = r"^[A-Za-z0-9.-]+$"



#####################################################################################
#####################################################################################
#####################################################################################
# FUNCTION LIBRARY 
#####################################################################################
#####################################################################################
#####################################################################################


#####################################################################################
# THIS FUNCTION CLEARS THE SCREEN ON MULTIPLE OSes SO THE PROGRAM
# DOESNT HAVE TO BE SO DANG UGLY
#####################################################################################
def clear_terminal():
    os.system("cls" if platform.system() == "Windows" else "clear")

#####################################################################################
# THIS FUNCTION DISPLAYS THE SPLASH SCREEN WHEN THE USER RUNS THE PROGRAM
#####################################################################################
def display_splashscreen():
    # clear the terminal, I am the captain now
    clear_terminal()

    # print a lovely little splashscreen
    print(r"                                                  ")
    print(r"                                                  ")
    print(r"   __ _                  _        _ _       _     ")
    print(r"  / _\ |__   ___  _ __  | | _ __ (_) |_ ___| |__  ")
    print(r"  \ \| '_ \ / _ \| '_ \/ __) '_ \| | __/ __| '_ \ ")
    print(r"  _\ \ | | | (_) | |_) \__ \ | | | | || (__| | | |")
    print(r"  \__/_| |_|\___/| .__/(   /_| |_|_|\__\___|_| |_|")
    print(r"                 |_|    |_|                       ")
    print(r"                                                  ")
    print(r"    by Charles Deane 2025                         ")
    print(r"                                                  ")
    print(r"    A friendly reminder:                          ")
    print(r"    DO NOT USE THIS WITHOUT SOMEONE'S CONSENT     ")
    print(r"                                                  ")
    print(r"    Press ENTER if you UNDERSTAND and AGREE...    ")
    print(r"                                                  ")
    
    # wait for the user to press enter
    # rather than using input I am using getpass to avoid echoing
    # input that is not <ENTER>
    getpass.getpass("")
    # clear the screen
    clear_terminal()



#####################################################################################
# THIS FUNCTION CONFIGURES THE BREVO API AND RETURNS THE API INSTANCE 
#####################################################################################
def configure_brevo_api(api_key):
    # configure api key authorization: 
    configuration = brevo_python.Configuration()
    configuration.api_key['api-key'] = api_key

    # create an instance of the API class
    api_instance = brevo_python.TransactionalEmailsApi(brevo_python.ApiClient(configuration))

    # print the api instance to confirm it is working
    print("  [*] Brevo API Authentication successful")

    #return the api instance for use globally
    return api_instance


#####################################################################################
# THIS FUNCTION MAKES A LIST READABLE IN SENTENCE FORMAT
#####################################################################################
def make_list_readable(site_list):
    # make the site_list a reasonable string
    # this will make it so that lists of 2 or more items are formatted correctly with an "and"
    # so you either get "A" "A and B" or "A, B, ... and Z" 
    return_string = ""
    for i in range(0, len(site_list)):
        if i == len(site_list) - 1 and len(site_list) > 1:
            return_string += "and " + site_list[i].upper()
        elif len(site_list) <= 2:
            return_string += site_list[i].upper() + " "
        else:
            return_string += site_list[i].upper() + ", "
            
    # return the string
    return return_string

#####################################################################################
# THIS FUNCTION SENDS AN ALERT USING THE BREVO API
#####################################################################################
def send_alert(api_instance, site_list, shopper_name, user_name, user_email, from_email):

    # notify the terminal monitoring that an alert is being sent
    print("  [*] Sending alert to " + user_name + " at " + user_email)

    #####################################################################################
    # create the components of the email
    #####################################################################################
    site_list_string = make_list_readable(site_list)
    subject = "ALERT! " + site_list_string + " found in browser history!"
    
    sender = {"name": "your friendly neighborhood shopsnitch", "email":from_email}
    reply_to = {"name": "your friendly neighborhood shopsnitch", "email":from_email}
    to = [{"email":user_email,"name":user_name}]

    # format the body of the email with html
    html_content = """
        <h1>ALERT!</h1>
        <h2>""" + site_list_string + """ found in browser history!</h2>
        <h3>You may want to give """ + shopper_name + """ a call before they purchase!<h3>
        """

    #####################################################################################
    # combine the variables into an email object as defined by the brevo api
    #####################################################################################
    send_smtp_email = brevo_python.SendSmtpEmail(to=to, reply_to=reply_to,
                                             html_content=html_content, sender=sender, subject=subject) # SendSmtpEmail | Values to send a transactional email
    # try to send an email
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        # pprint(api_response)
    # if there is an error, print the error
    except ApiException as e:
        print("  [!] Exception when calling TransactionalEmailsApi->send_transac_email: %s\n" % e)




#####################################################################################
# THIS FUNCTION CHECKS THE BROWSER HISTORY FOR THE SPECIFIED TIME PERIOD
# THE TIME PERIOD PARAMETER IS IN MINUTES
#####################################################################################
def get_browser_history(time_period):
    
    returnlist = []
    print("Checking installed browsers")

    # get the available browser history
    output = get_history()

    # the timezone must be added so the object is not naive
    current_time = datetime.now(timezone.utc)

    # add the items from the browser history within the time period to the return list 
    all_user_history = output.histories
    for history in all_user_history:
        if history[0] > current_time - timedelta(minutes=time_period):
           returnlist.append(history) 

    # returns a list of the browser history within the time period
    return returnlist




#####################################################################################
# THIS FUNCTION CHECKS TO SEE IF THE ALERT SITE IS IN THE BROWSER HISTORY
# OF A GIVEN LIST AND RETURNS A BOOLEAN
#####################################################################################
def find_alerts(my_recent_browser_history, alert_site_list):
    # first check to see if there are any items in the browser history list
    # if there are no items then return false because the result is not present
    if len(my_recent_browser_history) == 0:
        print("  [*] No new browser history found")
        return []

    # if there are items in the browser history list then check to see if the alert site is in the list
    else:
        return_list = []
        for history in my_recent_browser_history:
            for alert_site in alert_site_list:
                if alert_site in str(history[2]).lower():
                    return_list.append(alert_site)
                    break
    
    # if the return list is empty then there are no alerts in the browser history
    if return_list == []:
        print("  [*] No alerts found in browser history")
        return []
    # if the return list is not empty then there are alerts in the browser history
    else:
        return_list = list(set(return_list))
        print( "  [*] Found " + make_list_readable(return_list) + " in browser history!")
        return return_list


#####################################################################################
#####################################################################################
#####################################################################################
# THESE FUNCTIONS GATHER AND VALIDATE USER INPUT
#####################################################################################
#####################################################################################
#####################################################################################

# THIS FUNCTION PROMPTS THE USER FOR THEIR NAME AND VALIDATES IT
def get_user_name(regex):
    # prompt the user for their name
    user_name = input("\n  Please enter your name -> ")
    # check to see if the name is valid
    # if it is valid then return the name
    # if it is not valid then recurse and start over
    if re.match(regex, user_name):
        return user_name
    else:
        print("  Invalid name. Please try again.")
        return get_user_name(regex)



# THIS FUNCTION PROMPTS THE USER FOR THEIR EMAIL ADDRESS AND VALIDATES IT
def get_user_email(regex):
    # prompt the user for their email address
    user_email = input("\n  Please enter your email address -> ")
    # check to see if the email address is valid
    # if it is valid then return the email address
    # if it is not valid then recurse and start over
    if re.match(regex, user_email):
        return user_email
    else:
        print("  Invalid email. Please try again.")
        return get_user_email(regex)



# THIS FUNCTION PROMPTS THE USER FOR THE SHOPPER NAME AND VALIDATES IT
def get_shopper_name(regex):
    # prompt the user for the shopper name
    shopper_name = input("\n  Please enter the name of the shopper -> ")
    # check to see if the shopper name is valid
    # if it is valid then return the shopper name
    # if it is not valid then recurse and start over
    if re.match(regex, shopper_name):
        return shopper_name
    else:
        print("  Invalid name. Please try again.")
        return get_shopper_name(regex)



# THIS FUNCTION PROMPTS THE USER FOR THE ALERT SITES AND VALIDATES THEM
def get_alert_site(regex):
    # prompt the user for the alert sites
    print("\n  Please enter the name of the sites you")
    print("  want to be alerted about. If there are")
    print("  multiple sites, separate them with a space.")
    alert_site = input("  Or hit enter for default (Amazon) -> ")
    # if the user does not enter anything then set the alert site to Amazon by default
    if alert_site == "":
        return ['Amazon']
    # if the user enters data, split the input into a list
    else:
        alert_site_list = alert_site.split() # parsing the input into a list
    # check to see that all the items in the list are valid
    # if an invalid item is found then it will recurse and start over
    for alert in alert_site_list:
        if re.match(regex, alert) == False:
            print("  Invalid input. Please try again.")
            return get_alert_site(regex)
    # if all items are valid then return the list
    return alert_site_list

# THIS FUNCTION CLEANS THE ALERT SITE LIST
def clean_history_list(this_list):
    # convert all values to lowercase so that they compare properly
    for i in range(0, len(this_list)):
        this_list[i] = this_list[i].lower()
    # remove any duplicates from the list
    this_list = list(set(this_list))
    # return the cleaned list
    return this_list

# THIS FUNCTION EXITS THE PROGRAM GRACEFULLY
def exit_gracefully():
    clear_terminal()
    sys.exit(0)

#####################################################################################
#####################################################################################
#####################################################################################
# DISPLAY THE SPLASH SCREEN
#####################################################################################
#####################################################################################
#####################################################################################
try:
    display_splashscreen()
except KeyboardInterrupt:
    exit_gracefully()
    
#####################################################################################
#####################################################################################
#####################################################################################
# GATHER USER INPUT
#####################################################################################
#####################################################################################
#####################################################################################

# display a nice greeting
print("\nI just need some information from you before we get started...\n")

# this boolean will be used to determine if the user is satisfied with their input
# the program will not start processing data until the value is TRUE
finished_gathering_user_input = False

# This loop will continue until the user is satisfied with their input
try:
    while finished_gathering_user_input == False:
        #gather user input
        user_name = get_user_name(NAME_REGEX)
        user_email = get_user_email(EMAIL_REGEX)
        shopper_name = get_shopper_name(NAME_REGEX)
        alert_site_list = get_alert_site(WEBSITE_REGEX)
    

        # clean the data on the alert site
        alert_site_list = clean_history_list(alert_site_list)

        # clear the terminal so that that the question is more obvious
        clear_terminal()

        # display the user input
        print("\n  Please confirm your information:")
        print("")
        print("")
        print("  Name:    ", user_name)
        print("")
        print("  Email:   ", user_email)
        print("")
        print("  Shopper: ", shopper_name)
        print("")
        #funky list printing with a loop for values that arent index 0
        print("  Sites:   ", alert_site_list[0])
        for i in range(1, len(alert_site_list)):
            print("           ", alert_site_list[i])
        print("")
        print("")

        # prompt the user to confirm their input
        user_input_verification = input("  Is this information correct?  (Y/N)  ")
    

        # Change the user input to all uppercase to greatly reduce the amount of checks needed
        user_input_verification = user_input_verification.upper()

        # Check to see if the user is in fact done, otherwise clear the screen 
        # before the loop reiterates so things arent a total mess
        if user_input_verification == "Y" or  user_input_verification == "YES":
            finished_gathering_user_input = True
        else:
            clear_terminal() 
except KeyboardInterrupt:
    exit_gracefully()


#####################################################################################
#####################################################################################
#####################################################################################
# Start the Brevo API
#####################################################################################
#####################################################################################
#####################################################################################

# clear the terminal so that the program is purdier
clear_terminal()
print("  [*] Starting Brevo API...")

# initialize the global api instance
global_api_instance = configure_brevo_api(API_KEY)
print("  [*] Brevo API started successfully")



#####################################################################################
#####################################################################################
#####################################################################################
# Test functions to make sure things are working before setting timer
#####################################################################################
#####################################################################################
#####################################################################################

def main_function():
    # get the most recent slice of history
    current_history = get_browser_history(TIME_INTERVAL)
    # find the alerts in current history
    current_matches = find_alerts(current_history, alert_site_list)
    # if there are any matches then send an alert
    if current_matches != []:
        print("  [*] Initializing alert system")
        send_alert(global_api_instance, current_matches, shopper_name, user_name, user_email, FROM_EMAIL)
    else:
        print("  [*] No alerts will be sent at this time")

try:
    while True:
        # run the main function
        main_function()
        # sleep for the specified time interval
        print("  [*] Sleeping for " + str(TIME_INTERVAL) + " minutes")
        print("  [*] Press CTRL+C to exit")
        # sleep for the specified time interval
        time.sleep(TIME_INTERVAL * 60)
except KeyboardInterrupt:
    exit_gracefully()
