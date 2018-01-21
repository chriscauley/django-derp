from django.contrib import admin

from models import Test, TestRun

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    pass

@admin.register(TestRun)
class TestRunAdmin(admin.ModelAdmin):
    pass