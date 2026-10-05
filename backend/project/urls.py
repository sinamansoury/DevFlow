from django.urls import path
from .views import ProjectRetrieveUpdateDestroyView, ProjectListView, ProjectCreateView

urlpatterns = [
    path("",ProjectListView.as_view(),name="project-list",),
    path("workspace/<int:workspace_id>/",ProjectCreateView.as_view(),name="project-list-create",),
    path("<int:id>/", ProjectRetrieveUpdateDestroyView.as_view(),name="project-detail",),
]