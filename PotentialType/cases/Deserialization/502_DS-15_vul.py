    def _handle_connection(self, conn, addr):
        try:
            raw_data = conn.recv(4096)
            if not raw_data:
                return

            # Vulnerable deserialization point
            request = pickle.loads(raw_data)
            response = self._process_request(request)
            conn.sendall(pickle.dumps(response))
        except Exception as e:
            conn.sendall(pickle.dumps({'error': str(e)}))
        finally:
            conn.close()