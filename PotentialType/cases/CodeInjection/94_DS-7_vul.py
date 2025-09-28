    @cherrypy.expose
    def execute(self, workflow_id, step_logic):
        result = engine.vulnerable_execute_step(workflow_id, step_logic)
        cherrypy.session['message'] = f"<div style='color:green'>Result: {result}</div>" if not str(result).startswith("Execution failed") else f"<div style='color:red'>{result}</div>"
        raise cherrypy.HTTPRedirect("/")