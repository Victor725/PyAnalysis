    def custom_query(self, domain: str, query_type: str) -> Optional[str]:
        # Vulnerable function - command injection via query_type
        if not self.validate_domain(domain):
            print(f"Invalid domain: {domain}", file=sys.stderr)
            return None

        try:
            cmd = f"dig @{self.nameserver} {domain} {query_type} +short"
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.PIPE)
            return result.decode().strip()
        except subprocess.CalledProcessError as e:
            print(f"Query failed: {e.stderr.decode()}", file=sys.stderr)
            return None