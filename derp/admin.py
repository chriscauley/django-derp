from django.contrib import admin

from models import Commit, Test, TestStatus, TestRun, TestGroup

@admin.register(TestGroup)
class TestGroupAdmin(admin.ModelAdmin):
    pass

@admin.register(Commit)
class CommitAdmin(admin.ModelAdmin):
    pass

class TestRunInline(admin.TabularInline):
    extra = 0
    model = TestRun
    readonly_fields = ['commit_id', 'queries', 'milliseconds']

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    inlines = [TestRunInline]
    readonly_fields = ['type', 'parameters', 'parameters_hash', 'created', 'result']
    list_filter = ['testgroup']
    list_editable = ['testgroup']
    list_display = ["__unicode__", "testgroup"]

@admin.register(TestStatus)
class TestStatusAdmin(admin.ModelAdmin):
    pass

@admin.register(TestRun)
class TestRunAdmin(admin.ModelAdmin):
    list_filter = ['commit_id']
    list_display = ['__unicode__','commit_id','milliseconds','queries']