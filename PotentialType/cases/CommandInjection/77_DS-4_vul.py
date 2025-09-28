    def create_backup(self, tables: Optional[List[str]] = None) -> bool:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"{self.db_name}_{timestamp}.sql")
        
        try:
            if tables:
                tables_str = " ".join(tables)
                # Vulnerable function - command injection via table names
                cmd = f"pg_dump -U {self.db_user} -d {self.db_name} -t {tables_str} > {backup_file}"
            else:
                cmd = f"pg_dump -U {self.db_user} -d {self.db_name} > {backup_file}"
            
            subprocess.run(cmd, shell=True, check=True)
            return os.path.exists(backup_file)
        except subprocess.CalledProcessError as e:
            print(f"Backup failed: {e}", file=sys.stderr)
            return False