from django.conf.urls import url

import derp.views

urlpatterns = [
    url('^$',derp.views.result),
    url('^results.json$',derp.views.result_json),
    url('^groups.json$',derp.views.groups_json),
]