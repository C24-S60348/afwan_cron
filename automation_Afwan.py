import getpass
import sys
import config 
import urllib3
import requests

#pip install selenium
#pip install beautifulsoup4
#pip install urllib3
#pip install requests
#pip install webdriver-manager

#VARIABLES-------------------------------------
program = "CR" # A - AutoBooking , CB - Check Booking PNR , CT - Celik Tafsir fetch , 
               # TB - Telegram Bot , WS - Web Scraping , AAI - AI Chat test ,
               # CR - Cron Run , CSFTP - Check SFTP , 
#VARIABLES------------------


#print(len(sys.argv))
if len(sys.argv) > 1:
    program = sys.argv[1]

#Public variables
fyuser = ""
fypass = ""
fycode = ""
tbtoken = ""
csftplink = ""
can05 = True
can1 = True
can2 = True
can3 = True
can5 = True
can10 = True
http = urllib3.PoolManager()

def run_function(program_code, code2=None, info3=None):
    program = program_code
    global http


    #functions
    if (True):
        browser_code = 'F' # C - Chrome , F - Firefox , E - Microsoft Edge , S - Safari
        openfileorfolder = 'F' # F - File , FD - Folder
        xmlformatted = True
        def getbrowser(browser_code):
            if browser_code == 'C':
                trymethod = 1
                if trymethod == 1:
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
        def needPass():
            import json
            password = getpass.getpass("Please input password (can be blank): ")
            url = "https://afwanproductions.pythonanywhere.com/api/executejsonv2"  # Replace with the actual URL
            payload = {
                "password": password,
                "query": "SELECT * FROM afwandata"
            }
            headers = {
                "Content-Type": "application/json"
            }
            #response = requests.post(url, json=payload, headers=headers)

            #print("Status Code:", response.status_code)
            #print("Response:", response.text)
            
            
            payload = json.dumps(payload).encode("utf-8") #change to json
            response = http.request("POST", url, body=payload, headers=headers)

            print("Status Code:", response.status)
            print("Response:", response.data.decode("utf-8"))

            global fyuser
            global fypass
            global fycode
            global tbtoken
            global csftplink #todo

            # Convert response to JSON
            data = response.json()
            # Extract fyuser from the first result
            if "results" in data and len(data["results"]) > 0:
                fyuser = data["results"][0]["fyuser"]
                fypass = data["results"][0]["fypass"]
                fycode = data["results"][0]["fycode"]
                tbtoken = data["results"][0]["tbtoken"]


    #CHECK BOOKING PNR
    if program == "CB":
        #needPass()

        import xml.dom.minidom
        #import urllib.request
        import os
        import platform
        import base64
        #needPass()

        #VARIABLES------------------
        pnr = 'LDIW8U'
        stagingorprod = "S" #S - Staging , P - Prod
        #VARIABLES------------------
        fycode = config.fy_code
        
        if stagingorprod == "S":
            link = config.fy_app_staging
            url = f"{link}?Key={fycode}&RecordLocator={pnr}"
        else:
            link = config.fy_app_prod
            url = f"{link}?Key={fycode}&RecordLocator={pnr}"

        content = http.request("GET", url)
        content = content.data.decode("utf-8")
        content = base64.b64decode(content).decode('utf-8')
        #req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        #try:
            #with urllib.request.urlopen(req) as response:
                #content = response.read()
        #except urllib.error.HTTPError as e:
            #print(f"HTTP Error: {e.code} - {e.reason}")
        #except urllib.error.URLError as e:
            #print(f"URL Error: {e.reason}")

        #content = base64.b64decode(content).decode('utf-8')

        if xmlformatted:
            dom = xml.dom.minidom.parseString(content)
            content = dom.toprettyxml(indent="    ")

        file_name = f"output booking/{pnr}.xml"
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Content has been written to {file_name}")

        # Open the file location
        file_path = os.path.abspath(file_name)
        if openfileorfolder == "FD":
            file_path = os.path.dirname(file_path)

        if platform.system() == "Windows":
            os.startfile(file_path)
        elif platform.system() == "Darwin":  # macOS
            os.system(f'open "{file_path}"')
        else:  # Linux
            os.system(f'xdg-open "{file_path}"')

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
        needPass()

        #VARIABLES------------------
        is_one_way = False
        is_login = False
        if fyuser == "":
            fyuser = ""  # put your custom email and pass fy staging here
            fypass = ""
        flight_fare_type = 'B'   #S - Saver , B - Basic , F - Flex
        flight_fare_type2 = 'B'
        adult = 1
        infant = 0
        station_depart = 'pen'
        station_return = 'lgk'
        target_date = '20250319'
        target_date2 = '20250320'
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

        fydevlink = config.fydevlink
        username = config.fydevusername
        password = config.fydevpassword
        url = f"https://{username}:{password}@{fydevlink}"
        station_depart = station_depart.upper()
        station_return = station_return.upper()

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
        from bs4 import BeautifulSoup
        from lxml import 
        from datetime import datetime
        import platform
        isProd = True
        
        ct_link = os.getenv("CT_LINK")

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
            idx = data.find('entry-title')
            s = data[idx:len(data)]
            idx2 = s.find('</ul>')
            s = s[0:idx2]
            #print(s)

            #get all href in Array
            pages = re.findall(r'href="(.+?)"', s)
            #print(pages)

            #put all inside txt variable
            for f in pages:
                txt += (f + " ")

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


        os.startfile(file_path)  # Windows
        # os.system(f'open "{file_path}"') # macOS
        # os.system(f'xdg-open "{file_path}"') # Linux


        exit()

    #TELEGRAM BOT
    elif program == "TB":
        # needPass()
        import json

        # VARIABLES -----------------
        TOKEN = tbtoken
        if info3 == None:
            code2 = "Afwan" #Custom to
            info3 = "custom" #Custom message
        #VARIABLES ------------------
        
        if code2 == "Afwan":
            CHAT_ID = "222338004" # Celik Tafsir website update Warning : -4723012335 , Study with Afwan : -4515480710 , Afwan : 222338004
        elif code2 == "Study":
            CHAT_ID = "-4515480710"
        elif code2 == "Study":
            CHAT_ID = "-4515480710"
        
        MESSAGE = info3
        
        
        # VARIABLES -----------------
        tb_token = config.tb_token
        
        # Telegram API URL
        url = f"https://api.telegram.org/bot{tb_token}/sendMessage"
        data={"chat_id": CHAT_ID, "text": MESSAGE}
        data = json.dumps(data).encode("utf-8") #change to json
        response = http.request("POST", url, body=data, headers={"Content-Type":"application/json"})

        # Send the message
        #response = requests.post(url, data={"chat_id": CHAT_ID, "text": MESSAGE})

        # Check response
        #if response.status_code == 200:
        if response.status == 200:
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
        email = config.afwanemail
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
    elif program == "CR":
        import time
        from datetime import datetime
        import platform
        from bs4 import BeautifulSoup
        
        def check_status_html(cname, soup):
            cname = soup.find("p", class_=cname)
            if cname:
                cname = cname.decode_contents()
                if cname == "True":
                    return True
                     
            return False
        
        def check_can_cron():
            print("Run check...")
            global http
            cronchecklink = config.cronchecklink
            url = cronchecklink
            
            #response = http.request("GET", url)
            
            #response = response.data.decode("utf-8")
            #soup = BeautifulSoup(response, 'html.parser')
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            global can05
            global can1
            global can2
            global can3
            global can5
            global can10
            
            print(response)
            
            can05 = check_status_html("min05", soup)
            can1 = check_status_html("min1", soup)
            can2 = check_status_html("min2", soup)
            can3 = check_status_html("min3", soup)
            can5 = check_status_html("min5", soup)
            can10 = check_status_html("min10", soup)
                
            #print(can05)
            #print(can1)
            #print(can2)
            #print(can3)
            #print(can5)
            #print(can10)
            
            print("Done check")

        def load_10_min():
            try:              
                print("---------------------- every 10 min")

                run_function("CSFTP")
                run_function("RP")

                print("---------------------- every 10 min")

            except Exception as e:
                print(f"Failed to load {url} - Error: {e}")
        
        def load_5_min():     
            print("---------------every 5 min")
              
            print("---------------every 5 min")
        
        def load_3_min():     
            print("---------------every 3 min")
              
            print("---------------every 3 min")

        if __name__ == "__main__":
            method_use = 4
            
            if method_use == 4:
                check_can_cron()
                print("run once")
                if can10:
                        load_10_min()
                if can5:
                        load_5_min()
                if can3:
                        load_3_min()
            
            if method_use != 4:
                while True:
                    check_can_cron()
                    
                    if can10:
                        load_10_min()
                    if can5:
                        load_5_min()
                    if can3:
                        load_3_min()
                    
                    method_use = 3
                    
                    if method_use == 1:
    
                        for remaining in range(600, 300, -60): #sleep 5min
                            remaining_minute = remaining/60
                            print(f"\rWaiting: {remaining_minute} minutes remaining...", end="", flush=True)
                            time.sleep(60)
                        
                        load_5_min()
                    
                        for remaining in range(300, 0, -60): #sleep 5min
                            remaining_minute = remaining/60
                            print(f"\rWaiting: {remaining_minute} minutes remaining...", end="", flush=True)
                            time.sleep(60)
                    
                    elif method_use == 2:
                        print(f"\rWaiting: 10 minutes remaining...", end="", flush=True)
                        time.sleep(300)
                        load_5_min()
                        print(f"\rWaiting: 5 minutes remaining...", end="", flush=True)
                        time.sleep(300)
                        
                    elif method_use == 3:
                        totalsec = 200
                        #minutes = 600
                        countsec = 10
                        #countsec = 600
                        for remaining in range(0, totalsec, countsec): #sleep 5min
                            emin = remaining/60
                            esec = remaining
                            print(f"\rElapsed {esec}s ...", end="", flush=True)
                            time.sleep(countsec)
                    
                    
                    
                #time.sleep(600)  # Sleep for 5 minutes (300 seconds) # 10 mins
    
    #CHECK SFTP
    elif program == "CSFTP":
        csftp_link = config.csftp_link
        url = csftp_link
        try:
            print("running CSFTP...")
            #response = requests.get(url)
            response = http.request("GET", url)
            response = response.data.decode("utf-8")
            html_data = response
            #print(html_data)
            if (html_data != "connected to NAVITAIRE1SAP<br/>connected to NPS1FIREFLY<br/>connected to ELNVOICE1NAVITAIRE"): #has changes
                run_function("TB", "Afwan", f"One of the SFTP is not running  \n  \n  {html_data}")
            print("done CSFTP")

        except Exception as e:
            print(f"Failed to load {url} - Error: {e}")

    #Reminder Parking
    elif program == "RP":
        import time
        from datetime import datetime

        print("running RP...")
        def checkTime():
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            weekdays = now.weekday() < 5  # Monday to Friday are considered weekdays (0-4)

            # Define the time range
            start_time = "13:50"
            end_time = "14:10"

            start_time2 = "8:50"
            end_time2 = "9:10"
            
            start_time3 = "20:50"
            end_time3 = "21:10"
            
            print(f"now is {current_time}")

            if weekdays and start_time <= current_time <= end_time:
                run_function("TB", "Afwan", "Bayar parking petanggg")
                # print("Current time is between 13:50 and 14:10 on a weekday.")
            if weekdays and start_time2 <= current_time <= end_time2:
                run_function("TB", "Afwan", "Bayar parking pagii")
                # print("Now it's 9 AM, please pay your parking.")
            if start_time3 <= current_time <= end_time3:
                run_function("TB", "Afwan", "Cakap SAYANG kat sara")
                
                
        
        checkTime()
        print("done RP")






run_function(program)


