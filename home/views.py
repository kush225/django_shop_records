from django.shortcuts import render
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import sqlite3
from datetime import date
import os

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
        self.path = "data.db" 

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
	
        return self.cursor

    def __exit__(self, exc_class, exc, traceback):
        self.conn.commit()
        self.conn.close()

def addData(cursor):
	try:
		url="https://epos.delhi.gov.in/AbstractTransReport.jsp"

		options = webdriver.ChromeOptions()
		options.add_argument("headless")
		options.add_argument('--no-sandbox')
		options.add_argument('--disable-gpu')

		if os.getenv("PRODUCTION", False) and os.getenv("PRODUCTION") == "True":
			options.binary_location = '/app/.apt/usr/bin/google-chrome' 
			path="/app/.chromedriver/bin/chromedriver"
			driver = webdriver.Chrome(executable_path=path, options=options)
		else:
			from webdriver_manager.chrome import ChromeDriverManager
			driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

		timeout = 30
		driver.get(url)
	
		element_present= EC.presence_of_all_elements_located((By.XPATH, '//div[@id="detailsER"]/table' ))
		WebDriverWait(driver, timeout).until(element_present)
		all_rows = driver.find_elements_by_xpath('//div[@id="detailsER"]/table/tbody/tr')
		for rows in all_rows:
			if rows.text.split(" ")[1] == "EAST":
				print(rows.text)
				driver.execute_script("arguments[0].click();", WebDriverWait(rows, timeout).until(EC.element_to_be_clickable((By.XPATH, ".//td[2]/a"))))
				break	

		element_present= EC.presence_of_all_elements_located((By.XPATH, '//div[@id="detailsERR"]/table' ))
		WebDriverWait(driver, timeout).until(element_present)
		all_rows = driver.find_elements_by_xpath('//div[@id="detailsERR"]/table/tbody/tr')
		for rows in all_rows:
			if rows.text.split(" ")[1] == "KRISHNA":
				print(rows.text)
				driver.execute_script("arguments[0].click();", WebDriverWait(rows, timeout).until(EC.element_to_be_clickable((By.XPATH, ".//td[2]/a"))))
				break	

		element_present= EC.presence_of_all_elements_located((By.XPATH, '//div[@id="detailsERRR"]/table' ))
		WebDriverWait(driver, timeout).until(element_present)
		all_rows = driver.find_elements_by_xpath('//div[@id="detailsERRR"]/table/tbody/tr')
		for rows in all_rows:
			if rows.text.split(" ")[1] == "100100600029":
				print(rows.text)
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
					# print(rows.text)
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
					print('Next not available or page not loaded!',e)
		except exceptions.StaleElementReferenceException as e:
			print(e)
		except TimeoutException as e:
			print(e) 
		print(len(data))
		
		return True
	except TimeoutException:
		print("Timed out waiting for page to load")
		return False
	except Exception as e:
		print(e)
		return False

def executeQuery(cursor, query, date):
	card_types = ["AAY", "PR", "PRS"]
	total = 0
	rows = []
	for card_type in card_types:
		cursor.execute(query,{'date':date, 'scheme':  card_type})
		res= cursor.fetchone()
		resp = res[0] if res[0] else 0 
		total = resp + total 
		rows.append([card_type, resp])
	rows.append(["Total", total])
	return rows

def fetchData(cursor):
	new_dict = {}
	# cursor.execute("SELECT DISTINCT(date) from records")
	# dates = cursor.fetchall()
	# dates = [x[0] for x in dates]
	# sorted(dates, key=lambda x: datetime.strptime(x, '%d-%m-%Y'), reverse=True)
	queries =[
		["total_cards", "count(*)"], 
		["pm_wheat", "SUM(pm_wheat)"], 
		["pm_rice", "SUM(pm_rice)"],
		["kejriwal_wheat", "SUM(wheat)"],
		["kejriwal_rice", "SUM(rice)"],
		["kejriwal_sugar", "SUM(sugar)"],
		]
	for date in dates:
		my_dict = {"total_cards": [], "pm_wheat": [], "pm_rice": [], "kejriwal_wheat": [], "kejriwal_rice": [], "kejriwal_sugar": []}
		new_dict[date]=my_dict
		for item in queries:
			query= "SELECT {} FROM records WHERE date=:date and scheme=:scheme".format(item[1])
			rows = executeQuery(cursor, query, date)
			new_dict[date][item[0]] = rows	

	return new_dict

# Create your views here.
def home(request):
	my_dict = {}
	success=False
	with dbopen() as cursor:
		success=addData(cursor)
		if success:
			my_dict = fetchData(cursor)
			print(my_dict)
		else: 
			print("FAILED")
	print(my_dict)
	context = { "data": my_dict, "status": success}
	return render(request, 'home.html', context)