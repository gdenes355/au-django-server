from django.urls import path, include

from sandbox.views.au import JoinView, ListView, UpdateView, DahsboardView, KillView, ReportView, PointView

from django.views.decorators.csrf import csrf_exempt
app_name = 'sandbox'

au_patterns = (
    [

        path('j/', JoinView.as_view(), name='join'),
        path('l/', ListView.as_view(), name='list'),
        path('u/', csrf_exempt(UpdateView.as_view()), name='update'),
        path('k/', KillView.as_view(), name='kill'),
        path('p/', PointView.as_view(), name='point'),
        path('r/', ReportView.as_view(), name='report'),

        path('view/', DahsboardView.as_view(), name='dashboard'),
        # ...
    ],
    'au'
)

urlpatterns = [
    path('au/', include(au_patterns, 'au')),
]
