import phonenumbers
from phonenumbers import PhoneNumberFormat
def json_to_short_text(data):
    text_chunks = []
    for record in data:
        if "id" in record :
            del record["id"]
        chunk = ', '.join(f"{key}: {value}" for key, value in record.items())
        # Limit the size of each chunk
        while len(chunk) > 500:
            # Truncate or split the chunk
            text_chunks.append(chunk[:500])  # Append the first 500 characters
            chunk = chunk[500:]  # Reduce the chunk
        if chunk:
            text_chunks.append(chunk)
    text_chunks_text='\n'.join(text_chunks)    # Append any remaining part
    return text_chunks_text
def format_row(row):

    del row["id"]
    return " ,".join(f"{key.replace("_"," ").title()}:{row[key]}"  for key in row.keys())




def format_phone_number(number, region='EG'):
    try:
        parsed_number = phonenumbers.parse(number, region)
        formatted_number = phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
        return formatted_number
    except phonenumbers.NumberParseException as e:
        print(f"Error: {e}")
        return None
def extract_phone_numbers(text, region='US'):
    phone_numbers = []
    for match in phonenumbers.PhoneNumberMatcher(text, region):
        phone_number = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
        phone_numbers.append(phone_number)
    return phone_numbers
# Example usage
# print(format_phone_number("+201234567890"))