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
import pickle
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from ..SaleRecord.settings import PROJECT_DIR

columns=["s_no", "rc_number", "scheme", "type", "receipt_number", "date", "kejriwal_wheat", "kejriwal_rice", "kejriwal_sugar", "pm_wheat", "pm_rice", "amount", "portability", "auth_time"]
card_types = ["AAY", "PR", "PRS"]
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

def autopct_format(values):
	def my_format(pct):
		total = sum(values)
		val = int(pct)*total/100
		return '{:.1f}%\n({:.0f})'.format(pct, val)
	return my_format

def saveChart(data):
	for _, v in data.items():
		for key,value in v.items():
			slices = []
			labels = []
			explode = []
			for item in value:
				if item[0] in card_types and item[1] != 0:
					slices.append(item[1])
					labels.append(item[0])
					explode.append(0.05)
			else:
				# total = sum(slices) 
				# if total > 0:
				try:
					
					plt.style.use('fivethirtyeight')
					# fig1, ax1 = plt.subplots()
					# ax1.pie(slices,explode=explode, labels=labels, wedgeprops={'edgecolor':'black'},
					# 	shadow=True, startangle=90, pctdistance=0.4, autopct=autopct_format(slices), normalize=True,textprops={'fontsize': 20})
					# #draw circle
					# centre_circle = plt.Circle((0,0),0.70,fc='white')
					# fig = plt.gcf()
					# fig.gca().add_artist(centre_circle)
					# # Equal aspect ratio ensures that pie is drawn as a circle
					# ax1.axis('equal')  
					plt.pie(slices,explode=explode, labels=labels, wedgeprops={'edgecolor':'black'}, radius=1.2,
						shadow=True, startangle=90, autopct=autopct_format(slices), normalize=True,textprops={'fontsize': 20})
					plt.title(key.replace("_", " ").title(), fontdict = {'fontsize' : 48})
					plt.tight_layout()
					plt.savefig( os.path.join(PROJECT_DIR, 'static', 'home', 'media', key + ".png") ,bbox_inches='tight',)
					plt.close()	
				except Exception as e: 
					print(e)



def initialize(request):
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
			context = {"error": "Timed out waiting for district page to load"}
			return JsonResponse(context,status = 400)
		except Exception as e:
			driver.close()
			context = {"error": repr(e)}
			return JsonResponse(context,status = 400)


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
			context = {"error": "Timed out waiting for zone page to load"}
			return JsonResponse(context,status = 400)
		except Exception as e:
			driver.close()
			context = {"error": repr(e)}
			return JsonResponse(context,status = 400)	

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
			context = {"error": "Timed out waiting for fps page to load"}
			return JsonResponse(context,status = 400)
		except Exception as e:
			driver.close()
			context = {"error": repr(e)}
			return JsonResponse(context,status = 400)

		try:
			recordsList=[]
			element_present= EC.presence_of_all_elements_located((By.XPATH, '//div[@id="Report_paginate"]' ))
			WebDriverWait(driver, timeout).until(element_present)
			# elem = driver.find_element_by_link_text("Next")
			elem = driver.find_element_by_xpath('//div[@id="Report_paginate"]/a[3]')
			
			Records.objects.all().delete()
			not_done = True
			while elem and not_done:
				element_present= EC.presence_of_all_elements_located((By.XPATH, '//table[@id="Report"]' ))
				WebDriverWait(driver, timeout).until(element_present)
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
			with open("pickle.db", "wb") as f:
				pickle.dump(recordsList, f)
			driver.close()

		except TimeoutException as e:
			context = {"error": "Timed out waiting for results page to load"}
			return JsonResponse(context,status = 400)
		except Exception as e:
			context = {"error": repr(e)}
			return JsonResponse(context,status = 400)

	except Exception as e:
		print(e)
		context = {"error": repr(e)}
		try:
			driver.close()
		except Exception as e:
			print(e)
		return JsonResponse(context,status = 400)

	return JsonResponse(context, status = 200)

def combineData(request):
	context = {}
	try:
		with open("pickle.db", "rb") as f:
			recordsList = pickle.load(f)
		Records.objects.all().delete()
		Records.objects.bulk_create(recordsList)	
		my_dict = fetchData()
		print(my_dict, recordsList)

		with open("pickle2.db", "wb") as f:
			pickle.dump(my_dict, f)
		return JsonResponse(context, status = 200)
	except Exception as e:
		context = {"error": repr(e)}
		return JsonResponse(context,status = 400)

def executeQuery(query, date):
	total = 0
	rows = []
	for card_type in card_types:
		if query[0] == "total_cards":
			res= Records.objects.filter(scheme=card_type).count()
		else:
			res=Records.objects.filter(scheme=card_type).aggregate(Sum(query[0]))[f'{query[0]}__sum']
		
		resp = int(res) if res else 0 
		total = resp + total 
		rows.append([card_type, resp])
	rows.append(["Total", total])
	return rows

def fetchData():
	new_dict = {}
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


def index(request):
	context = {"date": today}

	return render(request, 'home.html', context)	

def display(request):
	with open("pickle2.db", "rb") as f:
		display_data = pickle.load(f)
	saveChart(display_data)
	context = { "data": display_data, "date": today}
	return render(request, 'table.html', context)