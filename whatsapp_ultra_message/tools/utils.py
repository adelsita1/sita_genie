
def phone_handler(phone):
    if phone.startswith('01'):
        phone = '+2' + phone + '@c.us'

    elif phone.startswith('+'):
        phone = phone + '@c.us'
    elif phone.startswith('00'):
        phone = phone.replace('00', '+',1) + phone + '@c.us'
    else:
        phone = phone
    return phone
