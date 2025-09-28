    def process_firmware_update(self, firmware_data):
        try:
            # Vulnerable deserialization - accepts arbitrary pickled firmware metadata
            firmware_meta = pickle.loads(firmware_data['metadata'])
            
            if not self._validate_firmware_metadata(firmware_meta):
                return False

            firmware_id = hashlib.sha256(firmware_data['binary']).hexdigest()
            self.firmware_cache[firmware_id] = {
                'binary': firmware_data['binary'],
                'metadata': firmware_meta
            }
            
            # Schedule updates for compatible devices
            for device_id, device in self.devices.items():
                if device['firmware_version'] in firmware_meta['compatible_versions']:
                    self.command_queue.append({
                        'device_id': device_id,
                        'command': 'UPDATE_FIRMWARE',
                        'firmware_id': firmware_id,
                        'timestamp': str(datetime.utcnow())
                    })
            
            return True
        except Exception as e:
            print(f"Firmware processing failed: {e}")
            return False