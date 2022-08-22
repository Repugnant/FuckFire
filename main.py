import requests
from bs4 import BeautifulSoup
from os import mkdir, getcwd
import argparse
import re
from contextlib import suppress
from pathlib import Path

regex = re.compile(r"(https?:\/\/)?(www\.)?(mediafire\.com)\/(folder)\/([a-z0-9A-Z]*)\/?(.+)?")

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

	folder_key = regex.match(folder_url)[5]
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

	folder_key = regex.match(folder_url)[5]
	API_FILES_REQUEST = f"https://www.mediafire.com/api/1.4/folder/get_content.php?r=tnuc&content_type=files&filter=all&order_by=name&order_direction=asc&chunk=1&version=1.5&folder_key={folder_key}&response_format=json"

	# Making requests
	r = requests.get(API_FILES_REQUEST)
	r_json = r.json()
	
	# Making dir
	with suppress(FileExistsError):
		path = Path(dir_)
		path.mkdir(parents=True, exist_ok=False)
		print(f"[+] Folder: '{path.absolute()}' created.")

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
	folder = regex.match(URL)
	if (folder is None):
		print("[-] Invalid URL")
		return

	folder_key = folder[5]
	dir_ = f"{getcwd()}/downloads/{folder_key}"

	download_files_from_folder(URL, dir_)

	while is_there_folders(URL):

		for folder in is_there_folders(URL):
			folder_url = folder["url"]
			folder_name = folder["name"]

			dir_ += f"{folder_name}/"

			download_files_from_folder(folder_url, dir_)

			URL = folder_url

if __name__ == "__main__":
	try:
		main()

	except KeyboardInterrupt:
		print("\nClosing...")
