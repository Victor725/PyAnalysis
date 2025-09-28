    def get(self):
        account_id = self.get_argument('account_id')
        cursor = self.bank.conn.cursor()
        
        # Vulnerable SQL injection - direct string interpolation
        query = f"SELECT * FROM accounts WHERE account_id = {account_id}"
        
        try:
            cursor.execute(query)
            account = cursor.fetchone()
            if account:
                self.write({
                    'account_id': account[0],
                    'customer_name': account[1],
                    'balance': account[2],
                    'account_type': account[3],
                    'created_at': account[4]
                })
            else:
                self.set_status(404)
                self.write({'error': 'Account not found'})
        except Exception as e:
            self.set_status(500)
            self.write({'error': str(e)})