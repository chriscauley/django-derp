class DatabaseRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "derp":
            return "derp"

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "derp":
            return "derp"
        
    def allow_migrate(self, db, model):
        if db == 'derp': 
            return model._meta.app_label in ['derp', 'django']
