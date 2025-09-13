import sys
import variables
from datetime import datetime, timezone, timedelta
from flask_page.publicvar import last_run_times
# import logging

# logging.basicConfig(filename="cron_log.txt", level=logging.INFO, format="%(asctime)s - %(message)s")

#import urllib3
#import requests

#pip install selenium
#pip install beautifulsoup4
#pip install urllib3
#pip install requests
#pip install webdriver-manager



#VARIABLES-------------------------------------
program = variables.program
if program == "":
    program = "CB" 
#VARIABLES------------------



#print(len(sys.argv))
if len(sys.argv) > 1:
    program = sys.argv[1]
elif program == "FW":
    print("Running server...")
else:
    print("""
Please input argument:
          
# A - AutoBooking , CB - Check Booking PNR , CT - Celik Tafsir fetch ,
# TB - Telegram Bot , WS - Web Scraping , AAI - AI Chat test ,
# CRM - Cron Run Multiple , CRPC - Cron Run PC Multiple , CRO - Cron Run Once, 
# CSFTP - Check SFTP , RP - Reminder Parking , FW - Flask Website afwanproductions,
# CM - Check message telegram , BP - Bot Polling
# STL - Summary Today Log , EXPO - Expo go export,
# PROXY - Proxy server, PROXYWE - Proxy with edit link html
          
If you're server, run python3 runner.py CRM and python3 runner.py BP 
                    
""")
    exit(0)

program = program.upper()

if (program == "FW"):
    #moved to afwanhaziqmy.py
    from flask import Flask
    from flask_cors import CORS
    
    app = Flask(__name__)
    
    # CORS configuration to allow all origins
    CORS(app, supports_credentials=True,
        resources={r"/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"]
    )

if (program == "QT"):
    from quart import Quart, request, jsonify, render_template, render_template_string
    from quart_cors import cors

    app = Quart(__name__)
    app = cors(app, allow_origin="*")

#Public variables
if True:
    fyuser = ""
    fypass = ""
    fycode = ""
    tbtoken = ""
    csftplink = ""
    timenowKL = 0
    # last_run_times = last_run_times
    reminder = {} #todo - get data from user
    #http = urllib3.PoolManager()

def run_function(program_code, code2=None, info3=None):
    program = program_code
    global variables
    global timenowKL
    #global http



    #functions
    if (True):
        import urllib.request as ur
        import variables
        import time
        import datetime
        from datetime import datetime, timezone, timedelta
        from decimal import Decimal
        import platform
        browser_code = 'F' # C - Chrome , F - Firefox , E - Microsoft Edge , S - Safari
        openfileorfolder = 'F' # F - File , FD - Folder
        xmlformatted = True
        def open_file_path(file_path):
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                os.system(f'open "{file_path}"')
            else:  # Linux
                os.system(f'xdg-open "{file_path}"')
        def getbrowser(browser_code):
            if browser_code == 'C':
                trymethod = 0
                if trymethod == 0:
                    chrome_options = ChromeOptions()
                    chrome_options.add_experimental_option("detach", True)
                    chrome_options.add_argument("user-data-dir=C:\\Users\\YourUser\\AppData\\Local\\Google\\Chrome\\User Data")
                    chrome_options.add_argument("--profile-directory=Default")
                    browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
                elif trymethod == 1:
                    options = webdriver.ChromeOptions()
                    options.add_experimental_option("detach", True)
                    browser = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
                else:
                    options = ChromeOptions()
                    options.add_experimental_option("detach", True)  # Prevents browser from closing
                    #service = Service("chromedriver.exe")  # Path to your ChromeDriver
                    browser = webdriver.Chrome(options=options)
            elif browser_code == 'F':
                trymethod = 1
                if trymethod == 1:
                    options = webdriver.FirefoxOptions()
                    service = FirefoxService(FirefoxDriverManager().install())
                    browser = webdriver.Firefox(service=service, options=options)
                else:
                    browser = webdriver.Firefox()
            elif browser_code == 'S':
                browser = webdriver.Safari()
            elif browser_code == 'E':
                trymethod = 1
                if trymethod == 1:
                    options = EdgeOptions()
                    options.add_experimental_option("detach", True)  # Prevents browser from closing
                    service = EdgeService(EdgeDriverManager().install())
                    browser = webdriver.Edge(service=service, options=options)
                else:
                    options = EdgeOptions()
                    options.add_experimental_option("detach", True)  # Prevents browser from closing
                    browser = webdriver.Edge(options=options)
                # browser = webdriver.Edge(options=options)
            else:
                browser = webdriver.Firefox()

            return browser


    #CHECK BOOKING PNR
    if program == "CB":
        #needPass()

        import xml.dom.minidom
        #import urllib.request
        import os
        import platform
        import base64
        from datetime import datetime
        #needPass()

        #VARIABLES------------------
        pnr = input("Please input PNR: ")
        stagingorprod = input("Staging - s , Prod - p: ").upper() #S - Staging , P - Prod
        #VARIABLES------------------
        fycode = variables.fy_code
        bookingtype = "Production"

        if stagingorprod == "S":
            bookingtype = "Staging"
            link = variables.fy_app_staging
            url = f"{link}?Key={fycode}&RecordLocator={pnr}"
        else:
            bookingtype = "Production"
            link = variables.fy_app_prod
            url = f"{link}?Key={fycode}&RecordLocator={pnr}"

        #content = http.request("GET", url)
        #content = content.data.decode("utf-8")
        #content = base64.b64decode(content).decode('utf-8')
        req = ur.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        #try:
            #with urllib.request.urlopen(req) as response:
                #content = response.read()
        #except urllib.error.HTTPError as e:
            #print(f"HTTP Error: {e.code} - {e.reason}")
        #except urllib.error.URLError as e:
            #print(f"URL Error: {e.reason}")

        with ur.urlopen(req) as response:
                content = response.read().decode('utf-8')
        content = base64.b64decode(content)


        if xmlformatted:
            dom = xml.dom.minidom.parseString(content)
            content = dom.toprettyxml(indent="    ")

        date = datetime.now().strftime("%Y-%m-%d %H%M %S")
        file_name = f"output booking/{pnr} - {bookingtype} - {date}.xml"
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Content has been written to {file_name}")

        # Open the file location
        file_path = os.path.abspath(file_name)
        if openfileorfolder == "FD":
            file_path = os.path.dirname(file_path)
        
        open_file_path(file_path)

    #BOOKING FIREFLY - Auto Booking
    elif program == "A":
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.alert import Alert
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.edge.options import Options as EdgeOptions
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.edge.service import Service as EdgeService
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.firefox import GeckoDriverManager as FirefoxDriverManager
        from webdriver_manager.microsoft import EdgeChromiumDriverManager as EdgeDriverManager
        from webdriver_manager.opera import OperaDriverManager
        # from webdriver_manager.drivers import edge
        import time
        #needPass()

        #VARIABLES------------------
        is_one_way = input("Is one way? y/n: ").upper() # Y - Yes, N - No
        is_one_way = is_one_way == "Y"
        # is_login = input("Is login? y/n: ").upper() # Y - Yes , N - No
        is_login = "N" # Y - Yes , N - No - need to No because of OTP
        is_login = is_login == "Y"
        fyuser = variables.fy_dev_user
        fypass = variables.fy_dev_pass
        if fyuser == "":
            fyuser = ""  # put your custom email and pass fy staging here
            fypass = ""
        station_depart = input("Input Departure: ").upper()
        station_return = input("Input Return: ").upper()
        adult = int(input("Input Adult: "))
        infant = int(input("Input Infant: "))
        flight_fare_type = input("Input Fare type (S) (B) (F): ").upper()   #S - Saver , B - Basic , F - Flex
        target_date = '2025' + input("Input date (0319 = march 19): ")
        if not is_one_way:
            flight_fare_type2 = input("Input Fare type (S) (B) (F): ").upper()
            target_date2 = '2025' + input("Input date (0320 = march 20): ")
        
        
        first_name = 'afwan'
        last_name = 'haziq'
        contact_first_name = 'afwann'
        contact_last_name = 'haziqq'
        contact_email = 'afwan@haziq.com'
        mobile_phone = '01152853044'
        #VARIABLES-------------------------

        
        

        # options = ChromeOptions()
        # options.add_experimental_option("detach", True)  # Prevents browser from closing

        #service = Service("chromedriver.exe")  # Path to your ChromeDriver
        # browser = webdriver.Chrome(options=options)

        browser = getbrowser(browser_code)

        #functions
        if True:
            def scrollClickClass(class_name):
                e = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

                for _ in range(5):  # multiple scrolls
                    browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", e)
                    time.sleep(0.5)

                e = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
                e.click()

            def scrollSearchClass(class_name):
                e = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))

                for _ in range(5):  # multiple scrolls
                    browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", e)
                    time.sleep(0.5)

            def scrollSearchID(id):
                e = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, id)))

                for _ in range(5):  # multiple scrolls
                    browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", e)
                    time.sleep(0.5)

            def clickClass(class_name):
                e = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, class_name)))
                e.click()

            def clickXPath(key):
                e = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, key)))
                e.click()

            def clickID(id):
                e = WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.ID, id)))
                e.click()

            def waitBackdrop():
                WebDriverWait(browser, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, "offcanvas-backdrop")))

            def clickDate(date):
                WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "calendar-day")))
                WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "calendar-day")))
                date_element = browser.find_element(By.XPATH, f"//div[@class='calendar-day' and @data-date3='{date}']")
                date_element.click()

            def sendKeyID(id, key):
                e = browser.find_element(By.ID, id)
                e.send_keys(key)

            def scrollAndType(id, key):
                scrollSearchID(id)
                sendKeyID(id, key)

            def clickBeforeSelected(data_market):
                element = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class, 'before_selected')][@data-market='{data_market}']"))
                )
                print("Clicking the element...")
                element.click()

            def scrollSearchXPath2(key):
                elements = WebDriverWait(browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, key)))

                for e in elements:
                    for _ in range(5):  # Scroll multiple times
                        browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", e)
                        time.sleep(0.5)

                        # Check if element is visible and clickable
                        if e.is_displayed() and e.is_enabled():
                            print("Element found and clickable, clicking now...")
                            e.click()
                            return  # Exit after clicking

            def scrollSearchXPath(key):
                e = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, key)))

                for _ in range(5):  # multiple scrolls
                    browser.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", e)
                    time.sleep(0.5)

            def getFareID(key):
                if key == 'S':
                    return 1
                elif key == 'B':
                    return 2
                elif key == 'F':
                    return 4
                else:
                    return 1

        fydevlink = variables.fydevlink
        username = variables.fy_mweb_user
        password = variables.fy_mweb_pass
        url = f"https://{username}:{password}@{fydevlink}"

        browser.get(url)
        assert 'Firefly' in browser.title

        #login
        if is_login:
            browser.get(url+'/Login')
            sendKeyID('username', fyuser)
            sendKeyID('password', fypass)
            clickID('button_login')

        #search page
        if True:
            if is_one_way:
                clickID('one-way')

            clickClass('departure-station-div')
            scrollSearchID('station'+station_depart)
            clickID('station'+station_depart)

            waitBackdrop()

            clickClass('arrival-station-div')
            scrollSearchID('station'+station_return)
            clickID('station'+station_return)

            waitBackdrop()

            clickClass('calendar-div')
            scrollSearchXPath(f"//div[@class='calendar-day' and @data-date3='{target_date}']")
            clickXPath(f"//div[@class='calendar-day' and @data-date3='{target_date}']")
            # clickDate(target_date)
            if not is_one_way:
                scrollSearchXPath(f"//div[@class='calendar-day' and @data-date3='{target_date2}']")
                clickXPath(f"//div[@class='calendar-day' and @data-date3='{target_date2}']")
            clickClass('calendar-done')

            waitBackdrop()

            clickClass('passengers-div')
            for x in range(adult-1):
                clickClass('adult-plus')
            for x in range(infant):
                clickClass('infant-plus')
            clickClass('passengers-done')

            waitBackdrop()

            clickID('button_search')

        flight_fare_id = getFareID(flight_fare_type)
        if not is_one_way:
            flight_fare_id2 = getFareID(flight_fare_type2)


        #select page
        if True:
            # clickClass('before_selected')
            data_market = 0
            scrollSearchXPath(f"//div[contains(@class, 'before_selected')][@data-market='{data_market}']")
            clickXPath(f"//div[contains(@class, 'before_selected')][@data-market='{data_market}']")
            scrollSearchXPath(f"//div[@class='selectFareButton' and @onclick='selectFlightProduct(this, {flight_fare_id});']")
            clickXPath(f"//div[@class='selectFareButton' and @onclick='selectFlightProduct(this, {flight_fare_id});']")

            if not is_one_way:
                data_market = 1
                scrollSearchXPath(f"//div[contains(@class, 'before_selected')][@data-market='{data_market}']")
                clickXPath(f"//div[contains(@class, 'before_selected')][@data-market='{data_market}']")
                scrollSearchXPath(f"//div[@class='selectFareButton' and @onclick='selectFlightProduct(this, {flight_fare_id2});']")
                clickXPath(f"//div[@class='selectFareButton' and @onclick='selectFlightProduct(this, {flight_fare_id2});']")

            clickID('button_continue')

        #passenger page
        if not is_login:
            scrollAndType('first_name1', first_name)
            scrollAndType('last_name1', last_name)
            scrollAndType('contact_first_name', contact_first_name)
            scrollAndType('contact_last_name', contact_last_name)
            scrollAndType('contact_email', contact_email)
            scrollAndType('contact_mobile_phoneINPUT', mobile_phone)
            #click ID 'agreement'
        if True:
            scrollSearchID('agreement')
            clickID('agreement')
            clickID('button_continue')

        #elem.send_keys('seleniumhq' + Keys.RETURN)
        #elem.send_keys('seleniumhq')
        print(f"Done")
        #browser.quit()

    #CELIK TAFSIR
    elif program == "CT":
        import urllib.request #url getter
        import re #get from pattern
        import os
        #from bs4 import BeautifulSoup
        import platform
        isProd = True

        ct_link = variables.ct_link

        if isProd:
            req = urllib.request.urlopen(ct_link)
            data = req.read()

        index = data.find("Senarai Surah".encode("utf-8"))

        # Get the substring from the index to the end of the string
        substring = data[index:len(data)]

        #get all list
        indexS = substring.find("<ul>".encode("utf-8"))
        indexE = substring.find("</ul>".encode("utf-8"))
        substring2 = substring[indexS:indexE+5]

        #get all list of surah
        index3 = substring2.find("al-fatihah/".encode("utf-8"))
        index4 = substring2.find("an-nas/".encode("utf-8"))
        ss = substring2[index3-90 : index4+20]
        decoded_ss = ss.decode("utf-8")

        #get all href in Array
        nums = re.findall(r'href="(.+?)"', decoded_ss)

        #print(nums[0])

        #Date
        today = datetime.today().strftime("%Y%m%d-%H%M")

        #get all link and store it inside .txt file
        if False :
            txt = ""
            for f in nums:
                txt += (f + "\n")

            filename = "output python/output" + today + ".txt"
            with open(filename, "a") as f:
                print(txt, file=f)

            exit()


        #links
        txt = ""
        for link in nums:
            req = urllib.request.urlopen(link)
            data = req.read()

            print(link)

            #idx = data.find("entry-title")
            #soup = BeautifulSoup(data, 'html.parser')
            #get all Surah's inside pages
            data = str(data)
            idx = data.find('display-posts-listing')
            s = data[idx:len(data)]
            idx2 = s.find('</ul>')
            s = s[0:idx2]
            #print(s)

            #get all href in Array
            pages = re.findall(r'href="(.+?)"', s)
            # print(pages)

            #put all inside txt variable
            for f in pages:
                txt += (f + " ")
            
            # print(txt)
            # exit()

            #albaqarah ada 3 part
            if (not (link == f'{ct_link}surah-002-al-baqarah/' or link == f'{ct_link}surah-002-bahagian-2/')):
                #remove last space
                txt = txt[:-1]
                #add newline foreach surah
                txt += ";\n"

        #remove last space
        # txt = txt[:-1]
        # txt += ";\n"

        #20-Feb-2025
        date = datetime.now()
        formatted_date = date.strftime('%d-%b-%Y')
        txt += formatted_date

        #create file
        file_name = "output python/output" + today + ".txt"
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        with open(file_name, "w") as f:
            print(txt, file=f)

        print(f"Successfully created file {file_name}")

        # Open the file location
        file_path = os.path.abspath(file_name)
        if openfileorfolder == "FD":
            file_path = os.path.dirname(file_path)
        
        open_file_path(file_path)
        # os.startfile(file_path)  # Windows
        # os.system(f'open "{file_path}"') # macOS
        # os.system(f'xdg-open "{file_path}"') # Linux

        # Open the link in the default web browser
        import webbrowser
        webbrowser.open("https://github.com/C24-S60348/C24-S60348.github.io/blob/main/CelikTafsirLinkData/data.txt")


        exit()

    #TELEGRAM BOT
    elif program == "TB":
        # needPass()
        import json
        import requests

        # VARIABLES -----------------
        if info3 == None:
            code2 = "Afwan" #Custom to
            info3 = "custom" #Custom message
        #VARIABLES ------------------

        token = variables.tb_token
        token_fy = variables.tb_token_fy
        tb_token = ""

        if code2 == "Afwan":
            CHAT_ID = "222338004" # Celik Tafsir website update Warning : -4723012335 , Study with Afwan : -4515480710 , Afwan : 222338004
            tb_token = token
        elif code2 == "Study":
            CHAT_ID = "-4515480710"
            tb_token = token
        elif code2 == "Sara":
            CHAT_ID = "6238256254"
            tb_token = token
        elif code2 == "FYSFTP":
            CHAT_ID = "-4808008264"
            tb_token = token_fy
        

        MESSAGE = info3

        # Telegram API URL
        url = f"https://api.telegram.org/bot{tb_token}/sendMessage"
        # data={"chat_id": CHAT_ID, "text": MESSAGE}
        # data = json.dumps(data).encode("utf-8") #change to json
        # headers = {"Content-Type":"application/json"}
        #response = http.request("POST", url, body=data, headers=headers)

        # req = ur.Request(url, data=data, headers=headers, method="POST")
        # with ur.urlopen(req) as response:
        #     status_code = response.getcode()
        #     response = response.read().decode("utf-8")



        # Send the message
        response = requests.post(url, data={"chat_id": CHAT_ID, "text": MESSAGE})
        status_code = response.status_code

        # Check response
        #if response.status_code == 200:
        if status_code == 200:
            print("Message sent successfully!")
        else:
            print(f"Failed to send message: {response.text}")

    #WEB SCRAPING WITH LOGIN FOR afwanhaziq.pythonanywhere.com
    elif program == "WS":

        import urllib.request #url getter
        import urllib.parse
        import re #get from pattern
        import http.cookiejar
        import os
        from bs4 import BeautifulSoup
        import datetime

        def login_and_get_data(url, data, cookie_jar=None):

            encoded_data = urllib.parse.urlencode(data).encode()
            if not cookie_jar:
                cookie_jar = http.cookiejar.CookieJar()
            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
            urllib.request.install_opener(opener)
            req = urllib.request.Request(url, data=encoded_data, method='POST')
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            try:
                with urllib.request.urlopen(req) as response:
                    response_data = response.read().decode()
                    return response_data
            except urllib.error.HTTPError as e:
                print(f"Request failed with status code: {e.code}")
                return None

        def count_tags(html_string, tag_name):
            soup = BeautifulSoup(html_string, 'html.parser')
            li_tags = soup.find_all(tag_name)
            return len(li_tags)

        #initialize url, data, & cookie
        url = 'https://afwanhaziq.pythonanywhere.com/login'
        email = variables.afwanemail
        data = {'email': email, 'password': 'test12345', 'submit':''}
        cookie_jar = http.cookiejar.CookieJar()

        response_data = login_and_get_data(url, data, cookie_jar)
        #print(response_data)

        if response_data:
            txt = ""
            soup = BeautifulSoup(response_data, 'html.parser')

            # Find the specific ul element
            li_tags = soup.find_all('li', class_="list-group-item")
            li_count = len(li_tags)
            txt += f"Total post: {li_count}\n\n"
            print(f"Number of <li> tags with class 'list-group-item': {li_count}")
            count = 0
            for li_tag in li_tags:
                count += 1
                posting_data = li_tag.find('div')
                if posting_data:
                    post_text = posting_data.text.strip()
                    txt += f"Post {count}: {post_text}\n"
                    print(f"Post {count}: {post_text}")
                #print(posting_data)
                #print(li_tag.text.strip())

            #GET ALL DATA THEN PUT IT INSIDE TXT FILE ==========================================
            today = datetime.datetime.now().strftime("%Y%m%d-%H%M")
            print(today)

            filename = "/home/AfwanProductions/mysite/cron_output/output" + today + ".txt"
            os.makedirs(os.path.dirname(filename), exist_ok=True) #make dir if not exist

            #note- "a" is append, "w" is overwrite
            if os.path.exists(filename):
                with open(filename, "w") as f:
                    print(txt, file=f)
            else:
                with open(filename, "a") as f:
                    print(txt, file=f)

        else:
            print("Login failed or an error occurred.")

    #AI auto message test
    elif program == "AAI":
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.common.alert import Alert
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.edge.options import Options as EdgeOptions
        from selenium.webdriver.chrome.service import Service as ChromeService
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.edge.service import Service as EdgeService
        from webdriver_manager.chrome import ChromeDriverManager
        from webdriver_manager.firefox import GeckoDriverManager as FirefoxDriverManager
        from webdriver_manager.microsoft import EdgeChromiumDriverManager as EdgeDriverManager
        from webdriver_manager.opera import OperaDriverManager
        # from webdriver_manager.drivers import edge
        import time

        browser = getbrowser(browser_code)
        url = f"https://deepai.org/chat"

        browser.get(url)

        text = "Hello guys, i am a man with testing testing , how can i help you? eh? you're an AI chatbot, sorry, i think,"

        time.sleep(1)
        e = browser.find_element(By.CLASS_NAME, "chatbox")
        e.send_keys(text)
        time.sleep(1)
        # e = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, "//button[@data-testid='send-button']")))
        e = browser.find_element(By.ID, "chatSubmitButton")
        e.click()

    #CRON RUN
    elif program == "CRPC" or program == "CRO" or program == "CRM":
        #CRPC - Cron Run PC , CRO - Cron Run Once , CRM - Cron Run Multiple
        import platform
        #from bs4 import BeautifulSoup
        import re

        def run_cron():
            print("Run check...")
            cronchecklink = variables.cronchecklink
            url = cronchecklink

            req = ur.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with ur.urlopen(req) as response:
                 response = response.read().decode("utf-8")

            def get_html_true(class_name, html):
                pattern = rf'<p class="{class_name}">(.*?)</p>'
                match = re.search(pattern, html)
                if match:
                    if match.group(1) == "True":
                        return True
                return False
            def get_html(class_name, html):
                pattern = rf'<p class="{class_name}">(.*?)</p>'
                match = re.search(pattern, html)
                if match:
                    return match.group(1)
                return ""

            print(response)

            timenowKL = get_html("timenowKL", response)
            timenowKL = Decimal(timenowKL)
            global last_run_times
            cans = {}
            for key in last_run_times.keys():
                cans[key] = get_html_true(f"min{key}", response)

            print("Done check")

            for key in cans.keys():
                if cans[key]:
                    load_min(key)


        def load_min(min):
            global program
            print (f"program = {program}")
            print(f"---------------------- every {min} min")
            if min == "0.5":
                print("")
            if min == "1":
                print("")
                # run_function("RP")
            if min == "2":
                print("")
                # logging.info(f"Run RP")
                run_function("RP")
            if min == "3":
                print("")
            if min == "5":
                print("")
            if min == "10":
                print("")
            if min == "30":
                print("")
            if min == "60":
                print("")
                # logging.info(f"Run CSFTP")
                run_function("CSFTP")
            print(f"---------------------- every {min} min")

        run_cron()

        if program == "CRPC":
            while True:
                totalsec = 30
                countsec = 10
                for remaining in range(0, totalsec, countsec): #sleep 5min
                    esec = remaining
                    print(f"\rElapsed {esec}s ...", end="", flush=True)
                    time.sleep(countsec)
                run_cron()
        elif program == "CRM":
            while True:
                time.sleep(30)
                run_cron()

    #CHECK SFTP
    elif program == "CSFTP":
        url = variables.csftp_link
        try:
            print("running CSFTP...")
            req = ur.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with ur.urlopen(req) as response:
                 response = response.read().decode("utf-8")
            html_data = response
            #response = requests.get(url)
            #response = http.request("GET", url)
            #response = response.data.decode("utf-8")
            #html_data = response
            #print(html_data)
            if ('error' in html_data):
                run_function("TB", "FYSFTP", f"Error in SFTP  \n  \n  {html_data} \n \n on payment_feed_extract/cron_test_sftp.php")
            print (html_data)
            print("done CSFTP")

        except Exception as e:
            print(f"Failed to load {url} - Error: {e}")

    #Reminder Parking
    elif program == "RP":

        print("running RP...")

        now = datetime.now(timezone.utc)
        gmt8 = timezone(timedelta(hours=8))
        now = now.astimezone(gmt8)

        current_time = now.strftime("%H:%M")
        weekdays = now.weekday() < 5  # Monday to Friday are considered weekdays (0-4)

        print(f"now is {current_time}")



        # Load reminders from JSON

        reminders = [
            {"time_range": ["08:58", "09:01"], "message": "Bayar parking pagii https://play.google.com/store/apps/details?id=my.com.lits.flexiparking2", "days": "weekdays", "to": "Afwan"}
            ,{"time_range": ["13:58", "14:01"], "message": "Bayar parking petanggg https://play.google.com/store/apps/details?id=my.com.lits.flexiparking2", "days": "weekdays", "to": "Afwan"}
            ,{"time_range": ["20:50", "21:00"], "message": "Cakap SAYANG kat saraa", "days": "all", "to": "Afwan"}
            ,{"time_range": ["20:50", "20:53"], "message": "jangan lupa cakap sayang kat afwannn", "days": "all", "to": "Sara"}
            # ,{"time_range": ["16:31", "16:35"], "message": "test test", "days": "all", "to": "Afwan"}
        ]

        for reminder in reminders:
            if (weekdays and reminder["days"] == "weekdays") or reminder["days"] == "all":
                if reminder["time_range"][0] <= current_time <= reminder["time_range"][1]:
                    run_function("TB", reminder["to"], reminder["message"])


        print("done RP")
   
    #Check message
    elif program == "CM":
        import json
        import requests

        tb_token = variables.tb_token
        url = f"https://api.telegram.org/bot{tb_token}/getUpdates"
        target_id = "222338004"
        target_username = "sra2931" #Afwanhz , sra2931
        search_by = "CM" # ID , US - username , CM - Command
        try:
            print("running CM...")
            response = requests.get(url)
            data = response.json()
            for update in data.get("result", []):
                message = update.get("message", {})
                user = message.get("from", {})

                # Check if the message is from the target user
                if search_by == "ID":
                    if str(user.get("id")) == target_id:
                        id = user.get("id", "Unknown")
                        username = user.get("username", "Unknown")
                        text = message.get("text", "[No text message]")
                        print(f"Id: {id} | User: {username} | Message: {text}")

                elif search_by == "US":
                    if str(user.get("username")) == target_username:
                        id = user.get("id", "Unknown")
                        username = user.get("username", "Unknown")
                        text = message.get("text", "[No text message]")
                        print(f"Id: {id} | User: {username} | Message: {text}")

                elif search_by == "CM":
                    id = user.get("id", "Unknown")
                    username = user.get("username", "Unknown")
                    text = message.get("text", "[No text message]")
                    date = message.get("date", "[No date]") #Unique
                    # print(f"Id: {id} | User: {username} | Message: {text}")

                    #Command


                    if "/command1" in text:
                        if "/command1@I_Awesome_OT_Bot" in text:
                            print(f"{username} | date:{date} | command : {text}")
                        else:
                            print(f"{username} | date:{date} | command private : {text}")

        except Exception as e:
            print(f"Error: {e}")

        except Exception as e:
            print(f"Failed to load {url} - Error: {e}")

    #Flask website afwanproductions
    elif program == "FW":
        
        from flask import Flask
        from flask_page.apitest import apitest_bp
        from flask_page.connect_to_db import connect_to_db
        from flask_page.api_bp import api_bp
        from flask_page.home import home_bp
        from flask_page.croncheck import croncheck_bp
        from flask_page.executejsonv2 import executejsonv2_bp
        from flask_page.pelajar_data import pelajar_data_bp
        
        # from flask_page.publicvar import last_run_times
        global app
        app.register_blueprint(apitest_bp)
        app.register_blueprint(api_bp)
        app.register_blueprint(home_bp)
        app.register_blueprint(croncheck_bp)
        app.register_blueprint(executejsonv2_bp)
        app.register_blueprint(pelajar_data_bp)
        
        # Start the app using Uvicorn
        if __name__ == '__main__':
            app.run(host="0.0.0.0", port=5000, debug=True)

    elif program == "QT":
        import os
        import json
        import time
        import asyncio
        from datetime import datetime, timedelta, timezone
        import aiomysql
        import variables 
        from contextlib import asynccontextmanager
        from quart import Quart, request, jsonify, render_template, render_template_string
        from quart_cors import cors

        app = Quart(__name__)
        app = cors(app, allow_origin="*")
        
        
        # Async context manager for MySQL connection
        @asynccontextmanager
        async def connect_to_db():
            connection = await aiomysql.connect(
                host="AfwanProductions.mysql.pythonanywhere-services.com",
                user="AfwanProductions",
                password="afwan987",
                db="AfwanProductions$afwan_db",
                loop=asyncio.get_event_loop()
            )
            try:
                async with connection.cursor() as cursor:
                    yield cursor, connection
            except aiomysql.MySQLError as err:
                print(f"Error connecting to database: {err}")
                raise
            finally:
                connection.close()
        
        # Test Route
        @app.route('/api/test', methods=['GET', 'POST', 'OPTIONS'])
        async def test():
            return jsonify({"message": "Query executed successfully"}), 200
        
        # Handle Request (Non-DB)
        @app.route('/api', methods=['GET', 'POST'])
        async def handle_request():
            text = str(request.args.get('input'))  # ?input=a
            character_count = len(text)
            data_set = {'input': text, 'timestamp': time.time(), 'character_count': character_count}
            json_dump = json.dumps(data_set)
            return json_dump
        
        # QUERY EXECUTER JSON V2
        @app.route('/api/executejsonv2', methods=['GET', 'POST'])
        async def execute_query_json_v2():
            try:
                # Synchronously read JSON data
                data = request.get_json()
        
                if 'query' not in data:
                    return jsonify({"error": "query parameter is required"}), 400
        
                if 'password' not in data:
                    return jsonify({"error": "password parameter is required"}), 400
        
                sql = data['query']
                password = data['password']
        
                if password == variables.website_pass:
                    try:
                        async with connect_to_db() as (cursor, connection):
                            # Execute the SQL query asynchronously
                            await cursor.execute(sql)
        
                            # Check if the query returns rows (SELECT query)
                            if sql.strip().lower().startswith("select"):
                                columns = [column[0] for column in cursor.description]
                                rows = await cursor.fetchall()  # Fetch all rows asynchronously
                                results = [dict(zip(columns, row)) for row in rows]
                                return jsonify({"results": results}), 200
                            else:
                                # Commit for insert, update, delete
                                await connection.commit()
                                return jsonify({"message": "Query executed successfully"}), 200
                    except aiomysql.MySQLError as db_err:
                        return jsonify({"error": f"Database error: {db_err}"}), 500
                else:
                    return jsonify({"error": "Incorrect password"}), 401
            except Exception as e:
                return jsonify({"error": f"An unexpected error occurred: {e}"}), 500



        
        # Serve HTML Pages
        @app.route("/croncheck")
        async def cron_check():
            now = datetime.now(timezone.utc)
            gmt8 = timezone(timedelta(hours=8))
            current_time_raw = now.astimezone(gmt8)
            current_time_timestamp = current_time_raw.timestamp()
        
            timenowKL = current_time_timestamp
            times = {}
            cans = {}
        
            for key in last_run_times.keys():
                times[key] = datetime.fromtimestamp(last_run_times[key], tz=gmt8).strftime('%Y-%m-%d %I:%M %p')
                if (current_time_timestamp - last_run_times[key]) > ((float(key)*30)-10):
                    last_run_times[key] = current_time_timestamp
                    cans[key] = True
                else:
                    cans[key] = False
        
            current_time = current_time_raw.strftime('%Y-%m-%d %I:%M %p')
        
            html = f"""
                <!DOCTYPE html>
                <html>
                <head><title>Cron Check</title></head>
                <body>
                    <h2>Cron Check</h2>
                    <p>Current time: {current_time}</p>
                    """ 
        
            for key in times.keys():
                html += f'<p>Last {key}min: {times[key]}</p>'
            for key in times.keys():
                html += f'<p class="min{key}">{cans[key]}</p>'
        
            html += f"""
                    <p class="timenowKL">{timenowKL}</p>
                </body>
                </html>
            """
        
            return await render_template_string(html)
        
        TXT_FILES_DIR = "/home/AfwanProductions/mysite/cron_output/"
        @app.route("/")
        async def index():
            txt_files = [f for f in os.listdir(TXT_FILES_DIR) if f.endswith(".txt")]
            txt_files.sort(reverse=True)
            now = datetime.now(timezone.utc)
            gmt8 = timezone(timedelta(hours=8))
            current_time = now.astimezone(gmt8).strftime('%Y-%m-%d %I:%M %p')
            last_run_time = datetime.fromtimestamp(max(last_run_times.values()), tz=gmt8).strftime('%Y-%m-%d %I:%M %p')
            html = f"""
                <!DOCTYPE html>
                <html>
                <head><title>TXT Files</title></head>
                <body>
                    <h2>TXT Files from afwanhaziq.pythonanywhere.com</h2>
                    <p>Current time: {current_time}</p>
                    <p>Last run cron: {last_run_time}</p>
                    <ul>"""
            
            for file in txt_files:
                html += f"<li><a href='/view/{file}'>{file}</a></li>"
            html += """
                    </ul>
                </body>
                </html>
            """
            return await render_template_string(html, files=txt_files)
        
        @app.route("/view/<filename>")
        async def view_file(filename):
            filepath = os.path.join(TXT_FILES_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    content = f.read()
                
                html = f"""
                    <!DOCTYPE html>
                    <html>
                    <head><title>{filename}</title></head>
                    <body>
                        <h1>{filename}</h1>
                        <pre>{content}</pre>
                    </body>
                    </html>
                """
                return await render_template_string(html, content=content, filename=filename)
            except FileNotFoundError:
                return "File not found", 404
        
        # Start the app using Uvicorn
        if __name__ == '__main__':
            app.run(debug=True)

    #Run Bot Polling
    elif program == "BP":
        #pip install python-telegram-bot --upgrade
        #pip install apscheduler

        from telegram import Update
        from telegram.ext import Application, CommandHandler, CallbackContext #, MessageHandler, filters
        from apscheduler.schedulers.background import BackgroundScheduler
        import datetime
        import asyncio
        from functools import partial

        TOKEN = variables.tb_token
        scheduler = BackgroundScheduler()
        scheduler.start()

        #reminder--------------------
        async def reminder_command(update: Update, context: CallbackContext):
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
            user_name = update.effective_user.username
            message_parts = update.message.text.split(maxsplit=2)  

            if len(message_parts) < 3:
                await update.message.reply_text(
                    "Usage: /reminder <time> <message>\nExamples:\n- /reminder 2pm lunch\n- /reminder 2:30pm meeting"
                )
                return

            timing = message_parts[1]
            reminder_text = message_parts[2]

            # Try parsing time
            reminder_time = None
            for time_format in ("%I:%M%p", "%I%p"):
                try:
                    reminder_time = datetime.datetime.strptime(timing, time_format).time()
                    break
                except ValueError:
                    continue

            if reminder_time is None:
                await update.message.reply_text("Invalid time format! Use:\n- `2pm`\n- `2:30pm`\n- `10am`\n- `10:45pm`")
                return

            tz_gmt8 = datetime.timezone(datetime.timedelta(hours=8))
            now = datetime.datetime.now(tz=tz_gmt8).time()

            if reminder_time <= now:
                await update.message.reply_text("The time must be in the future!")
                return

            run_time = datetime.datetime.combine(datetime.date.today(), reminder_time).replace(tzinfo=tz_gmt8)

            # Correct way to add async function to scheduler
            scheduler.add_job(
                partial(asyncio.run, send_reminder(context.application, chat_id, reminder_text)),
                "date",
                run_date=run_time
            )

            print(f"{user_name} : Reminder set for {timing}: {reminder_text}")
            await update.message.reply_text(f"Reminder has set")

        async def send_reminder(application: Application, chat_id, message):
            await application.bot.send_message(chat_id=chat_id, text=f"🔔 Reminder: {message}")

        async def start(update: Update, context: CallbackContext):
            user_id = update.effective_user.id  # Get User ID
            user_message = update.message.text
            print(f"User ID: {user_id}")
            print(f"User Message: {user_message}")
            await update.message.reply_text("Hai sara, laju tak saya reply, hihi, sorry haritu ngantuukk")

        async def help_command(update: Update, context: CallbackContext):
            await update.message.reply_text("Available commands: /start")
        async def sayang_afwan(update: Update, context: CallbackContext):
            await update.message.reply_text("SAYANG SARA JUGAKKKKKKKK")
        async def sayang_sara(update: Update, context: CallbackContext):
            await update.message.reply_text("YESHH! AFWAN PATUT DISAYANGI")

        async def handle_messages(update: Update, context: CallbackContext):
            user_id = update.effective_user.id
            user_name = update.effective_user.username
            user_message = update.message.text
            print(f"Message from {user_name} : {user_message}")

            # Example: If user says "hello", bot replies "Hello too!"
            if "hello" in user_message.lower():
                await update.message.reply_text("Hello too!")
            if "hai afwan" in user_message.lower():
                await update.message.reply_text("Hai saraaa -Afwan 2025")
            # else:
            #     await update.message.reply_text(f"Afwan received: {user_message}")

        def main():
            app = Application.builder().token(TOKEN).build()

            # Add command handlers
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help_command))
            app.add_handler(CommandHandler("sayangafwan", sayang_afwan))
            app.add_handler(CommandHandler("sayangsara", sayang_sara))

            # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
            app.add_handler(CommandHandler("reminder", reminder_command))

            print("Bot is running...")

            # Start long polling
            app.run_polling()

        if __name__ == "__main__":
            main()

    #Summary today log
    elif program == "STL":
        today = datetime.now().strftime("%Y-%m-%d")
        log_summary = []

        with open("cron_log.txt", "r") as file:
            for line in file:
                if today in line:
                    log_summary.append(line.strip())

        
        now = datetime.now(timezone.utc)
        gmt8 = timezone(timedelta(hours=17.81))
        current_time_raw = now.astimezone(gmt8)
        current_time_timestamp = current_time_raw.timestamp()
        current_time = current_time_raw.strftime('%Y-%m-%d %I:%M %p')
        current_time2 = current_time_raw.strftime('%I:%M %p')
        if ("11:59 PM" <= current_time2 <= "12:01 AM"):
            #show summary
            today = datetime.now().strftime("%Y-%m-%d")
            log_summary = []

            with open("cron_log.txt", "r") as file:
                for line in file:
                    if today in line:
                        log_summary.append(line.strip())
            summary = "\n".join(log_summary) if log_summary else "No logs for today."
            run_function("TB", "Afwan", f"Summary of today's log:\n{summary}")
        print(current_time2)
        
    #expo react native bundle release
    elif program == "EXPO" or program == "EXPOAFTERCLEAN" or program == "EXPOAFTERBUNDLE":
        import textwrap

        print(textwrap.dedent(r"""
            README: This will run ./gradlew bundleRelease , please make sure:
                              
            Inside android\build.gradle:
                              
            ext {
                buildToolsVersion = findProperty('android.buildToolsVersion') ?: '35.0.0'
                minSdkVersion = Integer.parseInt(findProperty('android.minSdkVersion') ?: '24')
                compileSdkVersion = Integer.parseInt(findProperty('android.compileSdkVersion') ?: '35')
                targetSdkVersion = Integer.parseInt(findProperty('android.targetSdkVersion') ?: '34')
                kotlinVersion = findProperty('android.kotlinVersion') ?: '1.9.25'
                ndkVersion = "26.1.10909125"  ---important
            }
            repositories {
                google()
                mavenCentral()
            }
            dependencies {
                classpath('com.android.tools.build:gradle')
                classpath('com.facebook.react:react-native-gradle-plugin')
                classpath('org.jetbrains.kotlin:kotlin-gradle-plugin')
            }

            if want to use gradle 8.10.2:
            distributionUrl=https\://services.gradle.org/distributions/gradle-8.10.2-all.zip
            
            dependencies {
                classpath("com.android.tools.build:gradle:8.10.2") 
                ...
            }


            """
        ))

        import os
        import subprocess
        import sys
        import datetime
        import requests

        #Put directory app
        # projectloc = input("Please input project directory location: ")
        projectname = "Escabee"
        projectloc = r"C:\escabee-mobile"
        projectloc += r"\android" 

        # go to directory
        if True:
            if os.path.exists(projectloc):
                os.chdir(projectloc)
                print(f"Changed directory to: {os.getcwd()}")
            else:
                print(f"Warning: The specified directory '{projectloc}' does not exist.")

            # Check 
            if not os.path.exists("gradle"):
                print("Error: This is not an Android folder. You cannot run gradlew here.")
                sys.exit(1)

        def run_command(command):
            """Runs a command in the shell and waits for it to complete."""
            process = subprocess.Popen(command, shell=True)
            process.communicate()
            if process.returncode != 0:
                print(f"Error: Command '{command}' failed.")
                sys.exit(1)

        # Gradlew clean , bundleRelease
        if program == "EXPO" or program == "EXPOAFTERCLEAN":
            if program == "EXPO":
                print(r"Running: .\gradlew clean")
                run_command(r".\gradlew clean")

            print(r"Running: .\gradlew bundleRelease")
            run_command(r".\gradlew bundleRelease")

        # If already has AAB file, run this
        if True:
            # goto AAB file
            if True:
                output_dir = "app/build/outputs/bundle/release/"
                if os.path.exists(output_dir):
                    os.chdir(output_dir)
                    print(f"Changed directory to: {os.getcwd()}")
                else:
                    print(f"Warning: Output directory '{output_dir}' not found.")
            
            run_command("dir")

            bundletool_file = "bundletool-all-1.18.1.jar"
            keystore_file = "my-release-key.jks"
            aab_file = "app-release.aab"
            apks_file = datetime.datetime.now().strftime("my_app%d%b.apks")
            # Download bundletool
            if True:
                bundletool_url = "https://github.com/google/bundletool/releases/download/1.18.1/bundletool-all-1.18.1.jar"
                if not os.path.exists(bundletool_file):
                    print(f"Downloading {bundletool_file}...")
                    response = requests.get(bundletool_url, stream=True)
                    with open(bundletool_file, "wb") as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)
                print("Download completed.")

            # Generate Keystore
            if True:
                if not os.path.exists(keystore_file):
                    print("Generating keystore...")
                    run_command("keytool -genkeypair -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias")
                    print("Keystore generated.")

            # Build APK
            if True:
                if os.path.exists(apks_file):
                    print(f"Deleting existing {apks_file}...")
                    os.remove(apks_file)
                print("Building APKs using bundletool...")
                run_command(f'java -jar {bundletool_file} build-apks --bundle={aab_file} --output={apks_file} --mode=universal --ks={keystore_file} --ks-pass=pass:123456 --ks-key-alias=my-key-alias --key-pass=pass:123456')
                print(f"APKs successfully built as {apks_file}.")
            
            #Extract APK
            if True:
                if not os.path.exists(apks_file):
                    print(f"Error: {apks_file} not found.")
                    sys.exit(1)
                    
                print(f"Extracting {apks_file}...")
                extracted_dir = "extracted_apks"
                if not os.path.exists(extracted_dir):
                    os.makedirs(extracted_dir)
                # run_command(f'unzip -o "{apks_file}" -d {extracted_dir}')
                run_command(f'tar -xf "{apks_file}" -C {extracted_dir}')

            # Rename APK
            if True:
                universal_apk_path = os.path.join(extracted_dir, "universal.apk")
                if os.path.exists(universal_apk_path):
                    formatted_date = datetime.datetime.now().strftime("Escabee_%d_%b_%Y_%I%M%p.apk")
                    #Rename
                    # new_apk_name = os.path.join(os.getcwd(), formatted_date)
                    new_apk_name = os.path.join(extracted_dir, formatted_date)
                    os.rename(universal_apk_path, new_apk_name)
                    
                    print(f"Renamed 'universal.apk' to '{formatted_date}'")
                else:
                    print("Error: 'universal.apk' not found in extracted_apks.")
                    sys.exit(1)
            
            #go to folder
            if True:
                file_path = os.path.dirname(universal_apk_path) 
                open_file_path(file_path)

    #proxy server
    elif program == "PROXY":
        import requests
        from flask import Flask, request, Response

        app = Flask(__name__)

        @app.route('/proxy')
        def proxy():
            target_url = request.args.get('url')

            if not target_url:
                return Response("Missing 'url' parameter", status=400)

            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
                }
                response = requests.get(target_url, headers=headers)

                # Create a response with CORS headers
                proxy_response = Response(response.content, status=response.status_code)
                proxy_response.headers["Access-Control-Allow-Origin"] = "*"
                proxy_response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                proxy_response.headers["Access-Control-Allow-Headers"] = "Content-Type"

                return proxy_response

            except requests.RequestException as e:
                return Response(f"Error: {e}", status=500)

        if __name__ == "__main__":
            app.run(host="0.0.0.0", port=5000)

    #proxy server with edit html
    elif program == "PROXYWE":
        import requests
        from flask import Flask, request, Response
        from bs4 import BeautifulSoup  # Requires `pip install beautifulsoup4`

        app = Flask(__name__)

        @app.route('/proxy')
        def proxy():
            target_url = request.args.get('url')

            if not target_url:
                return Response("Missing 'url' parameter", status=400)

            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
                }
                response = requests.get(target_url, headers=headers)

                # Check content type
                content_type = response.headers.get("Content-Type", "")
                if "text/html" in content_type:  # Only modify HTML pages
                    soup = BeautifulSoup(response.text, "html.parser")

                    # Rewrite all anchor tags <a href="...">
                    for tag in soup.find_all("a", href=True):
                        if tag["href"].startswith("http"):  # Only modify absolute URLs
                            tag["href"] = f"/proxy?url={tag['href']}"

                    # Rewrite all form actions <form action="...">
                    for tag in soup.find_all("form", action=True):
                        if tag["action"].startswith("http"):
                            tag["action"] = f"/proxy?url={tag['action']}"

                    modified_html = str(soup)
                else:
                    modified_html = response.text  # Serve non-HTML files as-is

                # Create a response with CORS headers
                proxy_response = Response(modified_html, status=response.status_code)
                proxy_response.headers["Content-Type"] = content_type
                proxy_response.headers["Access-Control-Allow-Origin"] = "*"
                proxy_response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
                proxy_response.headers["Access-Control-Allow-Headers"] = "Content-Type"

                return proxy_response

            except requests.RequestException as e:
                return Response(f"Error: {e}", status=500)

        if __name__ == "__main__":
            app.run(host="0.0.0.0", port=5000)

    #Bundle expo
    elif program == "BEXPO":
        import subprocess

        def ask(prompt, default=""):
            script = f'display dialog "{prompt}" default answer "{default}" with title "Build Script"'
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True
            )
            # Result comes like: "button returned:OK, text returned:escabee-mobile"
            return result.stdout.strip().split(":")[-1].split(",")[-1].replace("text returned:", "").strip()

        # Ask project
        choice1 = ask("Enter project folder (1=escabee-mobile, 2=purgo-mobile)", "1")
        mapping1 = {
            "1": "escabee-mobile",
            "2": "purgo-mobile",
        }
        project = mapping1.get(choice1, "escabee-mobile")

        # Ask build type
        choice = ask("Enter build type (1=bundleRelease, 2=assembleRelease, 3=assembleDebug)", "1")

        mapping = {
            "1": "bundleRelease",
            "2": "assembleRelease",
            "3": "assembleDebug",
        }
        task = mapping.get(choice, "assembleRelease")

        # Set Node path
        import os
        os.environ["PATH"] = f"{os.environ['HOME']}/.nvm/versions/node/v22.14.0/bin:" + os.environ["PATH"]

        # Change dir
        project_path = os.path.expanduser(f"~/Documents/github/{project}/android")
        os.chdir(project_path)

        # Run Gradle
        print(f"Running ./gradlew {task} in {project_path}")
        subprocess.run(["./gradlew", task])

        subprocess.run(["open", f"{project_path}/app/build/outputs"])
    
    #Bundle expo2
    elif program == "BEXPO2":
        import subprocess
        import sys
        import os

        project = sys.argv[2] #escabee-mobile, purgo-mobile
        task = sys.argv[3] #assembleRelease, bundleRelease, assembleDebug
        project_path = os.path.expanduser(f"~/Documents/github/{project}/android")
        os.chdir(project_path)

        # Set Node path
        os.environ["PATH"] = f"{os.environ['HOME']}/.nvm/versions/node/v22.14.0/bin:" + os.environ["PATH"]

        # Change dir
        project_path = os.path.expanduser(f"~/Documents/github/{project}/android")
        os.chdir(project_path)

        # Run Gradle
        print(f"Running ./gradlew {task} in {project_path}")
        subprocess.run(["./gradlew", task])

        subprocess.run(["open", f"{project_path}/app/build/outputs"])
    
    #Bundle flutter
    elif program == "BFT":
        import subprocess
    
        def ask(prompt, default=""):
            script = f'display dialog "{prompt}" default answer "{default}" with title "Build Script"'
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True
            )
            # Result comes like: "button returned:OK, text returned:escabee-mobile"
            return result.stdout.strip().split(":")[-1].split(",")[-1].replace("text returned:", "").strip()

        # Ask project
        choice1 = ask("Enter project folder (1=celiktafsirv4, 2=escabee-mobile)", "1")
        mapping1 = {
            "1": "celiktafsirv4",
            "2": "escabee-mobile",
        }
        project = mapping1.get(choice1, "celiktafsirv4")

        # Ask build type
        choice = ask("Enter build type (1=bundleRelease, 2=assembleRelease, 3=assembleDebug)", "1")

        mapping = {
            "1": "bundleRelease",
            "2": "assembleRelease",
            "3": "assembleDebug",
        }
        task = mapping.get(choice, "assembleRelease")

        # Set Node path
        import os
        os.environ["PATH"] = f"{os.environ['HOME']}/.nvm/versions/node/v22.14.0/bin:" + os.environ["PATH"]

        # Change dir
        project_path = os.path.expanduser(f"~/Documents/github/{project}/android")
        project_path_main = os.path.expanduser(f"~/Documents/github/{project}")
        os.chdir(project_path)

        # Run Gradle
        print(f"Running ./gradlew {task} in {project_path}")
        subprocess.run(["./gradlew", task])

        print(f"opening {project_path_main}/build/app/outputs")
        subprocess.run(["open", f"{project_path_main}/build/app/outputs"])

    elif program == "BFT2":
        import subprocess
        import sys
        import os

        project = sys.argv[2] #celiktafsirv4, escabee-mobile
        task = sys.argv[3] #assembleRelease, bundleRelease, assembleDebug

        # Set Node path
        os.environ["PATH"] = f"{os.environ['HOME']}/.nvm/versions/node/v22.14.0/bin:" + os.environ["PATH"]

        # Change dir
        project_path = os.path.expanduser(f"~/Documents/github/{project}/android")
        project_path_main = os.path.expanduser(f"~/Documents/github/{project}")
        os.chdir(project_path)

        # Run Gradle
        print(f"Running ./gradlew {task} in {project_path}")
        subprocess.run(["./gradlew", task])

        print(f"opening {project_path_main}/build/app/outputs")
        subprocess.run(["open", f"{project_path_main}/build/app/outputs"])




if (program == "QT" or program == "FW"):
    run_function(program, app)
else:
    run_function(program)

