from django.urls import path
from .views import CalendlyAuthView, CalendlyCallbackView, CalendlyEventsView, CalendlyUserView

urlpatterns = [
    path('calendly/auth/', CalendlyAuthView.as_view(), name='calendly_auth'),
    path('auth/calendly/callback/', CalendlyCallbackView.as_view(), name='calendly_callback'),
    path('calendly/events/', CalendlyEventsView.as_view(), name='calendly_events'),
    path('calendly/user/', CalendlyUserView.as_view(), name='calendly_user'),
]