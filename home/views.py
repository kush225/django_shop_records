from django.shortcuts import render
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import sqlite3
# from webdriver_manager.chrome import ChromeDriverManager
from datetime import date
import logging

columns=["s_no", "rc_number", "scheme", "type", "receipt_number", "date", "wheat", "rice", "sugar", "pm_wheat", "pm_rice", "amount", "portability", "auth_time"]

current_date = date.today()
today = current_date.strftime('%d-%m-%Y')
# yesterday= (datetime.now() - timedelta(1)).strftime('%d-%m-%Y')
dates = [today]

class dbopen(object):
    """
    Simple CM for sqlite3 databases. Commits everything at exit.
    """
    def __init__(self):
        self.path = ":memory:" 

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
	
        return self.cursor

    def __exit__(self, exc_class, exc, traceback):
        self.conn.commit()
        self.conn.close()

def addData(cursor):
	url="https://epos.delhi.gov.in/AbstractTransReport.jsp"

	# options = webdriver.ChromeOptions()
	# options.add_argument("headless")
	# options.add_argument('--no-sandbox')
	# driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

	options = webdriver.ChromeOptions()
	options.binary_location = '/app/.apt/usr/bin/google-chrome' 
	options.add_argument("--headless")
	options.add_argument('--disable-gpu')
	options.add_argument('--no-sandbox')
	path="/app/.chromedriver/bin/chromedriver"
	driver = webdriver.Chrome(executable_path=path, options=options)

	timeout = 30
	driver.get(url)
	try:
		element_present= EC.presence_of_all_elements_located((By.XPATH, '//div[@id="detailsER"]/table' ))
		WebDriverWait(driver, timeout).until(element_present)
		all_rows = driver.find_elements_by_xpath('//div[@id="detailsER"]/table/tbody/tr')
		for rows in all_rows:
			if rows.text.split(" ")[1] == "EAST":
				logging.info(rows.text)
				driver.execute_script("arguments[0].click();", WebDriverWait(rows, timeout).until(EC.element_to_be_clickable((By.XPATH, ".//td[2]/a"))))
				break	

		element_present= EC.presence_of_all_elements_located((By.XPATH, '//div[@id="detailsERR"]/table' ))
		WebDriverWait(driver, timeout).until(element_present)
		all_rows = driver.find_elements_by_xpath('//div[@id="detailsERR"]/table/tbody/tr')
		for rows in all_rows:
			if rows.text.split(" ")[1] == "KRISHNA":
				logging.info(rows.text)
				driver.execute_script("arguments[0].click();", WebDriverWait(rows, timeout).until(EC.element_to_be_clickable((By.XPATH, ".//td[2]/a"))))
				break	

		element_present= EC.presence_of_all_elements_located((By.XPATH, '//div[@id="detailsERRR"]/table' ))
		WebDriverWait(driver, timeout).until(element_present)
		all_rows = driver.find_elements_by_xpath('//div[@id="detailsERRR"]/table/tbody/tr')
		for rows in all_rows:
			if rows.text.split(" ")[1] == "100100600029":
				logging.info(rows.text)
				driver.execute_script("arguments[0].click();", WebDriverWait(rows, timeout).until(EC.element_to_be_clickable((By.XPATH, ".//td[2]/a"))))
				break	
		
		
		data=[]
		element_present= EC.presence_of_all_elements_located((By.XPATH, '//div[@id="Report_paginate"]' ))
		WebDriverWait(driver, timeout).until(element_present)
		# elem = driver.find_element_by_link_text("Next")
		elem = driver.find_element_by_xpath('//div[@id="Report_paginate"]/a[3]')
		# cursor.execute("DROP TABLE IF EXISTS records")
		cursor.execute("""CREATE TABLE records (
			s_no integer,
			rc_number text,
			scheme text,
			type text,
			receipt_number text,
			date text,
			wheat integer,
			rice integer,
			sugar integer,
			pm_wheat integer,
			pm_rice integer,
			amount integer,
			portability text,
			auth_time integer
			)""")
		try:
			not_done = True
			while elem and not_done:
				element_present= EC.presence_of_all_elements_located((By.XPATH, '//table[@id="Report"]' ))
				WebDriverWait(driver, timeout).until(element_present)
				all_rows = driver.find_elements_by_xpath('//table[@id="Report"]/tbody/tr')
				
				for rows in all_rows:
					# logging.info(rows.text)
					my_list = rows.text.split(" ")
					if today != my_list[5]:
						not_done = False
						break
					data.append(my_list)
					
					cursor.execute(f"INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(int(my_list[0]), my_list[1],my_list[2],my_list[3],my_list[4],my_list[5],float(my_list[6]),float(my_list[7]),float(my_list[8]),float(my_list[9]),float(my_list[10]), float(my_list[11]), my_list[12], float(my_list[13])))
				try:
					elem = driver.find_element_by_xpath('//div[@id="Report_paginate"]/a[3]')
					if 'disabled' in elem.get_attribute('class'):
						break
					else:
						driver.execute_script("arguments[0].click();", elem)	
				except Exception as e:
					logging.info('Next not available or page not loaded!',e)
		except exceptions.StaleElementReferenceException as e:
			logging.error(e)
		except TimeoutException as e:
			logging.error(e) 
		logging.info(len(data))
		
		return True
	except TimeoutException:
		logging.error("Timed out waiting for page to load")
		return False
	except Exception as e:
		logging.error(e)
		return False

def fetchData(cursor):
	card_types = ["AAY", "PR", "PRS"]
		
	new_dict = {}
	# cursor.execute("SELECT DISTINCT(date) from records")
	# dates = cursor.fetchall()
	# dates = [x[0] for x in dates]
	# sorted(dates, key=lambda x: datetime.strptime(x, '%d-%m-%Y'), reverse=True)
	for date in dates:
		my_dict = {"total_cards": [], "pm_wheat": [], "pm_rice": [], "kejriwal_wheat": [], "kejriwal_rice": [], "kejriwal_sugar": []}
		new_dict[date]=my_dict
		total_sale = 0
		rows = []
		for card_type in card_types:
			cursor.execute(f"SELECT count(*) FROM records WHERE date=:date and scheme=:scheme",{'date':date, 'scheme':  card_type})
			resp = cursor.fetchone()[0]
			total_sale = resp + total_sale 
			rows.append([card_type, resp])
		rows.append(["Total", total_sale])
		new_dict[date]["total_cards"] = rows

		## PM
		total = 0
		rows = []
		for card_type in card_types:
			cursor.execute(f"SELECT SUM(pm_wheat) FROM records WHERE date=:date and scheme=:scheme",{'date':date, 'scheme':  card_type})
			resp = cursor.fetchone()[0]
			total = resp + total 
			rows.append([card_type, resp])
		rows.append(["Total", total])
		new_dict[date]["pm_wheat"] = rows

		total = 0
		rows = []
		for card_type in card_types:
			cursor.execute(f"SELECT SUM(pm_rice) FROM records WHERE date=:date and scheme=:scheme",{'date':date, 'scheme':  card_type})
			resp = cursor.fetchone()[0]
			total = resp + total 
			rows.append([card_type, resp])
		rows.append(["Total", total])
		new_dict[date]["pm_rice"] = rows
			

		## Kejriwal
		total = 0
		rows = []
		for card_type in card_types:
			cursor.execute(f"SELECT SUM(wheat) FROM records WHERE date=:date and scheme=:scheme",{'date':date, 'scheme':  card_type})
			resp = cursor.fetchone()[0]
			total = resp + total 
			rows.append([card_type, resp])
		rows.append(["Total", total])
		new_dict[date]["kejriwal_wheat"] = rows

		total = 0
		rows = []
		for card_type in card_types:
			cursor.execute(f"SELECT SUM(rice) FROM records WHERE date=:date and scheme=:scheme",{'date':date, 'scheme':  card_type})
			resp = cursor.fetchone()[0]
			total = resp + total 
			rows.append([card_type, resp])
		rows.append(["Total", total])
		new_dict[date]["kejriwal_rice"] = rows

		total = 0
		rows = []
		for card_type in card_types:
			cursor.execute(f"SELECT SUM(sugar) FROM records WHERE date=:date and scheme=:scheme",{'date':date, 'scheme':  card_type})
			resp = cursor.fetchone()[0]
			total = resp + total 
			rows.append([card_type, resp])
		rows.append(["Total", total])
		new_dict[date]["kejriwal_sugar"] = rows

	return new_dict

# Create your views here.
def home(request):
	my_dict = {}
	success=False
	with dbopen() as cursor:
		success=addData(cursor)
		if success:
			my_dict = fetchData(cursor)
			logging.info(my_dict)
		else: 
			logging.info("FAILED")
	logging.debug(my_dict)
	context = { "data": my_dict, "status": success}
	return render(request, 'home.html', context)