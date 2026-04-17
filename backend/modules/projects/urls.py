from django.urls import include, path
from rest_framework.routers import DefaultRouter

from modules.projects.viewsets import (
    MilestoneViewSet,
    ProjectTimesheetViewSet,
    ProjectViewSet,
    TaskViewSet,
)

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")
router.register("tasks", TaskViewSet, basename="task")
router.register("milestones", MilestoneViewSet, basename="milestone")
router.register("timesheets", ProjectTimesheetViewSet, basename="project-timesheet")

urlpatterns = [path("", include(router.urls))]
