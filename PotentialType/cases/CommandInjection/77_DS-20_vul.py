    def get_system_info(self, info_type='all', custom_command=None):
        self.validate_info_type(info_type)
        output_file = os.path.join(self.output_dir, self.generate_filename(info_type))

        # Command injection vulnerability here
        if info_type == 'all':
            cmd = f"(uname -a; lscpu; free -h; df -h; ifconfig) > {output_file}"
        elif info_type == 'hardware':
            cmd = f"(lshw -short 2>/dev/null || system_profiler SPHardwareDataType) > {output_file}"
        elif info_type == 'software':
            cmd = f"(dpkg -l || rpm -qa || brew list) > {output_file}"
        elif info_type == 'network':
            cmd = f"(ifconfig || ip addr) > {output_file}"
        else:  # custom
            cmd = f"{custom_command} > {output_file}"

        subprocess.run(cmd, shell=True, check=True)
        print(f"System info saved to {output_file}")
        return output_file