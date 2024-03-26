import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service)

job_details_list = []

def process_job_cards(job_cards):
    for job_card in job_cards:

        job_Title = None
        company_name = None
        salary = None
        job_type = []
        shift_type = []
        job_des = ""
        job_url = ""
        location = ""
        rating = ""

        time.sleep(3)

        try:
            link_element = job_card.find_element(By.CSS_SELECTOR, "a.jcs-JobTitle")
            link_url = link_element.get_attribute("href")
        except NoSuchElementException:
            continue
        
        job_link = link_element.get_attribute("href")
        job_url = job_link

        driver.execute_script("window.open('{}', '_blank');".format(job_link))
        driver.switch_to.window(driver.window_handles[1])

        try:
            job_title = driver.find_element(By.XPATH, '//*[@id="viewJobSSRRoot"]//h1/span')
            company = driver.find_element(By.CLASS_NAME, "css-1l2hyrd.e19afand0")

            job_Title = job_title.text
            company_name = company.text
        except NoSuchElementException:
            pass

        try:
            rating_text = driver.find_element(By.XPATH, '/html/body/div/div[2]/div[3]/div/div/div[1]/div[2]/div[1]/div[2]/div/div/div/div[1]/div[2]/span').text
            rating = rating_text
        except NoSuchElementException:
            pass

        try:
            location_elements = driver.find_elements(By.CLASS_NAME, "css-waniwe.eu4oa1w0")
            for location_element in location_elements:
                location += location_element.text
        except NoSuchElementException:
            pass

        try:
            elements = driver.find_elements(By.CSS_SELECTOR, ".js-match-insights-provider-16m282m.e37uo190")
            for element in elements:
                aria_label = element.get_attribute("aria-label")
                if aria_label == 'Pay':
                    actual_salary = element.find_element(By.CLASS_NAME, "js-match-insights-provider-tvvxwd.ecydgvn1")
                    salary = actual_salary.text
                elif aria_label == 'Job type':
                    job_type_list = element.find_elements(By.XPATH, ".//ul[@class='js-match-insights-provider-1o7r14h eu4oa1w0']")
                    for ul_element in job_type_list:
                        li_elements = ul_element.find_elements(By.TAG_NAME, "li")
                        for li_element in li_elements:
                            schedule_types = li_element.find_elements(By.CSS_SELECTOR, ".js-match-insights-provider-tvvxwd.ecydgvn1")
                            for descendant_element in schedule_types:
                                if descendant_element.text != '':
                                    job_type.append(descendant_element.text)
                elif aria_label == 'Shift and schedule':
                    shift_types = element.find_elements(By.XPATH, ".//ul[@class='js-match-insights-provider-1o7r14h eu4oa1w0']//li//div[@class='js-match-insights-provider-tvvxwd ecydgvn1']")
                    for descendant_element in shift_types:
                        if descendant_element.text != '':
                            shift_type.append(descendant_element.text)
        except NoSuchElementException:
            pass

        try:
            job_description_element = driver.find_element(By.ID, "jobDescriptionText")
            unique_lines = set()
            for child_element in job_description_element.find_elements(By.XPATH, ".//*"):
                unique_lines.add(child_element.text)
            job_description_text = "\n".join(unique_lines)
            job_des = job_description_text
        except NoSuchElementException:
            pass
        
        job_details = {
            "company_name": company_name if company_name else None,
            "job_Title": job_Title if job_Title else None,
            "location": location if location else "",
            "salary": salary if salary else None,
            "job_type": job_type if job_type else [],
            "shift_type": shift_type if shift_type else [],
            "job_url": job_url if job_url else "",
            "job_des": job_des if job_des else "",
            "rating": rating
        }
        
        job_details_list.append(job_details)
        
        time.sleep(2)

        try:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except Exception as e:
            print("Error while closing window:", e)

try:
    driver.get("https://ph.indeed.com/?from=gnav-util-homepage")
    driver.maximize_window()
    
    input_field = driver.find_element(By.ID, "text-input-what")
    input_field.send_keys("Software Engineer")

    input_field = driver.find_element(By.ID, "text-input-where")
    input_field.send_keys("Philippines")
    
    jobButton = driver.find_element(By.CSS_SELECTOR, "#jobsearch > div > div.css-169igj0.eu4oa1w0 > button")
    jobButton.click()

    time.sleep(5)

    for i in range(0, 131, 10):
        driver.get("https://ph.indeed.com/jobs?q=software+engineer&l=Philippines&start=" + str(i))
        job_cards = driver.find_elements(By.CSS_SELECTOR, "#mosaic-provider-jobcards > ul > li")
        process_job_cards(job_cards)
        time.sleep(5)

    df = pd.DataFrame(job_details_list)
    df.to_csv('Indeed_job_details.csv', index=False)

except Exception as e:
    print("An error occurred:", e)

finally:
    driver.quit()
