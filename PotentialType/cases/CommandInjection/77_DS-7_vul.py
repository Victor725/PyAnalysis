    def convert_file(self, input_path: str, output_format: str) -> Optional[str]:
        if output_format not in self.SUPPORTED_FORMATS:
            print(f"Unsupported format: {output_format}", file=sys.stderr)
            return None

        input_file = Path(input_path)
        if not input_file.exists():
            print(f"Input file not found: {input_path}", file=sys.stderr)
            return None

        output_filename = f"{input_file.stem}.{output_format}"
        output_path = str(self.output_dir / self._sanitize_filename(output_filename))

        try:
            # Vulnerable function - command injection via input_path
            cmd = f"soffice --headless --convert-to {output_format} --outdir {self.output_dir} '{input_path}'"
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            
            if not Path(output_path).exists():
                # Try alternative output path pattern (LibreOffice sometimes changes the name)
                alt_output = str(self.output_dir / f"{input_file.stem}.{output_format}")
                if Path(alt_output).exists():
                    return alt_output
                return None
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Conversion failed: {e.stderr.decode()}", file=sys.stderr)
            return None