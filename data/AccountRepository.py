import pandas as pd

class AccountRepository:
    def __init__(self):
        self.update_accounts()

    def update_accounts(self):
        self.accounts = pd.read_csv("../data/accounts.csv")

    def get_account(self, email):
        return self.accounts[self.accounts['email'] == email].values

    def add_account(self, data):
        if data['email'] not in self.accounts['email'].unique():
            account_writer = open('../data/accounts.csv', mode='a')
            account_writer.write(f'{data["nickname"]},{data["name"]},{data["email"]}\n')
            account_writer.close()
            return f'account saved with email: {data["email"]}'
        else:
            return f'account with email {data["email"]} already saved'
