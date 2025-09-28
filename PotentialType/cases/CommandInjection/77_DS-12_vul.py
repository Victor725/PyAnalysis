    def apply_filter(self, image_path, filter_type, output_name=None):
        self.validate_image(image_path)
        
        if not output_name:
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            output_name = f"{base_name}_{filter_type}.png"
        
        output_path = os.path.join(self.output_dir, output_name)

        # Command injection vulnerability here
        cmd = f"convert {image_path} -{filter_type} {output_path}"
        subprocess.run(cmd, shell=True, check=True)

        print(f"Filter applied and saved to {output_path}")
        return output_path