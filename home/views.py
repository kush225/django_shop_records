from django.http.response import JsonResponse
from django.shortcuts import render
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import exceptions
# import sqlite3
from datetime import date, datetime
import os
# import time
from .models import Records
from django.db.models import Sum

columns=["s_no", "rc_number", "scheme", "type", "receipt_number", "date", "kejriwal_wheat", "kejriwal_rice", "kejriwal_sugar", "pm_wheat", "pm_rice", "amount", "portability", "auth_time"]
date_format =  '%d-%m-%Y'
current_date = date.today()
today = current_date.strftime(date_format)
# yesterday= (datetime.now() - timedelta(1)).strftime('%d-%m-%Y')
dates = [today]

url="https://epos.delhi.gov.in/AbstractTransReport.jsp"

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument("--disable-dev-shm-usage")
display_data = []

timeout = 25


######
driver = None
recordsList = []

def initialize(request):
	global driver
	context = {}
	try:
		if os.getenv("PRODUCTION", False) and os.getenv("PRODUCTION") == "True":
			options.binary_location = os.getenv('CHROME_BINARY_PATH')
			#  '/app/.apt/usr/bin/google-chrome' 
			path= os.getenv('CHROME_DRIVER_PATH')
			# "/app/.chromedriver/bin/chromedriver"
			driver = webdriver.Chrome(executable_path=path, options=options)
			# driver = webdriver.PhantomJS()
		else:
			from webdriver_manager.chrome import ChromeDriverManager
			driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
		driver.get(url)
	except Exception as e:
		print(e)
		context = {"error": repr(e)}
		try:
			driver.close()
		except Exception as e:
			print(e)
		return JsonResponse(context,status = 400)

	return JsonResponse(context, status = 200)

def call1(request):
	global driver
	context = {}
	try:
		element_present= EC.presence_of_all_elements_located((By.XPATH, '//div[@id="detailsER"]/table' ))
		WebDriverWait(driver, timeout).until(element_present)
		all_rows = driver.find_elements_by_xpath('//div[@id="detailsER"]/table/tbody/tr')
		for rows in all_rows:
			if rows.text.split(" ")[1] == "EAST":
				print("call1: ",rows.text)
				driver.execute_script("arguments[0].click();", WebDriverWait(rows, timeout).until(EC.element_to_be_clickable((By.XPATH, ".//td[2]/a"))))
				break
	except TimeoutException as e:
		driver.close()
		context = {"error": "Timed out waiting for page to load"}
		return JsonResponse(context,status = 400)
	except Exception as e:
		driver.close()
		context = {"error": repr(e)}
		return JsonResponse(context,status = 400)

	return JsonResponse(context, status = 200)

def call2(request):
	global driver
	context = {}
	try:
		element_present= EC.presence_of_all_elements_located((By.XPATH, '//div[@id="detailsERR"]/table' ))
		WebDriverWait(driver, timeout).until(element_present)
		all_rows = driver.find_elements_by_xpath('//div[@id="detailsERR"]/table/tbody/tr')
		for rows in all_rows:
			if rows.text.split(" ")[1] == "KRISHNA":
				print("call2: ",rows.text)
				driver.execute_script("arguments[0].click();", WebDriverWait(rows, timeout).until(EC.element_to_be_clickable((By.XPATH, ".//td[2]/a"))))
				break
	except TimeoutException as e:
		driver.close()
		context = {"error": "Timed out waiting for page to load"}
		return JsonResponse(context,status = 400)
	except Exception as e:
		driver.close()
		context = {"error": repr(e)}
		return JsonResponse(context,status = 400)

	return JsonResponse(context, status = 200)

def call3(request):
	global driver
	context = {}
	try:
		element_present= EC.presence_of_all_elements_located((By.XPATH, '//div[@id="detailsERRR"]/table' ))
		WebDriverWait(driver, timeout).until(element_present)
		all_rows = driver.find_elements_by_xpath('//div[@id="detailsERRR"]/table/tbody/tr')
		for rows in all_rows:
			if rows.text.split(" ")[1] == "100100600029":
				print("call3: ",rows.text)
				driver.execute_script("arguments[0].click();", WebDriverWait(rows, timeout).until(EC.element_to_be_clickable((By.XPATH, ".//td[2]/a"))))
				break
	except TimeoutException as e:
		driver.close()
		context = {"error": "Timed out waiting for page to load"}
		return JsonResponse(context,status = 400)
	except Exception as e:
		driver.close()
		context = {"error": repr(e)}
		return JsonResponse(context,status = 400)

	return JsonResponse(context, status = 200)

def call4(request):
	global driver
	global recordsList
	context = {}
	try:
		recordsList=[]
		element_present= EC.presence_of_all_elements_located((By.XPATH, '//div[@id="Report_paginate"]' ))
		WebDriverWait(driver, 15).until(element_present)
		# elem = driver.find_element_by_link_text("Next")
		elem = driver.find_element_by_xpath('//div[@id="Report_paginate"]/a[3]')
		
		Records.objects.all().delete()
		not_done = True
		while elem and not_done:
			element_present= EC.presence_of_all_elements_located((By.XPATH, '//table[@id="Report"]' ))
			WebDriverWait(driver, 5).until(element_present)
			all_rows = driver.find_elements_by_xpath('//table[@id="Report"]/tbody/tr')
			
			for rows in all_rows:
				# print("call4: ", rows.text)
				my_list = rows.text.split(" ")
				if today != my_list[5]:
					not_done = False
					break
				dt = datetime.strptime(my_list[5], date_format).strftime("%Y-%m-%d")
				my_dict = dict(zip(columns, [ int(my_list[0]), my_list[1],my_list[2],my_list[3],my_list[4],dt,float(my_list[6]),float(my_list[7]),float(my_list[8]),float(my_list[9]),float(my_list[10]), float(my_list[11]), my_list[12], float(my_list[13])]))
				recordsList.append(Records(**dict(my_dict)))
				
			try:
				elem = driver.find_element_by_xpath('//div[@id="Report_paginate"]/a[3]')
				if 'disabled' in elem.get_attribute('class'):
					break
				else:
					driver.execute_script("arguments[0].click();", elem)	
			except Exception as e:
				print('Next not available or page not loaded!',e)
		print(len(recordsList))
		driver.close()
	except TimeoutException as e:
		context = {"error": "Timed out waiting for page to load"}
		return JsonResponse(context,status = 400)
	except Exception as e:
		context = {"error": repr(e)}
		return JsonResponse(context,status = 400)
	
	
	return JsonResponse(context, status = 200)

def combineData(request):
	context = {}
	global recordsList
	global display_data
	display_data = None
	try:
		Records.objects.all().delete()
		Records.objects.bulk_create(recordsList)	
		my_dict = fetchData()
		print(my_dict, recordsList)
		display_data = my_dict
		context = { "data": display_data, "status": True, "date": today}
		return render(request, 'table.html', context)
	except Exception as e:
		context = {"error": repr(e)}
		return JsonResponse(context,status = 400)

# def addData():
	try:
		if os.getenv("PRODUCTION", False) and os.getenv("PRODUCTION") == "True":
			options.binary_location = os.getenv('CHROME_BINARY_PATH')
			#  '/app/.apt/usr/bin/google-chrome' 
			path= os.getenv('CHROME_DRIVER_PATH')
			# "/app/.chromedriver/bin/chromedriver"
			driver = webdriver.Chrome(executable_path=path, options=options)
			# driver = webdriver.PhantomJS()
		else:
			from webdriver_manager.chrome import ChromeDriverManager
			driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
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
		
		
		objs=[]
		element_present= EC.presence_of_all_elements_located((By.XPATH, '//div[@id="Report_paginate"]' ))
		WebDriverWait(driver, timeout).until(element_present)
		# elem = driver.find_element_by_link_text("Next")
		elem = driver.find_element_by_xpath('//div[@id="Report_paginate"]/a[3]')
		
		try:
			Records.objects.all().delete()
			not_done = True
			while elem and not_done:
				element_present= EC.presence_of_all_elements_located((By.XPATH, '//table[@id="Report"]' ))
				WebDriverWait(driver, timeout).until(element_present)
				all_rows = driver.find_elements_by_xpath('//table[@id="Report"]/tbody/tr')
				
				for rows in all_rows:
					my_list = rows.text.split(" ")
					if today != my_list[5]:
						not_done = False
						break
					dt = datetime.strptime(my_list[5], date_format).strftime("%Y-%m-%d")
					my_dict = dict(zip(columns, [ int(my_list[0]), my_list[1],my_list[2],my_list[3],my_list[4],dt,float(my_list[6]),float(my_list[7]),float(my_list[8]),float(my_list[9]),float(my_list[10]), float(my_list[11]), my_list[12], float(my_list[13])]))
					objs.append(Records(**dict(my_dict)))
					
					# cursor.execute(f"INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(int(my_list[0]), my_list[1],my_list[2],my_list[3],my_list[4],my_list[5],float(my_list[6]),float(my_list[7]),float(my_list[8]),float(my_list[9]),float(my_list[10]), float(my_list[11]), my_list[12], float(my_list[13])))
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
		print(len(objs))
		Records.objects.bulk_create(objs)
		driver.close()
		return (True, "")
	except TimeoutException:
		driver.close()
		return (False, "Timed out waiting for page to load") 
	except Exception as e:
		return (False, repr(e))

def executeQuery(query, date):
	card_types = ["AAY", "AAH"]
	total = 0
	rows = []
	for card_type in card_types:
		if card_type == "AAH":
			if query[0] == "total_cards":
				res= Records.objects.exclude(scheme="AAY").count()
			else:
				res=Records.objects.exclude(scheme="AAY").aggregate(Sum(query[0]))[f'{query[0]}__sum']	
		else:
			if query[0] == "total_cards":
				res=Records.objects.filter(scheme="AAY").count()
			else:
				res=Records.objects.filter(scheme="AAY").aggregate(Sum(query[0]))[f'{query[0]}__sum']
		
		resp = int(res) if res else 0 
		total = resp + total 
		rows.append([card_type, resp])
	rows.append(["Total", total])
	return rows

def fetchData():
	new_dict = {}
	# dates = cursor.fetchall()
	# dates = [x[0] for x in dates]
	# sorted(dates, key=lambda x: datetime.strptime(x, '%d-%m-%Y'), reverse=True)
	queries =[
		["total_cards" ], 
		["pm_wheat"], 
		["pm_rice"],
		["kejriwal_wheat"],
		["kejriwal_rice"],
		["kejriwal_sugar"],
		]
	for date in dates:
		my_dict = {"total_cards": [], "pm_wheat": [], "pm_rice": [], "kejriwal_wheat": [], "kejriwal_rice": [], "kejriwal_sugar": []}
		new_dict[date]=my_dict
		for item in queries:
			rows = executeQuery(item, date)
			new_dict[date][item[0]] = rows	

	return new_dict

# def fetch(request):
	global display_data
	display_data = None
	my_dict = {}
	success=False
	# t1 = time.time()
	success, msg =addData()
	if success:
		my_dict = fetchData()
		print(my_dict)
	else: 
		context = {"error": msg}
		return  JsonResponse(context, status = 400)
	# t2 = time.time()
	# print("TOTAL TIME", t2-t1)
	context = { "data": my_dict, "status": success, "date": today}
	display_data = my_dict
	return JsonResponse(context, status = 200)
	# return render(request, 'table.html', context)

def index(request):
	my_dict ={
		today: {"total_cards": [], "pm_wheat": [], "pm_rice": [], "kejriwal_wheat": [], "kejriwal_rice": [], "kejriwal_sugar": []}	
	} 
	context = { "data": my_dict, "status": False, "date": today}

	return render(request, 'home.html', context)	

def display(request):
	context = { "data": display_data, "status": True, "date": today}
	return render(request, 'table.html', context)