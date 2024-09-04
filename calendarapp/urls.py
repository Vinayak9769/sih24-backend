from django.urls import path, include
from .views import create_event, update_event, delete_event, get_event_list, upload_ics_view, book_event
urlpatterns = [
    path('create/', create_event),
    path('events/<uuid:event_id>/update', update_event),
    path('events/<uuid:event_id>/delete', delete_event),
    path('get/', get_event_list),
    path('upload-ics/', upload_ics_view, name='upload_ics'),
    path('book-event/', book_event),


]
