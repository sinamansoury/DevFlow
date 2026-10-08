from django.urls import path
from .views import TaskListView, TaskRetrieveUpdateDestroyView, TaskCreateView

urlpatterns = [
    path("",TaskListView.as_view(),name="task-list",),
    path("projects/<int:project_id>/",TaskCreateView.as_view(),name="task-create",),
    path("<int:id>/",TaskRetrieveUpdateDestroyView.as_view(),name="task-detail",),
]