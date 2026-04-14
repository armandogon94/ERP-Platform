from rest_framework.routers import DefaultRouter

from modules.hr.viewsets import (
    DepartmentViewSet,
    EmployeeViewSet,
    LeaveRequestViewSet,
    PayrollViewSet,
)

router = DefaultRouter()
router.register("departments", DepartmentViewSet, basename="department")
router.register("employees", EmployeeViewSet, basename="employee")
router.register("leave-requests", LeaveRequestViewSet, basename="leave-request")
router.register("payrolls", PayrollViewSet, basename="payroll")

urlpatterns = router.urls
