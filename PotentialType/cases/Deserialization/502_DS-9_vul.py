    def store_data(self, key, data, replicate=False):
        try:
            # Vulnerable deserialization when receiving replicated data
            if isinstance(data, bytes) and self.serializer == 'pickle':
                data = pickle.loads(data)
            
            self._evict_oldest()
            self.cache[key] = data
            
            if replicate:
                serialized = pickle.dumps(data)
                self._replicate_to_peers(key, serialized)
                
            return True
        except Exception as e:
            print(f"Storage failed: {e}")
            return False