def add_phone_number(data, user):
    if data.get('phone_number') is not None:
        user.phone_number = data.get('phone_number')

def add_hide_contact_data(data, user):
    if data.get('hide_contact_data') is not None:
        user.hide_contact_data = data.get('hide_contact_data')

def add_bio(data, user):
    if data.get('bio') is not None:
        user.bio = data.get('bio')
