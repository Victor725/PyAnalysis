    def post(self):
        try:
            data = json.loads(self.request.body)
            username = data['username']
            password = data['password']
            email = data.get('email', '')

            db = Database()
            cursor = db.conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                (username, db.hash_password(password), email)
            )
            db.conn.commit()
            self.write(json.dumps({'status': 'success'}))
        except sqlite3.IntegrityError:
            raise tornado.web.HTTPError(400, "Username already exists")