import time
import json
import sys
import getpass
import os
import calendar

# 🔖 Config folder
# OS অনুযায়ী storage path ঠিক করা
if os.name == 'nt':  # Windows
	Folder = os.path.join(os.getenv('USERPROFILE'), "student_data")
else:
	Folder = "/storage/emulated/0/abc_result"

# Folder তৈরি (exist না থাকলে)
if not os.path.exists(Folder):
	os.makedirs(Folder)

config_path = os.path.join(Folder, "python", "config.json")
save_password = os.path.join(Folder, "python", "pass_file.json")

# 🗂️ Ensure folder exists
if not os.path.exists(Folder):
	os.makedirs(Folder)

# 📁 Create empty config/password file if not exists
if not os.path.exists(config_path):
	with open(config_path, 'w') as f:
		json.dump({}, f)

if not os.path.exists(save_password):
	with open(save_password, 'w') as f:
		json.dump([], f)

result_file = ""
current_class = ""
current_term = ""
current_year = ""

def clear_screen():
	os.system('cls' if os.name == 'nt' else 'clear')

def printx(text, delay=0.02):
	for x in text:
		sys.stdout.write(x)
		sys.stdout.flush()
		time.sleep(delay)
	print()

def save_config(class_, term_, year_):
	data = {"class": class_, "term": term_, "year": year_}
	with open(config_path, 'w') as f:
		json.dump(data, f, indent=4)

def load_config():
	if not os.path.exists(config_path):
		return None
	with open(config_path, 'r') as f:
		try:
			data = json.load(f)
			return data
		except:
			return None

def get_result_filepath():
	global current_class, current_term, current_year

	conf = load_config()
	now_year = calendar.datetime.datetime.now().year

	while True:
		if conf and "class" in conf:
			class_input = conf["class"]
		else:
			class_input = input("📚 Enter class (1 to 5): ").strip()
		if class_input in ['1', '2', '3', '4', '5']:
			break
		else:
			printx("❌ Invalid class! Must be 1 to 5.")
			conf = None

	if conf and "year" in conf:
		year = conf["year"]
	else:
		year = input(f"📅 Enter exam year ({now_year}): ").strip()
		if year == "":
			year = str(now_year)
	if not year.isdigit():
		printx("⚠️ Invalid year! Using current year.")
		year = str(now_year)

	terms_map = {"1": "term_1", "2": "term_2", "3": "term_3"}
	if conf and "term" in conf:
		term = conf["term"]
	else:
		while True:
			print("\n📝 Select Exam Term:\n1️⃣. Term 1\n2️⃣. Term 2\n3️⃣. Term 3\n")
			term_input = input("Enter term number: ").strip()
			if term_input in terms_map:
				term = terms_map[term_input]
				break
			else:
				printx("🚫 Invalid term! Try again.")

	current_class = class_input
	current_term = term
	current_year = year

	save_config(current_class, current_term, current_year)

	subfolder = os.path.join(Folder, "_results", year, f"class_{current_class}")
	if not os.path.exists(subfolder):
		os.makedirs(subfolder)

	filename = f"{term}.json"
	filepath = os.path.join(subfolder, filename)

	if not os.path.exists(filepath):
		with open(filepath, 'w') as f:
			json.dump([], f, indent=4)

	return filepath

def add_student():
	clear_screen()
	printx("📥 Add New Student\n")
	
	while True:
		with open(result_file, 'r') as f:
			pre_data = json.load(f)
		print(f"Type 'exit' anytime to return\n\n")
		new_roll = input("🎯 Enter new student roll: ").strip()
		if new_roll.lower() == 'exit':
			main_menu()
			return

		# 🔍 Check for duplicate roll
		duplicate = False
		for x in pre_data:
			if new_roll == x['Roll']:
				clear_screen()
				printx("⚠️ Roll already exists.")
				print(f'\nRoll: {x["Roll"]}\nName: {x["Name"]}')
				duplicate = True
				break
		if duplicate:
			continue

		new_name = input("🧑 Enter student name: ").strip()
		if new_name.lower() == 'exit':
			main_menu()
		
		marks = {}
		subjects = ["Bangla", "English", "Math", "Social", "Science", "Religion"]
		for subject in subjects:
			while True:
				try:
					mark = input(f"📘 {subject} marks: ").strip()
					if mark.lower() == 'exit':
						main_menu()
						return
					mark = int(mark)
					if 0 <= mark <= 100:
						marks[subject] = mark
						break
					else:
						print("❌ 0-100 only.")
				except:
					print("⚠️ Invalid number.")

		pre_data.append({"Roll": new_roll, "Name": new_name, "Marks": marks})

		with open(result_file, 'w') as f:
			json.dump(pre_data, f, indent=4)
		printx("✅ Student added successfully!")
		time.sleep(0.5)
		clear_screen()
		print("➕ Add another student\n")

def modify_data():
	clear_screen()
	printx("✏️ Modify Student Info\n")
	mod_roll = input("🎯 Enter roll number: ").strip()
	with open(result_file, 'r') as f:
		mod_data = json.load(f)

	for x in mod_data:
		if mod_roll == x["Roll"]:
			print(f'\nRoll: {x["Roll"]}\nCurrent Name: {x["Name"]}\n')
			new_name = input("🔤 New name (leave blank to keep): ").strip()
			if new_name:
				x["Name"] = new_name

			subjects = ["Math", "English", "Science", "Bangla", "ICT", "Religion"]
			for subject in subjects:
				current = x["Marks"].get(subject, "N/A")
				new_mark = input(f"{subject} (now {current}): ").strip()
				if new_mark:
					try:
						val = int(new_mark)
						if 0 <= val <= 100:
							x["Marks"][subject] = val
					except:
						pass

			with open(result_file, 'w') as f:
				json.dump(mod_data, f, indent=4)
			printx("🔄 Data updated!")
			time.sleep(1)
			main_menu()
			return

	print("❌ Roll not found.")
	time.sleep(1)
	main_menu()

def delete_data():
	clear_screen()
	verify_pass()
	confirm = input("🗑️ Delete all data? (y/n): ").strip().lower()
	if confirm == "y":
		with open(result_file, 'w') as f:
			json.dump([], f, indent=4)
		print("✅ All data deleted.")
	time.sleep(1)
	main_menu()

def st_manager():
	clear_screen()
	printx("📚 Student Management")
	print("\n1. ➕ Add student\n2. ✏️ Modify student\n3. 🗑️ Delete all data\n\nEnter = Main menu\n\n")
	choice = input("🔢 Choice: ").strip()
	if choice == "1":
		clear_screen()
		add_student()
	elif choice == "2":
		clear_screen()
		modify_data()
	elif choice == "3":
		clear_screen()
		delete_data()
	else:
		main_menu()

def all_result():
	clear_screen()
	with open(result_file, 'r') as f:
		data = json.load(f)
	data.sort(key=lambda x: x['Roll'])
	for i, student in enumerate(data):
		print(f"{i+1}. Roll: {student['Roll']}, Name: {student['Name']}")
		total = sum(student["Marks"].values())
		for sub, mark in student["Marks"].items():
			print(f"   {sub}: {mark}")
		print(f"   📊 Total: {total}\n")
	input("🔙 Press Enter...")
	main_menu()

def view_by_roll():
	clear_screen()
	search_roll = input("🎯 Enter roll: ").strip()
	with open(result_file, 'r') as f:
		data = json.load(f)
	for s in data:
		if s["Roll"] == search_roll:
			print(f"Roll: {s['Roll']}\nName: {s['Name']}")
			total = 0
			for sub, mark in s["Marks"].items():
				print(f"{sub}: {mark}")
				total += mark
			print(f"📊 Total: {total}")
			break
	else:
		print("❌ Roll not found.")
	input("\n🔙 Press enter...")
	main_menu()

def view_results():
	clear_screen()
	printx("📄 Result Management")
	print("\n1. 📋 View all\n2. 🔍 Search by roll\n\nEnter = Main menu\n")
	choice = input("🔢 Choice: ").strip()
	if choice == "1":
		all_result()
	elif choice == "2":
		view_by_roll()
	else:
		main_menu()

def verify_pass():
	with open(save_password, 'r') as f:
		users = json.load(f)
	if users == []:
		return
	user = users[0]
	for i in range(4, 0, -1):
		print(f"🔒 Password for {user['Username']}:")
		if getpass.getpass() == user["Password"]:
			return
		else:
			print(f"❌ Wrong! {i-1} attempts left.")
	print("🔐 Too many tries!")
	sys.exit()

def set_password():
	with open(save_password, 'r') as f:
		pwd = json.load(f)
	if pwd == []:
		u = input("👤 New Username: ")
		p1 = getpass.getpass("🔑 New Password: ")
		p2 = getpass.getpass("🔁 Re-type Password: ")
		if p1 != p2:
			print("❌ Mismatch!")
			set_password()
		else:
			with open(save_password, 'w') as f:
				json.dump([{"Username": u, "Password": p1}], f)
			print("✅ Password set!")
	else:
		verify_pass()
		p1 = getpass.getpass("🔁 New Password: ")
		pwd[0]["Password"] = p1
		with open(save_password, 'w') as f:
			json.dump(pwd, f)
		print("✅ Password changed.")

def pass_manager():
	clear_screen()
	with open(save_password, 'r') as f:
		data = json.load(f)
	if data == []:
		print("\n1. 🔐 Set Password\n\n🔙Enter to main menu\n")
	else:
		print("\n1. 🔁 Change Password\n2. ❌ Remove Password\n\3. 🔙Enter to return\n")
	choice = input("🔢 Choice: ").strip()
	if choice == "":
		main_menu()
	
	elif choice == "1":
		set_password()
	elif choice == "2" and data:
		verify_pass()
		with open(save_password, 'w') as f:
			json.dump([], f)
		print("✅ Password removed.")
	main_menu()

def change_student_file():
	confirm = input("⚠️ Change file? This will reset config (y/n): ").strip().lower()
	if confirm == 'y':
		with open(config_path, 'w') as f:
			json.dump({}, f)
		print("🧹 Config reset. Restart to continue.")
		time.sleep(2)
		sys.exit()
	else:
		main_menu()

def main_menu():
	clear_screen()
	conf = load_config()
	loc = ""
	if conf and "class" in conf and "term" in conf and "year" in conf:
		loc = f"(📚 Class {conf['class']}, 📝 {conf['term']}, 📅 {conf['year']})"
	printx(f"	🏫 ABC School\n{loc}\n", 0.03)
	print("1. 👨‍🎓 Student Management\n2. 📄 Result Management\n3. 🔐 Password Manager\n4. 🔁 Change Student File\n5. ❎ Exit\n")
	a = input("🔢 Enter choice: ").strip()
	if a == "1":
		st_manager()
	elif a == "2":
		view_results()
	elif a == "3":
		pass_manager()
	elif a == "4":
		change_student_file()
	elif a == "5":
		sys.exit()
	else:
		print("❌ Invalid input.")
		time.sleep(1)
		main_menu()

# 🚀 Start the program
verify_pass()
result_file = get_result_filepath()
main_menu()