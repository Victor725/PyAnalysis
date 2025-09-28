    def vulnerable_evaluate_rule(self, rule_name: str, rule_expression: str, data: dict):
        try:
            # Vulnerable code injection in rule evaluation
            locals_dict = {'data': data}
            exec(f'result = {rule_expression}', self.safe_globals, locals_dict)
            self.rules[rule_name] = rule_expression
            return locals_dict.get('result')
        except Exception as e:
            return {'error': str(e)}