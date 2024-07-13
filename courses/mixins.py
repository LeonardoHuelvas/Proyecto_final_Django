from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

class RoleRequiredMixin(UserPassesTestMixin):
    required_role = None

    def test_func(self):
        return self.request.user.role == self.required_role

    def handle_no_permission(self):
        return redirect('404')  # Asegúrate de que '404' es el nombre correcto de tu vista de error 404.
