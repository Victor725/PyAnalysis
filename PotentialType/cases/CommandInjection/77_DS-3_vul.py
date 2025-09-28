    def search_logs(self, pattern, case_sensitive=False):
        # Vulnerable function - command injection via pattern
        try:
            grep_flags = "-i" if not case_sensitive else ""
            cmd = f"grep {grep_flags} '{pattern}' {os.path.join(self.log_dir, '*.log')}"
            results = subprocess.check_output(
                cmd,
                shell=True,
                stderr=subprocess.PIPE
            )
            return results.decode().splitlines()
        except subprocess.CalledProcessError:
            return []