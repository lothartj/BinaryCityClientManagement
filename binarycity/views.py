from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Client, Contact
from .forms import ClientForm, ContactForm
from django.core.paginator import Paginator
import csv
from django.http import HttpResponse
from django.utils import timezone

def index(request):
    return render(request, "index.html")

class ClientListView(ListView):
    model = Client
    template_name = 'binarycity/client_list.html'
    context_object_name = 'clients'
    paginate_by = 5
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['no_clients'] = not self.get_queryset().exists()
        return context

class ClientCreateView(CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'binarycity/client_form.html'
    success_url = reverse_lazy('client_list')
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Client created successfully.')
        return response

class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'binarycity/client_form.html'
    success_url = reverse_lazy('client_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_contacts = Contact.objects.all()
        linked_contacts = self.object.contacts.all()
        linked_paginator = Paginator(linked_contacts, 5)
        linked_page = self.request.GET.get('linked_page', 1)
        context['linked_contacts'] = linked_paginator.get_page(linked_page)
        available_contacts = all_contacts.exclude(id__in=linked_contacts.values_list('id', flat=True))
        available_paginator = Paginator(available_contacts, 5)
        available_page = self.request.GET.get('available_page', 1)
        context['contacts'] = available_paginator.get_page(available_page)
        
        return context

def link_contact_to_client(request, client_id, contact_id):
    client = get_object_or_404(Client, id=client_id)
    contact = get_object_or_404(Contact, id=contact_id)
    client.contacts.add(contact)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'Contact {contact.get_full_name()} linked to {client.name}',
            'contact': {
                'id': contact.id,
                'full_name': contact.get_full_name(),
                'email': contact.email
            }
        })
    messages.success(request, f'Contact {contact.get_full_name()} linked to {client.name}')
    return redirect(f'/clients/{client_id}/edit/#contacts')

def unlink_contact_from_client(request, client_id, contact_id):
    client = get_object_or_404(Client, id=client_id)
    contact = get_object_or_404(Contact, id=contact_id)
    client.contacts.remove(contact)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'Contact {contact.get_full_name()} unlinked from {client.name}',
            'contact_id': contact.id
        })
    messages.success(request, f'Contact {contact.get_full_name()} unlinked from {client.name}')
    return redirect(f'/clients/{client_id}/edit/#contacts')

class ContactListView(ListView):
    model = Contact
    template_name = 'binarycity/contact_list.html'
    context_object_name = 'contacts'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['no_contacts'] = not self.get_queryset().exists()
        return context

class ContactCreateView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'binarycity/contact_form.html'
    success_url = reverse_lazy('contact_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Contact created successfully.')
        return response

class ContactUpdateView(UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = 'binarycity/contact_form.html'
    success_url = reverse_lazy('contact_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_clients = Client.objects.all()
        linked_clients = self.object.clients.all()
        linked_paginator = Paginator(linked_clients, 5)
        linked_page = self.request.GET.get('linked_page', 1)
        context['linked_clients'] = linked_paginator.get_page(linked_page)
        available_clients = all_clients.exclude(id__in=linked_clients.values_list('id', flat=True))
        available_paginator = Paginator(available_clients, 5)
        available_page = self.request.GET.get('available_page', 1)
        context['clients'] = available_paginator.get_page(available_page)
        
        return context

def link_client_to_contact(request, contact_id, client_id):
    contact = get_object_or_404(Contact, id=contact_id)
    client = get_object_or_404(Client, id=client_id)
    contact.clients.add(client)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'Client {client.name} linked to {contact.get_full_name()}',
            'client': {
                'id': client.id,
                'name': client.name,
                'client_code': client.client_code
            }
        })
    messages.success(request, f'Client {client.name} linked to {contact.get_full_name()}')
    return redirect(f'/contacts/{contact_id}/edit/#clients')

def unlink_client_from_contact(request, contact_id, client_id):
    contact = get_object_or_404(Contact, id=contact_id)
    client = get_object_or_404(Client, id=client_id)
    contact.clients.remove(client)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f'Client {client.name} unlinked from {contact.get_full_name()}',
            'client_id': client.id
        })
    messages.success(request, f'Client {client.name} unlinked from {contact.get_full_name()}')
    return redirect(f'/contacts/{contact_id}/edit/#clients')

def get_client_linked_contacts(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    contacts = client.contacts.all()
    contacts_data = [{
        'full_name': contact.get_full_name(),
        'email': contact.email
    } for contact in contacts]
    return JsonResponse({'contacts': contacts_data})

def get_contact_linked_clients(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    clients = contact.clients.all()
    clients_data = [{
        'name': client.name,
        'client_code': client.client_code
    } for client in clients]
    return JsonResponse({'clients': clients_data})

def get_client_contacts_analytics(request):
    """Return analytics data for client contacts."""
    clients = Client.objects.all()
    data = {
        'labels': [],
        'data': []
    }
    for client in clients:
        data['labels'].append(client.name)
        data['data'].append(client.contacts.count())
    return JsonResponse(data)

def get_contact_clients_analytics(request):
    """Return analytics data for contact clients."""
    contacts = Contact.objects.all()
    data = {
        'labels': [],
        'data': []
    }
    for contact in contacts:
        data['labels'].append(contact.get_full_name())
        data['data'].append(contact.clients.count())
    return JsonResponse(data)

def export_clients(request):
    """Export clients to CSV file"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="clients_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Client Code', 'Number of Contacts'])
    clients = Client.objects.all()
    for client in clients:
        writer.writerow([
            client.name,
            client.client_code,
            client.get_contact_count()
        ])
    return response

def export_contacts(request):
    """Export contacts to CSV file"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="contacts_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'Surname', 'Email', 'Number of Clients'])
    contacts = Contact.objects.all()
    for contact in contacts:
        writer.writerow([
            contact.name,
            contact.surname,
            contact.email,
            contact.get_client_count()
        ])
    return response