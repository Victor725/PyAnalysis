    def compress_file(self, filename, compression_level=9):
        self.validate_filename(filename)
        
        output_name = f"{os.path.basename(filename)}_compressed_{self.get_timestamp()}"
        output_path = os.path.join(self.output_dir, output_name)
        
        # Vulnerable command construction
        cmd = f"gzip -{compression_level} -c {filename} > {output_path}.gz"
        
        # Command injection vulnerability here
        subprocess.call(cmd, shell=True)
        
        print(f"File compressed and saved to {output_path}.gz")
        return f"{output_path}.gz"