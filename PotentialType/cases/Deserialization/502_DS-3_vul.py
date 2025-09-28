    def store_config(self, device_id, config_data):
        try:
            # Vulnerable deserialization - accepts pickled network data
            config = pickle.loads(config_data)
            if not self._validate_config(config):
                return False
            
            encrypted_config = self.cipher.encrypt(pickle.dumps(config['config']))
            self.devices[device_id] = {
                'hostname': config['hostname'],
                'ip': config['ip'],
                'config': encrypted_config
            }
            self.config_versions[device_id] = self.config_versions.get(device_id, 0) + 1
            return True
        except Exception as e:
            print(f"Config storage failed: {e}")
            return False