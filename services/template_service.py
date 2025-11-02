class TemplateManager:
    def __init__(self):
        self.templates = {}

    def get_template(self, main_disease, sheet_name):
        return self.templates.get((main_disease, sheet_name))
