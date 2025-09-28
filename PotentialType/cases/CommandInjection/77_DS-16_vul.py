    def execute_system_check(self, check_type, custom_command=None):
        self.validate_check_type(check_type)
        log_file = os.path.join(self.log_dir, self.generate_log_filename(check_type))

        # Command injection vulnerability here
        if check_type == 'cpu':
            cmd = f"top -bn1 | grep 'Cpu(s)' > {log_file}"
        elif check_type == 'memory':
            cmd = f"free -h > {log_file}"
        elif check_type == 'disk':
            cmd = f"df -h > {log_file}"
        elif check_type == 'network':
            cmd = f"netstat -tuln > {log_file}"
        else:  # custom
            cmd = f"{custom_command} > {log_file}"

        subprocess.run(cmd, shell=True, check=True)
        print(f"Check completed. Results logged to {log_file}")
        return log_file