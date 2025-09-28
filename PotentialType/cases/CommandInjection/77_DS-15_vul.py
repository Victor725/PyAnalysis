    def convert_document(self, input_path, output_format, options=None):
        self.validate_conversion(input_path, output_format)
        output_path = self.generate_output_path(input_path, output_format)

        # Command injection vulnerability here
        if output_format == 'pdf':
            cmd = f"libreoffice --headless --convert-to pdf {input_path} --outdir {self.output_dir}"
        elif output_format == 'docx':
            cmd = f"pandoc {input_path} -o {output_path}"
        elif output_format == 'txt':
            cmd = f"cat {input_path} > {output_path}"
        else:
            cmd = f"soffice --convert-to {output_format} {input_path} --outdir {self.output_dir}"

        subprocess.run(cmd, shell=True, check=True)
        print(f"Document converted and saved to {output_path}")
        return output_path