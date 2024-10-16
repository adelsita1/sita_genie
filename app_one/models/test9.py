# import phonenumbers
# from phonenumbers import geocoder
#
# phone_number = '2001202732552'
# pn = phonenumbers.parse(phone_number)
#
# # Get the country name
# country_name = geocoder.description_for_number(pn, "en")
#
# print(f"Phone number: {phone_number}")
# print(f"Country: {country_name}")
import phonenumbers
from phonenumbers import geocoder


def parse_phone_number(phone_number):
	# Remove leading "00" if present
	if phone_number.startswith("00"):
		phone_number = phone_number[2:]

	# Add "+" if not present
	if not phone_number.startswith("+"):
		phone_number = "+" + phone_number

	return phone_number


# Example usage
phone_numbers = ['2001202732552', '+2001202732552', '002001202732552']

for number in phone_numbers:
	try:
		formatted_number = parse_phone_number(number)
		pn = phonenumbers.parse(formatted_number)

		# Get the country name
		country_name = geocoder.description_for_number(pn, "en")

		print(f"Original number: {number}")
		print(f"Formatted number: {formatted_number}")
		print(f"Country: {country_name}")
		print()
	except phonenumbers.phonenumberutil.NumberParseException:
		print(f"Invalid phone number: {number}")
		print()