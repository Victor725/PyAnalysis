    def test_curl_request(self, url: str, data: Optional[Dict] = None) -> str:
        # Vulnerable function - command injection via url or data
        try:
            data_str = ""
            if data:
                data_str = f"-d '{json.dumps(data)}'"
            cmd = f"curl -X POST {data_str} {url}"
            result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            return result.decode()
        except subprocess.CalledProcessError as e:
            return e.output.decode()