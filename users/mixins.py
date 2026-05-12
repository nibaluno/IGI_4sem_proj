from django.contrib.auth.mixins import UserPassesTestMixin

class BuyerRequiredMixin(UserPassesTestMixin):
    """Пускает только авторизованных ПОКУПАТЕЛЕЙ"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'buyer'

class EmployeeRequiredMixin(UserPassesTestMixin):
    """Пускает только авторизованных СОТРУДНИКОВ"""
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'employee'

