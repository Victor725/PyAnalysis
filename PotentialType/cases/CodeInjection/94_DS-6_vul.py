    def vulnerable_apply_config(self, config_name: str, config_logic: str):
        try:
            # Vulnerable code injection in config evaluation
            exec(config_logic, self.environment, locals())
            self.configs[config_name] = locals().get('config_value')
            return True
        except Exception as e:
            return str(e)