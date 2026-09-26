from django.urls import path
from .views import WorkspaceListCreateView, WorkspaceMemberListView, WorkspaceMemberAddView, WorkspaceMemberDeleteView, \
    WorkspaceRetrieveUpdateDestroyView

urlpatterns = [
    path("", WorkspaceListCreateView.as_view(), name="workspace-list-create"),
    path("<int:id>/",WorkspaceRetrieveUpdateDestroyView.as_view(),name="workspace-detail",),
    path("<int:workspace_id>/members/",WorkspaceMemberListView.as_view(),name="workspace-members",),
    path("<int:workspace_id>/members/add/",WorkspaceMemberAddView.as_view(),name="workspace-add-members",),
    path("<int:workspace_id>/members/delete/<int:user_id>/",WorkspaceMemberDeleteView.as_view(),name="workspace-delete-members",),
]