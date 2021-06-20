import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from sqlitedict import SqliteDict

#add highscore support

# checks existing db if key present => if newvalue != oldvalue ? upfate old to new and return value : return old value
# key not present return None
def check_and_update_and_return(key, new_value):
    if new_value is None:
        return mydict.get(key, default=None)

    old_value = mydict.get(key, default=None)
    if old_value is None:
        return None
    else:
        if old_value != new_value:
            mydict[key] = new_value
            mydict.commit()
            return new_value
        else:
            return old_value

 # adds to sqlite dict and returns none
# print inserted number
def add_to_sqlite_dict(key,value):
    mydict[key]=value
    mydict.commit()
    print("inserted :",key,value)


def print_mydict():
    print("my dictionary is:\n")
    for key, value in mydict.iteritems():
        print(key, value)


def main():
    chrome_options = Options()
    chrome_options.add_argument("user-data-dir=C:\\Users\\vinee\\AppData\\Local\\Google\\Chrome\\User Data\\Default")
    #chrome_options.add_extension("sqlite/extension_1_35_2_0.crx")
    driver = webdriver.Chrome(executable_path='./chromedriver', chrome_options=chrome_options)
    driver.implicitly_wait(5)
    driver.get("http://www.higherlowergame.com/")

    try:
        cookiebtn = driver.find_element_by_xpath("//button[@class='sc-htpNat gXzlcV']")
        cookiebtn.click()
        time.sleep(3)
    except:
        pass

    btn_start = driver.find_element_by_xpath("//button[@class='game-button game-button--start']")
    btn_start.click()
    time.sleep(3)

    count = 0
    while True:
        #left_eletext = driver.find_element_by_xpath("//p[@class='term-keyword__keyword']").text[1:-1].lower()
        left_eletext = driver.find_element_by_xpath("//*[@id='root']/div/span/span/div/div[2]/div[1]/div[1]/div/div[1]/p[1]").text[1:-1].lower()

        #left_elenum = int(driver.find_element_by_xpath("//p[@class='term-volume__volume']").text.replace(',', ''))
        left_elenum = int(driver.find_element_by_xpath("//*[@id='root']/div/span/span/div/div[2]/div[1]/div[1]/div/div[2]/p[1]").text.replace(',', ''))


        #right_eletext = driver.find_element_by_xpath("(//p[@class='term-keyword__keyword'])[2]").text[1:-1].lower()
        right_eletext = driver.find_element_by_xpath("//*[@id='root']/div/span/span/div/div[2]/div[1]/div[2]/div/div[1]/p[1]").text[1:-1].lower()


        #print(left_eletext, left_elenum, right_eletext)

        res_left = check_and_update_and_return(key=left_eletext, new_value=left_elenum)

        if res_left is None:
            add_to_sqlite_dict(key=left_eletext, value=left_elenum)
            res_left = left_elenum

        res_right = check_and_update_and_return(key=right_eletext,new_value=None)

        if res_right is None:
            higher_btn = driver.find_element_by_xpath("//button[contains(@class,'game-button term-actions__button')]")
            higher_btn.click()
            right_elenum = driver.find_element_by_xpath(
                xpath="//*[@id='root']/div/span/span/div/div[2]/div[1]/div[2]/div/div[2]/p[1]/span")
            t_end = time.time() + 3
            mylist = []
            while time.time() < t_end:
                try:
                    mylist.append(int(right_elenum.text.replace(',', '')))
                except:
                    pass
            add_to_sqlite_dict(key=right_eletext, value=int(mylist[-1]))
            time.sleep(3)
            game_over_btn = None
            try:
                game_over_btn = driver.find_element_by_xpath("//*[@id='game-over-btn']")
            except:
                #print("game over not found") #so we can continue
                pass

            if game_over_btn is not None:
                game_over_btn.click()


        else:
            if res_left < res_right:
                higher_btn = driver.find_element_by_xpath(
                    "//button[contains(@class,'game-button term-actions__button')]")
                higher_btn.click()
            else:
                lower_btn = driver.find_element_by_xpath(
                    "(//button[contains(@class,'game-button term-actions__button')])[2]")
                lower_btn.click()
        time.sleep(8)
        highscore=driver.find_element_by_xpath("//*[@id='root']/div/span/span/div/div[1]/p").text
        score=driver.find_element_by_xpath("//p[text()='Score']").text
        print(count,score,highscore)
        count += 1
    driver.close()



if __name__ == '__main__':
    N = 1
    thread_list = list()
    global mydict
    with SqliteDict('./my_db.sqlite') as mydict:
        for i in range(N):
            t = threading.Thread(name='Test tab {}'.format(i), target=main)
            t.start()
            print(t.name + ' started!')
            thread_list.append(t)

        for thread in thread_list:
            thread.join()
        print('\ncompleted!\n')
        #print_mydict()
        print("size of db",len(mydict))
    print("\nexited mydict")
