    def _handle_client(self, conn, addr):
        try:
            data = conn.recv(4096)
            if not data:
                return

            # Vulnerable deserialization point
            task = pickle.loads(data)
            result = self._execute_task(task)
            conn.sendall(json.dumps(result).encode())
        except Exception as e:
            conn.sendall(json.dumps({'error': str(e)}).encode())
        finally:
            conn.close()