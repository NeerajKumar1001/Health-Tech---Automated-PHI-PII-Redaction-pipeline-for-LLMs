import random

otp_store = {}

def save_otp(email):
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    return otp

def verify_otp(email, otp):
    return otp_store.get(email) == otp