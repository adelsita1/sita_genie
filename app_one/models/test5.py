import asyncio
import pyppeteer
import xml.etree.ElementTree as ET
from PyPDF2 import PdfMerger
import os
import tempfile


async def convert_website_to_pdf(url, pdf_path):
	browser = await pyppeteer.launch()
	page = await browser.newPage()
	await page.goto(url, waitUntil = 'networkidle0')
	await page.pdf({'path': pdf_path, 'format': 'A4'})
	await browser.close()


def read_xml_file(file_path):
	try:
		with open(file_path, 'r', encoding = 'utf-8') as file:
			return file.read()
	except Exception as e:
		print(f"Error reading XML file: {e}")
		return None


def parse_sitemap(xml_content):
	root = ET.fromstring(xml_content)
	urls = []
	for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
		loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
		if loc is not None:
			urls.append(loc.text)
	return urls


async def process_all_urls(urls, output_pdf_path):
	temp_pdfs = []


	for i, url in enumerate(urls):
		print(f"Processing URL {i + 1}/{len(urls)}: {url}")
		temp_pdf = os.path.join(tempfile.gettempdir(), f'temp_{i}.pdf')
		await convert_website_to_pdf(url, temp_pdf)
		temp_pdfs.append(temp_pdf)


	merger = PdfMerger()
	for pdf in temp_pdfs:
		merger.append(pdf)

	merger.write(output_pdf_path)
	merger.close()


	for pdf in temp_pdfs:
		os.remove(pdf)


async def main():

	xml_file_path = '/home/catherine/Desktop/SITA/odoo/odoo17/custom_modules/app_one/models/sitemap.xml'
	output_pdf_path = '/home/catherine/Desktop/SITA/odoo/odoo17/custom_modules/app_one/models/output.pdf'

	xml_content = read_xml_file(xml_file_path)
	if xml_content is None:
		return

	# Parse URLs and process them
	urls = parse_sitemap(xml_content)
	if urls:
		print(f"Found {len(urls)} URLs to process")
		await process_all_urls(urls, output_pdf_path)
		print(f"PDF has been created at: {output_pdf_path}")
	else:
		print("No URLs found in the sitemap")


if __name__ == "__main__":
	asyncio.run(main())