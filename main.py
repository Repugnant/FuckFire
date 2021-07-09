import requests
from bs4 import BeautifulSoup
from os import chdir, mkdir, getcwd
import argparse


def parse_args():
	parser = argparse.ArgumentParser(description="Procees input Url")
	parser.add_argument("--url", "-u", help="Enter here your folder Url")

	args = parser.parse_args()

	if not args.url:
		print("Usage: python3 main.py -u [Folder_Url]")
		exit()

	return args.url

def is_there_folders(folder_url):
	""" Search folders in the main folder and returns their info """

	folders = []

	folder_key = folder_url.split("/")[4]
	API_FOLDER_REQUEST = f"https://www.mediafire.com/api/1.4/folder/get_content.php?r=tnuc&content_type=all&filter=all&order_by=name&order_direction=asc&chunk=1&version=1.5&folder_key={folder_key}&response_format=json"

	# Making requests
	r = requests.get(API_FOLDER_REQUEST)
	r_json = r.json()

	# Finding folders
	for folder in r_json["response"]["folder_content"]["folders"]:
		folder_name = folder["name"]
		folder_key = folder["folderkey"]
		
		folders.append(
			{
				"url": f"https://www.mediafire.com/folder/{folder_key}/{folder_name}",
				"name": folder_name,
			}
		)

	return folders


def download_files_from_folder(folder_url, dir_):
	""" Download all files from a folder """

	folder_key = folder_url.split("/")[4]
	API_FILES_REQUEST = f"https://www.mediafire.com/api/1.4/folder/get_content.php?r=tnuc&content_type=files&filter=all&order_by=name&order_direction=asc&chunk=1&version=1.5&folder_key={folder_key}&response_format=json"

	# Making requests
	r = requests.get(API_FILES_REQUEST)
	r_json = r.json()
	
	# Making dir
	try:
		mkdir(dir_)

		print(f"[+] Folder: '{dir_}' created.")

	except FileExistsError:
		pass

	# Downloading files
	for file in r_json["response"]["folder_content"]["files"]:
		# Searching for info
		file_name = file["filename"]
		file_link = file["links"]["normal_download"]

		# Scrapping info from web
		r = requests.get(file_link)
		soup = BeautifulSoup(r.text, "lxml")

		# Searching for the direct download link
		download_button_element = soup.find("a", {"class": "input popsok"})
		download_link = download_button_element.attrs["href"]

		# Downloading file
		r = requests.get(download_link)

		with open(f"{dir_}/{file_name}", "wb") as image:
			image.write(r.content)


		print(f"[+] File: '{file_name}' Downloaded.")


def main():
	URL = parse_args()
	dir_ = getcwd() + "/downloads/"

	download_files_from_folder(URL, dir_)

	for folder in is_there_folders(URL):
		folder_url = folder["url"]
		folder_name = folder["name"]

		dir_ += f"{folder_name}/"

		download_files_from_folder(folder_url, dir_)


if __name__ == "__main__":
	try:
		main()

	except KeyboardInterrupt:
		print("\nClosing...")