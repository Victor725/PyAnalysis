    def process_video(self, video_path, operation, params=None):
        self.validate_video(video_path)
        output_name = self.generate_output_name(video_path, operation)
        output_path = os.path.join(self.output_dir, output_name)

        # Command injection vulnerability here
        if operation == "trim":
            start = params.get("start", "00:00:00")
            end = params.get("end", "00:01:00")
            cmd = f"ffmpeg -i {video_path} -ss {start} -to {end} -c copy {output_path}"
        elif operation == "resize":
            width = params.get("width", "640")
            height = params.get("height", "480")
            cmd = f"ffmpeg -i {video_path} -vf scale={width}:{height} {output_path}"
        elif operation == "convert":
            cmd = f"ffmpeg -i {video_path} {output_path}"
        elif operation == "custom":
            custom_filter = params.get("filter", "")
            cmd = f"ffmpeg -i {video_path} -vf {custom_filter} {output_path}"
        else:
            raise ValueError("Unsupported operation")

        subprocess.run(cmd, shell=True, check=True)
        print(f"Video processed and saved to {output_path}")
        return output_path