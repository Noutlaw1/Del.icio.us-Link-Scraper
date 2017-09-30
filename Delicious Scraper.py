from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import csv
import os
import sys

class Link_Entry:
    def __init__(self, name, url, tags=0):
        self.name = name
        self.url = url
        self.tags = tags


def start_menu():
 

   
        
    print "==========================="
    print "Del.icio.us link scraper."
    print "By Christopher N. Outlaw: nickoutlaw@gmail.com"
    print "Requires Mozilla Firefox"
    print "==========================="
    print "Menu"
    print "1. Start new extraction."
    print "2. Continue already started extraction."
    print "3. Login to website."
    print "4. Quit"
    menu_selection = int(raw_input("Enter selection: "))
    if menu_selection == 1:
        username = raw_input("Please enter the username you wish to search: ")
        main(username)
    if menu_selection == 2:
        username = raw_input("Please enter the username you wish to search: ")
        restart_previous_search(username)
    if menu_selection == 3:
        username = raw_input("Please enter your username: ")
        password = raw_input("Please enter your password: ")
        login(username, password)
        
    if menu_selection == 4:
        exit
    if menu_selection != 1 and menu_selection != 2 and menu_selection != 3 and menu_selection != 4:
        raw_input("Please select a valid menu item (1-5) and try again. Press enter to continue")
        os.system('cls')
        start_menu()
        

def write_to_CSV(entry_list):
    with open(sys.path[0]  + "/deliciousCSV.csv", "w") as f:
        writer = csv.writer(f)
        for entry in entry_list:
            name = entry.name
       
            url = entry.url
     
            if entry.tags == 0:
                writer.writerow([name.encode('utf-8',  'ignore'), url.encode('utf-8', 'ignore'), "N/A"])
            else:
                try:
                    writer.writerow([name.encode('utf-8', 'ignore'), url.encode('utf-8', 'ignore'), (entry.tags).encode('utf-8', 'ignore')])
                except:
                    writer.writerow([name.encode('utf-8', 'ignore'), url.encode('utf-8', 'ignore'), "There was a problem adding this entry's tags."])
        f.close()
        return entry_list
                        
def restart_previous_search(username=0, driver=0):
    with open(sys.path[0] + "/deliciouspagetracker.txt") as f:
        page_number = f.readline()
        f.close()
    print page_number
    
    if driver == 0:
        driver = webdriver.Firefox()
    driver.get("https://del.icio.us/"  + username + "?-*&page=" + str(page_number))
    entry_list = []
    while True:
        entry_list = scrape_page(driver, entry_list)
        page_num = goto_next_page(driver)
        f = open(sys.path[0] + "\deliciouspagetracker.txt", "w")
        f.write(str(page_num))
        f.close()
               
def login(username, password):

    driver = webdriver.Firefox()
    driver.get("https://del.icio.us/")
    element = driver.find_element_by_xpath('//a[@href="https://del.icio.us/login"]');
    print "Searching for sign in button..."
    element.click()


    timeout = 5
    try:
   
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'signInFlds'))
        print element_present
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print "Timed out waiting for page to load"

    time.sleep(3)
    print "Searching for username/password input"
    inputs = driver.find_elements_by_tag_name("input")
    time.sleep(3)
    for item in inputs:

        if item.is_displayed() == True:
            if item.get_attribute("name") == "username":
                item.send_keys(username)
            if item.get_attribute("name") == "password":
                item.send_keys(password)
    
    buttons = driver.find_elements_by_xpath("//*[@type='submit']")
    for button in buttons:
        if button.text == "Sign In":
            button.submit()
    entry_list = []
    continue_or_new = raw_input("Enter '1' to start a new search, or '2' to continue an existing one: ")
    username = raw_input("Enter the user name you want to scan: ")
    if continue_or_new == "1":
        print "Starting new search."
        main(username, driver)
    else:
        print "Resuming old search."
        restart_previous_search(username, driver)
def goto_next_page(driver):
    #print "Entry list length for goto next page: " + str(len(entry_list))
    current_url = driver.current_url
   
    current_url = current_url.split('=')
    #print len(current_url)
    if len(current_url) == 1:
        goto_url = current_url[0].replace("#","")
        goto_url = goto_url + "?&page=2"
        #print goto_url
        entries_found = True
        driver.get(goto_url)
        page_num = 2
        print "Going to page " + str(page_num)
    else:
        page_num = int(current_url[1])
        page_num = page_num + 1
        goto_url = current_url[0] + "=" + str(page_num)
        print "Going to page " + str(page_num)
        driver.get(goto_url)
    return page_num

def scrape_page(driver, entry_list):
    print "Scraping headers."
    headers = driver.find_elements_by_xpath("//div[@class=\"articleTitlePan\"]//h3")
    
    if len(headers) == 0:
        print "No headers... sleeping."
        time.sleep(5)
        headers = driver.find_elements_by_xpath("//div[@class=\"articleTitlePan\"]//h3")
        if len(headers) == 0:
            raw_input("Finished scraping. Press enter to exit.")
            quit()
            
    print "Headers found: " + str(len(headers))
    urls = driver.find_elements_by_xpath("//div[@class='articleInfoPan']/p[1]/a")
    url_list = []
    for url in urls:
        address = url.get_attribute('href')
        url_list.append(address)
    if len(urls) == 0:
        print "No urls... sleeping."
        time.sleep(5)
        urls = driver.find_elements_by_xpath("//div[@class='articleInfoPan']/p[1]/a")
    print "Urls: " + str(len(url_list))
    tag_divs = driver.find_elements_by_xpath("//div[@class='thumbTBriefTxt']")
    div_count = len(tag_divs)
    count = 0
    
    while count <= div_count-1:
        #print "Searching div..."
        x_path = "(//div[@class='thumbTBriefTxt'])[" + str(count+1) + "]/ul"
        try:
            tags = driver.find_element_by_xpath(x_path)
        except:
            try:
                print "Trying to find tags again..."
                time.sleep(2)
                x_path = "(//div[@class='thumbTBriefTxt'])[" + str(count+1) + "]/ul"
                tags = driver.find_element_by_xpath(x_path)
            except:
                header = headers[count].text
            
                url = urls[count].text
             
                
                entry = Link_Entry(header, url)
                #print "Object: Name - " + entry.name
                entry_list.append(entry)
                #print "Count for this page " + str(count)
                count = count + 1
                #print "No tags."
                #raw_input("added entry without tag")
                continue
        tags = tags.text
 
        header = headers[count].text
        
        url = urls[count].text
       
        entry = Link_Entry(header, url, tags)
        #raw_input("added entry with tag")
        entry_list.append(entry)
        #print "Count for this page " + str(count)
        count = count + 1
        #print "========="
    entry_list = write_to_CSV(entry_list)
    return entry_list

def main(username=0, driver=0):
    print "Main Function Started"
    print "Starting new search on user: " +  username
    
    if driver == 0:
        driver = webdriver.Firefox()
    driver.get("https://del.icio.us/" + username)
    entry_list = []
    f = open(sys.path[0] +  "\deliciouspagetracker.txt", "w")
    f.write("1")
    f.close()
    with open(sys.path[0] + "\deliciouspagetracker.txt", "w") as f:
        writer = csv.writer(f)
        writer.writerow(['Entry Name', 'Entry URL', "Entry Tags"])
        f.close()
    while True:
        entry_list = scrape_page(driver, entry_list)
        #goto_next_page(driver)
        page_num = goto_next_page(driver)
        f = open(sys.path[0] + "\deliciouspagetracker.txt", "w")
        f.write(str(page_num))
        f.close()

start_menu()     
        #tags = driver.find_elements_by_xpath("//ul[@class='tagname']/li/a")
        
                    
 

