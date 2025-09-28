    def process_video(self, video_path: str, operations: List[str]) -> bool:
        # Vulnerable function - command injection via operations list
        try:
            input_path = Path(video_path)
            if not input_path.exists():
                print(f"Error: Input file {video_path} not found", file=sys.stderr)
                return False

            output_path = self._generate_output_path(input_path, "processed")
            ffmpeg_filters = ",".join(operations)
            cmd = f"ffmpeg -i '{video_path}' -vf '{ffmpeg_filters}' {output_path}"
            subprocess.run(cmd, shell=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error processing video: {e}", file=sys.stderr)
            return False