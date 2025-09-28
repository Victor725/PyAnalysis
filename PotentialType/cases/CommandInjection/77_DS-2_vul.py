    def trace_route(self) -> str:
        # Vulnerable function - command injection via target_host
        try:
            trace = subprocess.check_output(
                f"traceroute {self.target_host}",
                shell=True,
                stderr=subprocess.STDOUT
            )
            return trace.decode()
        except subprocess.CalledProcessError as e:
            return e.output.decode()