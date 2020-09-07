
import requests

from lxml import html
from selenium import webdriver
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import random
import pandas as pd



def random_num_generate(length):
    global last_random_num
    num = random.randint(0, length)
    while last_random_num == num:
        num = random.randint(0,length)
    last_random_num = num
    return num


def random_num_proxy(length):
    global random_num_dict, dict_counter
    num = str(random.randint(0,length))
    if dict_counter == 50:
        random_num_dict = {'0':0,'1':0, '2':0, '3':0, '4':0, '5':0, '6':0, '7':0, '8':0, '9':0}
        dict_counter = 0
    while random_num_dict[num] >= 5:
        num = str(random.randint(0,length))
    else:
        random_num_dict[num] += 1
        dict_counter += 1
        print(random_num_dict)
        return int(num)

def setup():
    #23.106.28.66:29842
    proxy_list = ['23.105.4.190:29842','23.105.3.53:29842','23.81.56.35:29842','23.81.55.206:29842',
                  '23.106.28.87:29842','23.106.30.36:29842','23.105.4.238:29842','23.105.3.246:29842','23.81.56.192:29842',
                  '23.81.55.56:29842']
    proxy_num = random_num_proxy(len(proxy_list) - 1)
    proxies = proxy_list[proxy_num]


    headers_list = ['Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
                    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0',
                    ]
    header_num = random_num_generate(len(headers_list) - 1)

    refere_list = ['https://www.google.com']
    refere_num = random_num_generate(len(refere_list) -1)

    headers = headers_list[header_num]
    print(proxies)
    print(headers)

    return proxies, headers



def init_driver():
    set_up = setup()
    proxies = set_up[0]
    headers = set_up[1]


    chrome_path = "/Users/jordanliu/Desktop/chromedriver"
    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    chrome_options.add_argument('user-agent=%s' % headers)

    chrome_options.add_argument('--proxy-server=%s' % proxies)


    driver = webdriver.Chrome(chrome_path, options=chrome_options)
    return driver


if __name__ == '__main__':
    #
    import_data = pd.read_excel('/Users/jordanliu/Desktop/file_with_skus.xlsx')
    import_data = import_data.reset_index(drop=True)

    print(len(import_data))
    random_num_dict = {'0':0,'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0, '9': 0}
    dict_counter = 0
    last_random_num = 0
    price_list = []
    for line in range(len(import_data)):
        checker = False
        print(line)

        if line % 10 == 0:
            pause_time = random.randint(10,20)
        else:
            pause_time = random.randint(2,4)

        time.sleep(pause_time)
        driver = init_driver()
        driver.get('https://www.amazon.com/dp/'+ import_data.at[line,'SKU'])

        time.sleep(3)

        availability = driver.find_elements_by_xpath('//span[@class="a-size-medium a-color-success"]')
        availability2 = driver.find_elements_by_xpath('//span[@class="a-size-medium a-color-price"]')

        if str(availability) != '[]' and str(availability2) != '[]':
            if str(availability[0].text) != 'Available from these sellers.' or str(
                    availability2[0].text) != 'Currently unavailable.':

                try:
                    min_quant_check = str(driver.find_elements_by_xpath('//a[@id="trigger_popover"]'))
                    print(min_quant_check)

                    try:
                        price = str(driver.find_elements_by_xpath('//span[@id="price_inside_buybox"]')[0].text)
                    except:
                        price = str(driver.find_elements_by_xpath('//span[@id="priceblock_ourprice"]')[0].text)

                    print(price)

                    in_stock_check = driver.find_elements_by_xpath('//*[@id="availability"]/span')[0].text
                    print(in_stock_check)
                    prime = driver.find_elements_by_xpath('//div[@id="delivery-message"]')[0].text
                    print(prime)
                    
                    
                    ## REMEMBER to change the prime conditions, this was written before christmas that's why sat
                    ## fri was added
                    if ('One-Day' in prime or 'Two-Day' in prime or 'Same-Day' in prime or 'Tomorrow' in prime or 'Tuesday' in prime
                        or 'tomorrow' in prime ) and \
                            min_quant_check == '[]' \
                            and (in_stock_check == 'In Stock.' or in_stock_check == 'In stock.' or in_stock_check =='in stock.'):

                        print('YEYEYEYEYE')
                        price_list.append(price)
                    else:
                        import_data.drop(line, inplace=True)

                except:
                    import_data.drop(line, inplace=True)
            else:
                import_data.drop(line, inplace=True)
        else:
            import_data.drop(line, inplace=True)

        driver.quit()

    import_data.insert(1, 'Amazon Price', price_list)
    import_data = import_data.reset_index(drop=True)

    final_path = '/Users/jordanliu/Desktop/amazon_scrape.xlsx'
    writer = pd.ExcelWriter(final_path, engine='xlsxwriter')
    import_data.to_excel(writer)
    writer.save()

