import time
from selenium.webdriver.common.keys import Keys
from config import (
    get_web_driver_options,
    get_chrome_web_driver,
    set_ignore_certificate_error,
    set_browser_as_incognito,
    set_automation_as_head_less,
    NAME,
    CURRENCY,
    FILTERS,
    BASE_URL,
    DIRECTORY
)
from selenium.common.exceptions import NoSuchElementException
import json
from datetime import datetime

#url  == https://www.amazon.in/s?k={product name}&ref=filter conditions


class AmazonApi:
    def __init__(self,searchTerm,filter,baseURL,currency):
        self.baseURL=baseURL
        self.searchTerm=searchTerm
        options = get_web_driver_options()
        set_ignore_certificate_error(options)
        set_browser_as_incognito(options)
        self.driver=get_chrome_web_driver(options)
        self.currency =currency
        self.price_filter = f"&rh=p_36%3A{filter['min']}00-{filter['max']}00"
    
    def Run(self):
        print("starting Script.....")
        print(f"Looking for {self.searchTerm} product")
        links = self.GetProductLinks()
        if not links:
            print("Stopped script.")
            return
        print(f"Got {len(links)} links to products...")
        print("Getting info about products...")
        products = self.GetProductInfo(links)
        print( f" Got info of {len(products)} products ")
        self.driver.quit()
        return products

    def GetProductLinks(self):
        self.driver.get(self.baseURL)
        element = self.driver.find_element_by_id("twotabsearchtextbox")
        element.send_keys(self.searchTerm)
        element.send_keys(Keys.ENTER)
        time.sleep(1)
        self.driver.get(f"{self.driver.current_url}{self.price_filter}")
        time.sleep(1)
        resultList = self.driver.find_elements_by_class_name('s-result-list')
        links = []
        try:
            results = resultList[0].find_elements_by_xpath(
                "//div/span/div/div/div[2]/div[2]/div/div[1]/div/div/div[1]/h2/a")
            links = [link.get_attribute('href') for link in results]
            return links
        except Exception as e:
            print("Didn't get any products...")
            print(e)
            return links

    def GetProductInfo(self ,links):
        Asins=self.GetAsins(links)
        products=[]
        for asin in Asins:
            product = self.GetSingleProductInfo(asin)
            if product:
                products.append(product)
        return products

    def GetSingleProductInfo(self,asin):
        shortenURL = self.ShortURL(asin)
        self.driver.get(shortenURL)
        time.sleep(1)
        ProductName =self.GetName()
        Price = self.GetPrice()
        Seller =self.GetSeller()
        if Seller and ProductName and Price:
            ProductInfo={
                "Title":ProductName,
                "Price": Price,
                "Seller" : Seller
            }
            return ProductInfo
        return None

    def GetName(self):
        try:
            return self.driver.find_element_by_id("productTitle").text
        except Exception as e:
            print (e)
            print(f"Couldn'd find Title for, product :{self.driver.current_url}")
            return None

    def GetSeller(self):
        try:
            return self.driver.find_element_by_id("sellerProfileTriggerId").text
        except Exception as e:
            print (e)
            print(f"Couldn'd find Seller for, product :{self.driver.current_url}")
            return None

    def GetPrice(self):
        try:
            return self.driver.find_element_by_id("priceblock_ourprice").text
        except:
            try:
                return self.driver.find_element_by_id("priceblock_dealprice").text
            except Exception as e:
                print(e)
                print(f"Couldn'd find Price for, product :{self.driver.current_url}")
                return None

    def ShortURL(self,asin):
        return (self.baseURL+"/dp/"+asin)

    def GetAsins(self,links):
        return [self.GetAsin(link) for link in links]
    
    def GetAsin(self,link):
        return (link[link.find("/dp/")+4: link.find("/ref")])

if __name__ == '__main__' :
    hi = AmazonApi(NAME,FILTERS,BASE_URL,CURRENCY)
    data = hi.Run()
    print (data)