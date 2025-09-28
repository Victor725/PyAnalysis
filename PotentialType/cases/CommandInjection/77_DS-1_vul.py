    def search_files(self, keyword):
        # Vulnerable function - command injection via keyword
        try:
            result = subprocess.check_output(
                f"grep -l '{keyword}' {self.base_dir}/*",
                shell=True,
                stderr=subprocess.STDOUT
            )
            return result.decode().splitlines()
        except subprocess.CalledProcessError:
            return []