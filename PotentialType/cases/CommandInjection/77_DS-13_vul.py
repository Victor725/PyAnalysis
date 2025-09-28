    def create_backup(self, db_type, db_name, db_user, db_password, host="localhost"):
        self.validate_db_type(db_type)
        backup_file = os.path.join(self.backup_dir, self.generate_backup_name(db_type))

        # Command injection vulnerability here
        if db_type == 'mysql':
            cmd = (f"mysqldump -u {db_user} -p{db_password} -h {host} {db_name} "
                  f"> {backup_file}")
        elif db_type == 'postgresql':
            cmd = (f"pg_dump -U {db_user} -h {host} {db_name} "
                  f"> {backup_file}")
        else:  # mongodb
            cmd = (f"mongodump --host {host} --username {db_user} "
                  f"--password {db_password} --db {db_name} --out {backup_file}")

        subprocess.run(cmd, shell=True, check=True)
        print(f"Backup created at {backup_file}")
        return backup_file