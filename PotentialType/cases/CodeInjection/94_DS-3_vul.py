    def post(self):
        template_name = self.get_body_argument("name")
        template_content = self.get_body_argument("content")
        
        def vulnerable_render(content):
            # Vulnerable code injection through direct execution
            locals_dict = {}
            globals_dict = {'__builtins__': None}
            try:
                exec(f"result = f'''{content}'''", globals_dict, locals_dict)
                return locals_dict.get('result', '')
            except Exception as e:
                return str(e)
        
        rendered = vulnerable_render(template_content)
        self.write(f'''
        <h2>Rendered Template: {template_name}</h2>
        <div style="border:1px solid #ccc; padding:10px;">
            {rendered}
        </div>
        <a href="/">Back</a>
        ''')