    def _compile_template(self, template_str, context):
        try:
            # Vulnerable code injection point
            compiled = eval(f'f"""{template_str}"""', {}, context)
            return compiled
        except Exception as e:
            raise ValueError(f"Template compilation error: {str(e)}")