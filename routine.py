import os
import pyotp
import robin_stocks.robinhood as rh

def login():
    totp = pyotp.TOTP(os.environ['MFA_KEY']).now()
    login = rh.login(os.environ['RH_USERNAME'], os.environ['RH_PASSWORD'], mfa_code=totp)
    return login

def main():
    login_info = login()
    my_stocks = rh.build_holdings()
    for _key, _value in my_stocks.items():
        print(_key, _value)

if __name__ == '__main__':
    main()
