import datetime
import urllib

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import FormView, UpdateView, DeleteView
from django_datatables_view.base_datatable_view import BaseDatatableView
from djqscsv import render_to_csv_response

from .filters import CertificateFilter
from .forms import (CertificateRegisterForm, KpcAddressForm,
                    LicenseeCertificateForm, StatusUpdateForm, VoidForm)
from .models import Certificate, Licensee, KpcAddress
from .utils import CertificatePreview, _to_mdy, apply_certificate_search

User = get_user_model()


class ExportView(LoginRequiredMixin, View):

    columns = ["number", "aes", "licensee__name", "status",
               "last_modified", "date_of_sale", "date_of_issue", "date_of_expiry", "date_of_shipment", "date_of_delivery", "date_voided",
               "country_of_origin", "shipped_value", "number_of_parcels", "carat_weight", "harmonized_code__value",
               "exporter", "exporter_address",
               "consignee", "consignee_address",
               "port_of_export__name",
               "notes"]

    def get(self, request):
        """Return CSV of filtered certificates"""
        qs = apply_certificate_search(
            request, request.user.profile.certificates())
        qs = qs.values(*self.columns)

        export_kwargs = {'field_serializer_map': {
            'number': (lambda number: 'US' + str(number)),
            'status': Certificate.get_label_for_status,
            'last_modified': (lambda dt: dt.strftime("%m/%d/%Y %X %Z")),
            'date_of_issue': _to_mdy,
            'date_of_sale': _to_mdy,
            'date_of_expiry': _to_mdy,
            'date_of_shipment': _to_mdy,
            'date_of_delivery': _to_mdy,
            'date_voided': _to_mdy,
            'country_of_origin': (lambda countries: Certificate(country_of_origin=countries).get_country_of_origin_display)
        }}
        return render_to_csv_response(qs, **export_kwargs)


@permission_required('accounts.can_get_licensee_contacts', raise_exception=True)
def licensee_contacts(request):
    """Return users associated with the provided licensee"""
    if request.method == 'GET':
        licensee_id = request.GET.get('licensee')
        contacts = User.objects.filter(is_active=True,
                                       profile__licensees=licensee_id) if licensee_id else []
        if contacts:
            contacts_json = [
                {'id': user.id, 'name': user.profile.get_user_display_name()} for user in contacts]
        else:
            contacts_json = []
    else:
        return HttpResponse(status=405)
    return JsonResponse(contacts_json, safe=False)


class LicenseeDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Licensee
    template_name = 'licensee.html'

    def test_func(self):
        return self.get_object().user_can_access(self.request.user)


class CertificateRegisterView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['price'] = Certificate.get_price()
        return context

    def test_func(self):
        """only for superusers"""
        if not self.request.user.is_superuser:
            raise PermissionDenied
        return True

    template_name = 'certificate/register.html'
    form_class = CertificateRegisterForm
    success_url = reverse_lazy('cert-register')

    def form_valid(self, form):
        """Generate requested Certificates"""
        cert_kwargs = {'assignor': self.request.user, 'licensee': form.cleaned_data['licensee'],
                       'date_of_sale': form.cleaned_data['date_of_sale'],
                       'last_modified': datetime.datetime.now()}
        certs = form.get_cert_list()
        if certs:
            Certificate.objects.bulk_create(Certificate(
                number=i, **cert_kwargs) for i in certs)
        messages.success(
            self.request, f'Generated {len(certs)} new certificates.')
        return super().form_valid(form)


class CertificateListView(LoginRequiredMixin, TemplateView):
    template_name = 'certificate/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = CertificateFilter(
            self.request.GET, request=self.request, queryset=self.request.user.profile.certificates())
        context['statuses'] = {status[0]: status[1]
                               for status in Certificate.STATUS_CHOICES}
        context['dt_columns'] = CertificateJson.columns
        return context


class CertificateJson(LoginRequiredMixin, BaseDatatableView):
    model = Certificate
    columns = ["number", "status", "last_modified", "licensee__name",
               "aes", "consignee", "shipped_value",
               "date_of_issue", "date_of_sale",
               "date_of_expiry", "number_of_parcels", "carat_weight",
               "harmonized_code__value", "exporter", "date_of_shipment",
               "date_of_delivery", "date_voided", "port_of_export__name"]
    order_columns = columns

    max_display_length = 500

    def get_initial_queryset(self):
        """Limit to certificates visible to user"""
        return self.request.user.profile.certificates()

    def filter_queryset(self, qs):
        return apply_certificate_search(self.request, qs)

    def prepare_results(self, qs):
        qs = qs.values(*self.columns)
        return list(qs)


class BaseCertificateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Certificate
    slug_field = 'number'
    slug_url_kwarg = 'number'


class CertificateView(BaseCertificateView):
    REVIEW_MSG = "Please review the certificate data below."

    def test_func(self):
        obj = self.get_object()
        if not obj.user_can_access(self.request.user):
            raise PermissionDenied
        return True

    def dispatch(self, request, *args, **kwargs):
        """Disallow POST if user cannot edit a certificate"""
        if request.method == 'POST':
            cert = self.get_object()
            if not cert.user_can_edit(self.request.user):
                raise PermissionDenied()
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['editable'] = self.object.user_can_edit(self.request.user)
        return kwargs

    def get_form_class(self):
        if self.object.licensee_editable:
            return LicenseeCertificateForm
        return StatusUpdateForm

    def get_form(self):
        """
        Check for incoming GET params
        If present, populate form with values
        """
        kwargs = self.get_form_kwargs()
        form = super().get_form()
        if self.request.GET and isinstance(form, LicenseeCertificateForm):
            messages.info(self.request, self.REVIEW_MSG)
            return LicenseeCertificateForm(self.request.GET, **kwargs)
        return form

    def get_template_names(self):
        if self.object.licensee_editable:
            return ['certificate/details-edit.html']
        return ['certificate/details.html']

    def form_valid(self, form):
        """Render confirmation page if certificate submitted"""
        if isinstance(form, LicenseeCertificateForm):
            cert = form.save(commit=False)
            context = self.get_context_data()
            context['b64_pdf'] = CertificatePreview(cert).make_preview()
            return TemplateResponse(self.request, 'certificate/preview.html', context=context)
        else:
            response = super().form_valid(form)
            messages.success(self.request, form.SUCCESS_MSG)
            return response


class CertificateVoidView(BaseCertificateView):
    form_class = VoidForm
    template_name = 'certificate/void.html'

    ALREADY_VOID = "This certificate has already been voided."

    def test_func(self):
        obj = self.get_object()
        if not obj.user_can_edit(self.request.user):
            raise PermissionDenied
        return True

    def dispatch(self, request, *args, **kwargs):
        """Unexpected access if certificate is already voided"""
        obj = self.get_object()
        if obj.void:
            messages.warning(self.request, self.ALREADY_VOID)
            return redirect(obj.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, form.SUCCESS_MSG)
        return response


class CertificateConfirmView(BaseCertificateView):
    form_class = LicenseeCertificateForm

    def test_func(self):
        obj = self.get_object()
        if not obj.user_can_edit(self.request.user):
            raise PermissionDenied
        return True

    def form_invalid(self, form):
        """
        Unexpectedly modified form data on confirmation page
        Redirect to edit page w/ errors
        """
        form_data = urllib.parse.urlencode(self.request.POST)
        return redirect(self.object.get_absolute_url() + '?' + form_data)

    def form_valid(self, form):
        form.save()
        messages.success(self.request, form.SUCCESS_MSG)
        return redirect(form.instance.get_absolute_url())


class BaseAddressView(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        """
           Auditors cannot modify address book
           Licensee contacts may
        """
        if self.request.user.profile.is_auditor:
            raise PermissionDenied

        obj = self.get_object()
        if isinstance(obj, Licensee):
            accessible = obj.user_can_access(self.request.user)
        elif isinstance(obj, KpcAddress):
            accessible = obj.licensee.user_can_access(self.request.user)
        if not accessible:
            PermissionDenied
        return accessible


class KpcAddressCreate(BaseAddressView, FormView):
    form_class = KpcAddressForm
    template_name = 'kpc_address/create.html'

    def get_object(self):
        return get_object_or_404(Licensee, id=self.kwargs['pk'])

    def get_success_url(self):
        return self.get_object().get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['licensee'] = self.get_object()
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        kpc_address = form.save(commit=False)
        kpc_address.licensee = self.get_object()
        kpc_address.save()

        message = f'Successfully added "{form.instance.name}" to the address book.'
        messages.success(self.request, message)
        return response


class KpcAddressUpdate(BaseAddressView, UpdateView):
    model = KpcAddress
    form_class = KpcAddressForm
    template_name = 'kpc_address/update.html'

    def get_success_url(self):
        return self.object.licensee.get_absolute_url()

    def form_valid(self, form):
        response = super().form_valid(form)
        message = f'Successfully updated "{form.instance.name}".'
        messages.success(self.request, message)
        return response


class KpcAddressDelete(BaseAddressView, DeleteView):
    model = KpcAddress
    template_name = 'kpc_address/delete.html'

    def get_success_url(self):
        return self.object.licensee.get_absolute_url()

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        message = f'Successfully deleted "{self.object.name}" from the address book.'
        messages.success(self.request, message)
        return response
