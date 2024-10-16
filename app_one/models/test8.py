# from PyPDF2 import PdfReader, PdfWriter
#
#
# def remove_images_from_pdf(input_path, output_path):
# 	reader = PdfReader(input_path)
# 	writer = PdfWriter()
#
# 	for page in reader.pages:
# 		# Remove images
# 		if '/Resources' in page:
# 			if '/XObject' in page['/Resources']:
# 				del page['/Resources']['/XObject']
#
# 		# Add the modified page to the writer
# 		writer.add_page(page)
#
# 	# Save the modified PDF
# 	with open(output_path, "wb") as f:
# 		writer.write(f)
#
#
# # Example usage
# input_pdf = "/home/catherine/Desktop/SITA/odoo/odoo17/custom_modules/app_one/models/output.pdf"
# output_pdf = "/home/catherine/Desktop/SITA/odoo/odoo17/custom_modules/app_one/models/output_no_images.pdf"
#
# try:
# 	remove_images_from_pdf(input_pdf, output_pdf)
# 	print(f"Images removed. New PDF saved as {output_pdf}")
# except Exception as e:
# 	print(f"An error occurred: {str(e)}")
# import asyncio
# from pyppeteer import launch
#
#
# async def generate_pdf(url, pdf_path):
# 	browser = await launch()
# 	page = await browser.newPage()
#
# 	await page.goto(url)
#
# 	await page.pdf({'path': pdf_path, 'format': 'A4'})
#
# 	await browser.close()
#
#
# # Run the function
# asyncio.get_event_loop().run_until_complete(generate_pdf('https://tolipgroup.com/', '/home/catherine/Desktop/SITA/odoo/odoo17/custom_modules/app_one/models/example.pdf'))
import asyncio
import xml.etree.ElementTree as ET
from pyppeteer import launch
from PyPDF2 import PdfMerger
import tempfile
import os
async def process_url(url, temp_dir):
	browser = await launch()
	page = await browser.newPage()

	try:
		await page.goto(url, waitUntil = 'networkidle0', timeout = 30000)
		pdf_path = os.path.join(temp_dir, f"{hash(url)}.pdf")
		await page.pdf({'path': pdf_path, 'format': 'A4'})
		return pdf_path
	except Exception as e:
		print(f"Error processing URL {url}: {str(e)}")
		return None
	finally:
		await browser.close()
def extract_urls_from_sitemap(sitemap_path):
	tree = ET.parse(sitemap_path)
	root = tree.getroot()
	namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

	urls = []
	for url in root.findall('.//ns:loc', namespace):
		urls.append(url.text)
	return urls


async def generate_combined_pdf(sitemap_path, output_pdf_path):
	urls = extract_urls_from_sitemap(sitemap_path)

	with tempfile.TemporaryDirectory() as temp_dir:

		tasks = [process_url(url, temp_dir) for url in urls]
		pdf_paths = await asyncio.gather(*tasks)
		pdf_paths = [p for p in pdf_paths if p is not None]
		merger = PdfMerger()
		for pdf_path in pdf_paths:
			merger.append(pdf_path)

		merger.write(output_pdf_path)
		merger.close()


def main():
	sitemap_path = '/home/catherine/Desktop/SITA/odoo/odoo17/custom_modules/app_one/models/sitemap.xml'
	output_pdf_path = '/home/catherine/Desktop/SITA/odoo/odoo17/custom_modules/app_one/models/combined.pdf'

	asyncio.get_event_loop().run_until_complete(
		generate_combined_pdf(sitemap_path, output_pdf_path)
	)
	print(f"Combined PDF has been generated at: {output_pdf_path}")


if __name__ == "__main__":
	main()