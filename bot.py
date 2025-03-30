import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import csv
from datetime import datetime
import re


# driver
def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver




# scraper
def enter_location(driver, locations, asin_list, host_url, output_filename, city_map):
    driver.get("https://www.amazon.in/dp/B015TQ7USO")
    time.sleep(3)
    for location in locations:
        try:
            # Go to Amazon home page to change location first
            driver.get("https://www.amazon.in/dp/B015TQ7USO")
            time.sleep(2)

            wait = WebDriverWait(driver, 5)
            link = wait.until(EC.presence_of_element_located((By.ID, "contextualIngressPtLink")))
            link.click()
            time.sleep(2)

            input_box = driver.find_element(By.ID, "GLUXZipUpdateInput")
            input_box.clear()
            input_box.send_keys(location + Keys.ENTER)
            time.sleep(3)

            print(f"Location updated to {location} ({city_map.get(location, 'Unknown')})")
        except Exception as e:
            print(f"Failed to set location {location}: {e}")
            # Continue scraping with next location
            continue

        # After setting location, scrape all ASINs for this location
        for asin in asin_list:
            target_webpage = f"{host_url}{asin}"
            driver.get(target_webpage)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            city = city_map.get(location, "Unknown")
            seller_text = "no_buy_box"
            price_text = ""
            coupon_text=""
            free_delivery=""
            fastest_delivery=""
            seller_count=""
            min_price=""

            try:
                time.sleep(2)

                # Scrape seller
                seller = driver.find_element(By.ID, "sellerProfileTriggerId")
                seller_text = seller.text

                # Scrape price (adjust XPATH if needed)
                price = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[5]/div[1]/div[4]/div/div[1]/div/div/div/form/div/div/div/div/div[3]/div/div[1]/div/div/span[1]/span[2]/span[2]")
                price_text = price.text

                # Coupon scraping
                try:
                    label = driver.find_element(By.XPATH, "//label[contains(@id, 'couponText')]")
                    # print("scrapped label")
                    coupon_text = label.text.split("\n")[0].strip()
                    coupon_text=coupon_text.replace("Apply","").strip()
                    # print("failed here")
                except:
                    coupon_text = "no discount"

                try:
                    free_delivery_element=driver.find_element(By.XPATH,'//*[@id="mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE"]/span/span')
                    free_delivery=free_delivery_element.text
                except:
                    free_delivery=""

                try:
                    fastest_delivery_element=driver.find_element(By.XPATH,'//*[@id="mir-layout-DELIVERY_BLOCK-slot-SECONDARY_DELIVERY_MESSAGE_LARGE"]/span/span[1]')
                    fastest_delivery=fastest_delivery_element.text
                except:
                    fastest_delivery=""                


                try:
                    seller_count_element=driver.find_element(By.XPATH,'//*[@id="dynamic-aod-ingress-box"]/div/div[2]/a/span/span[1]')
                    seller_count_text=seller_count_element.text
                    parts = seller_count_text.split("(")  # Split at '('
                    if len(parts) > 1:
                        seller_count = parts[1].split(")")[0]  # Extract the number
                except:
                    seller_count=""

                try:
                    min_price_element=driver.find_element(By.XPATH,'//*[@id="dynamic-aod-ingress-box"]/div/div[2]/a/span/span[3]/span[2]/span[2]')
                    min_price=min_price_element.text
                except:
                    min_price=""

                row = [asin,1, timestamp, location, city, seller_text, price_text ,coupon_text,free_delivery,fastest_delivery,seller_count,min_price]

                with open(output_filename, mode='a', newline='', encoding='utf-8') as file:
                    csv.writer(file).writerow(row)
                print(f"Written data for ASIN {asin}, Pincode {location}")

                if(seller_count!=""):
                    
                    open_panel=driver.find_element(By.XPATH,'//*[@id="dynamic-aod-ingress-box"]/div/div[2]/a')
                    open_panel.click()
                    time.sleep(2)

                    try:
                        competitor_sellers=driver.find_elements(By.XPATH,'//*[@id="aod-offer"]')
                        time.sleep(2)
                        for seller in competitor_sellers:
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            city = city_map.get(location, "Unknown")
                            seller_text = "no_buy_box"
                            price_text = ""
                            coupon_text=""
                            free_delivery=""

                            
                            try:
                                seller_name_element=seller.find_element(By.CSS_SELECTOR,'#aod-offer-soldBy > div > div > div.a-fixed-left-grid-col.a-col-right > a')
                                seller_text=seller_name_element.text

                                seller_price_element=seller.find_element(By.CLASS_NAME,'a-price-whole')
                                price_text=seller_price_element.text

                                delivery_time_element=seller.find_element(By.CSS_SELECTOR,'#mir-layout-DELIVERY_BLOCK-slot-PRIMARY_DELIVERY_MESSAGE_LARGE > span > span')
                                free_delivery=delivery_time_element.text

                                try:
                                    coupon_text_element=seller.find_element(By.XPATH,"//label[contains(@id, 'couponText')]")
                                    coupon_text=coupon_text_element.text
                                except:
                                    coupon_text=''
                                
                                row=[asin,"", timestamp, location, city, seller_text, price_text ,coupon_text,free_delivery,"","",""]
                                with open(output_filename, mode='a', newline='', encoding='utf-8') as file:
                                    csv.writer(file).writerow(row)
                            except:
                                pass 


                    except:
                        print("no compititor!!")
                        
                


            except Exception as e:
                print(f"Error at Pincode {location}, ASIN {asin}: {e}")
                row = [asin,1,timestamp, location, city, seller_text, price_text ,coupon_text,free_delivery,fastest_delivery,seller_count,min_price]
                # Leave seller_text and price_text empty
                with open(output_filename, mode='a', newline='', encoding='utf-8') as file:
                    csv.writer(file).writerow(row)
                print(f"Written data for ASIN {asin}, Pincode {location}")

            
            print(f"Success: Pincode {location}, ASIN {asin}, Seller: {seller_text}, Price: {price_text},coupon:{coupon_text},free delivery:{free_delivery}, fastest_delivery:{fastest_delivery},seller count:{seller_count}, minimum price={min_price}")


            # Write data to CSV regardless
            
            




# scrapper initializer
def amazon_main(locations, asin_list, host_url, output_filename, city_map):
    driver = initialize_driver()
    enter_location(driver, locations, asin_list, host_url, output_filename, city_map)
    driver.quit()

