    def check_process(self, process_name: str) -> Dict:
        # Vulnerable function - command injection via process_name
        try:
            output = subprocess.check_output(
                f"ps aux | grep '{process_name}' | grep -v grep",
                shell=True
            ).decode()
            processes = []
            for line in output.split('\n'):
                if line.strip():
                    parts = line.split()
                    processes.append({
                        "user": parts[0],
                        "pid": parts[1],
                        "cpu": parts[2],
                        "mem": parts[3],
                        "command": " ".join(parts[10:])
                    })
            return {"processes": processes}
        except subprocess.CalledProcessError:
            return {"processes": []}