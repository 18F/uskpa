from django.contrib.auth import get_user_model
from django.core import mail
from django.test import RequestFactory, TestCase
from model_mommy import mommy

from accounts.admin import ProfileUserAdmin
from accounts.forms import UserCreationForm

User = get_user_model()


class ProfileAdminTests(TestCase):

    def setUp(self):
        self.form_kwargs = {'username': 'test', 'email': 'test@test.com'}
        self.form = UserCreationForm(self.form_kwargs)
        self.user = self.form.save(commit=False)
        # We don't need to target the real URL here, just making an HttpRequest()
        self.request = RequestFactory().get('/')
        self.request.user = mommy.make(User, is_superuser=True)
        self.site = 'SITE'

    def test_email_on_user_add(self):
        """Send an email to the user on creation of their account when no pw set"""
        ProfileUserAdmin(User, self.site).save_model(self.request, self.user, self.form, False,)
        self.assertEqual(len(mail.outbox), 1)

    def test_email_on_user_add_w_password(self):
        """Send an email to the user on creation of their account when pw set"""
        self.form_kwargs.update({'password1': 'a', 'password2': 'a'})
        form = UserCreationForm(self.form_kwargs)
        self.assertTrue(form.is_valid())
        ProfileUserAdmin(User, self.site).save_model(
            self.request, self.user, form, False,)
        self.assertEqual(len(mail.outbox), 1)

    def test_no_email_on_user_edit(self):
        """No emails generated when `change` is True, we're editing an existing User"""
        ProfileUserAdmin(User, self.site).save_model(self.request, self.user, self.form, True,)
        self.assertEqual(len(mail.outbox), 0)
