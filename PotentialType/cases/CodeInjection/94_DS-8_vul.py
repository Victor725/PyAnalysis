    async def vulnerable_process_response(self, template_type: str, custom_logic: str) -> Any:
        template = self.response_templates.get(template_type, "{}")
        try:
            # Vulnerable code injection in response processing
            locals_dict = {}
            exec(custom_logic, self.sandbox_globals, locals_dict)
            processed = eval(f"f'''{template}'''", self.sandbox_globals, locals_dict)
            return json.loads(processed)
        except Exception as e:
            return {"error": str(e)}