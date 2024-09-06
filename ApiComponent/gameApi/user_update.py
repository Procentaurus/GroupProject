def update_phone_number(data, user):
    if data.get('phone_number') is not None:
        user.phone_number = data.get('phone_number')

def update_hide_contact_data(data, user):
    if data.get('hide_contact_data') is not None:
        user.hide_contact_data = data.get('hide_contact_data')

def update_bio(data, user):
    if data.get('bio') is not None:
        user.bio = data.get('bio')

def update_username(data, user):
    if data.get('username') is not None:
        user.username = data.get('username')

def update_email(data, user):
    if data.get('email') is not None:
        user.email = data.get('email').lower()
