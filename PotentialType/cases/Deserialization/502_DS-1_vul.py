    def do_POST(self):
        if self.path == '/upload_config':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            if self.analytics.process_config_upload(post_data):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Config uploaded successfully')
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Failed to upload config')
        
        elif self.path == '/record':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            event_data = json.loads(post_data.decode())
            
            if self.analytics.record_event(event_data):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Event recorded')
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid event data')
        
        else:
            self.send_response(404)
            self.end_headers()