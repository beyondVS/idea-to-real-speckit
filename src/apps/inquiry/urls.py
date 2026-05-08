from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("api/inquiry/start/", views.start_session_api, name="start_session"),
    path("api/inquiry/<uuid:session_id>/chat/", views.chat_api, name="chat_api"),
    path(
        "api/inquiry/<uuid:session_id>/history/",
        views.get_history_api,
        name="get_history",
    ),
    path(
        "api/inquiry/<uuid:session_id>/rollback/", views.rollback_api, name="rollback"
    ),
    path(
        "api/inquiry/<uuid:session_id>/confirm/",
        views.confirm_completion_api,
        name="confirm_completion",
    ),
    path(
        "api/inquiry/<uuid:session_id>/rate/",
        views.rate_session_api,
        name="rate_session",
    ),
]
