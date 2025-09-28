    def capture_website(self, url, browser='chrome', delay=2, full_page=False):
        if not self.validate_url(url):
            raise ValueError("Invalid URL provided")

        output_file = os.path.join(self.output_dir, self.generate_filename(url))

        # Command injection vulnerability here
        if browser == 'chrome':
            cmd = (f"wkhtmltoimage --delay {delay} {'--enable-javascript' if full_page else ''} "
                  f"{url} {output_file}")
        elif browser == 'firefox':
            cmd = f"cutycapt --url={url} --out={output_file} --delay={delay}"
        else:  # webkit
            cmd = f"phantomjs rasterize.js {url} {output_file}"

        subprocess.run(cmd, shell=True, check=True)
        print(f"Screenshot saved to {output_file}")
        return output_file