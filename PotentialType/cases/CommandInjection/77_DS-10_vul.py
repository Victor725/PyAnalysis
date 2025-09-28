    def configure_kernel_param(self, param: str, value: str) -> bool:
        # Vulnerable function - command injection via param/value
        try:
            cmd = f"sysctl -w net.ipv4.{param}='{value}'"
            subprocess.run(cmd, shell=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to configure parameter: {e}", file=sys.stderr)
            return False