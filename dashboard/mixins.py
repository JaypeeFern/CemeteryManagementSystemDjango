import sweetify
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin


staff_required = user_passes_test(lambda user: user.is_staff, login_url='Home')
superuser_required = user_passes_test(lambda user: user.is_superuser, login_url='Home')


class StaffRequiredMixin(UserPassesTestMixin):
    login_url = 'Home'

    def test_func(self):
        return self.request.user.is_staff


class SuperuserRequiredMixin(UserPassesTestMixin):
    login_url = 'Home'

    def test_func(self):
        return self.request.user.is_superuser

class SweetifyMixin(object):
    """
    Adds a sweetalert success message on successful form submission.
    Drop-in replacement for django's SuccessMessageMixin.
    """

    success_message = ""
    sweetify_options = {}

    def form_valid(self, form):
        response = super(SweetifyMixin, self).form_valid(form)
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            sweetify.toast(self.request, success_message, **self.get_sweetify_options())
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data

    def get_sweetify_options(self):
        return self.sweetify_options
