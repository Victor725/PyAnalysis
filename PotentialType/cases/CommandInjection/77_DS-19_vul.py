    def perform_lookup(self, domain, lookup_type='A', custom_type=None):
        self.validate_domain(domain)
        output_file = os.path.join(self.output_dir, self.generate_filename(domain, lookup_type))

        # Command injection vulnerability here
        if lookup_type == 'custom':
            if not custom_type:
                raise ValueError("Custom type required")
            cmd = f"dig {domain} {custom_type} +short > {output_file}"
        else:
            cmd = f"dig {domain} {lookup_type} +short > {output_file}"

        subprocess.run(cmd, shell=True, check=True)
        print(f"Results saved to {output_file}")
        return output_file