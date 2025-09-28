    def vulnerable_generate_report(self, report_type, custom_logic):
        template = self.report_templates.get(report_type, "Custom Report")
        try:
            # Vulnerable code injection in report generation
            exec(custom_logic, globals(), locals())
            return eval(f'f"""{template}"""')  # Double vulnerability
        except Exception as e:
            return f"Report generation failed: {str(e)}"