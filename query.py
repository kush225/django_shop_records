import sqlite3
# from prettytable import PrettyTable

conn = sqlite3.connect('data.db')

c = conn.cursor()

# date = "20-07-2021"
card_types = ["AAY", "PR", "PRS"]

columns=["s_no", "rc_number", "scheme", "type", "receipt_number", "date", "wheat", "rice", "sugar", "pm_wheat", "pm_rice", "amount", "portability", "auth_time"]


c.execute("SELECT DISTINCT(date) from records")
dates = c.fetchall()


# def generateTable(header, rows):
# 	x = PrettyTable()
# 	x.field_names=header
# 	x.align = "l"
# 	for row in rows:
# 		x.add_row(row)

# 	print(x)


for item in dates:
	date = item[0]
	print("---------------------------------------")
	print("DATE: ", date)
	print("---------------------------------------")
	total_sale = 0
	rows = []
	header= ["Different cards", "Count"]
	for card_type in card_types:
		c.execute("SELECT count(*) FROM records WHERE date=:date and scheme=:scheme",{'date':date, 'scheme':  card_type})
		resp = c.fetchone()[0]
		total_sale = resp + total_sale 
		rows.append([card_type, resp])
	rows.append(["Total", total_sale])
	print(rows)
	# generateTable(header=header, rows=rows)

# 	## PM
# 	total = 0
# 	rows = []
# 	header= ["PM wheat sold", "Quantity (kg)"]
# 	for card_type in card_types:
# 		c.execute("SELECT SUM(pm_wheat) FROM records WHERE date=:date and scheme=:scheme",{'date':date, 'scheme':  card_type})
# 		resp = c.fetchone()[0]
# 		total = resp + total 
# 		rows.append([card_type, resp])
# 	rows.append(["Total", total])
# 	generateTable(header=header, rows=rows)

# 	total = 0
# 	rows = []
# 	header= ["PM rice sold", "Quantity (kg)"]
# 	for card_type in card_types:
# 		c.execute("SELECT SUM(pm_rice) FROM records WHERE date=:date and scheme=:scheme",{'date':date, 'scheme':  card_type})
# 		resp = c.fetchone()[0]
# 		total = resp + total 
# 		rows.append([card_type, resp])
# 	rows.append(["Total", total])
# 	generateTable(header=header, rows=rows)
		

# 	## Kejriwal
# 	total = 0
# 	rows = []
# 	header= ["Kejriwal wheat sold", "Quantity (kg)"]
# 	for card_type in card_types:
# 		c.execute("SELECT SUM(wheat) FROM records WHERE date=:date and scheme=:scheme",{'date':date, 'scheme':  card_type})
# 		resp = c.fetchone()[0]
# 		total = resp + total 
# 		rows.append([card_type, resp])
# 	rows.append(["Total", total])
# 	generateTable(header=header, rows=rows)

# 	total = 0
# 	rows = []
# 	header= ["Kejriwal rice sold", "Quantity (kg)"]
# 	for card_type in card_types:
# 		c.execute("SELECT SUM(rice) FROM records WHERE date=:date and scheme=:scheme",{'date':date, 'scheme':  card_type})
# 		resp = c.fetchone()[0]
# 		total = resp + total 
# 		rows.append([card_type, resp])
# 	rows.append(["Total", total])
# 	generateTable(header=header, rows=rows)

# 	total = 0
# 	rows = []
# 	header= ["Kejriwal sugar sold", "Quantity (kg)"]
# 	for card_type in card_types:
# 		c.execute("SELECT SUM(sugar) FROM records WHERE date=:date and scheme=:scheme",{'date':date, 'scheme':  card_type})
# 		resp = c.fetchone()[0]
# 		total = resp + total 
# 		rows.append([card_type, resp])
# 	rows.append(["Total", total])
# 	generateTable(header=header, rows=rows)

# conn.close()
