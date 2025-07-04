from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from .models import Client, Contact
from .forms import ClientForm, ContactForm

def index(request):
    return render(request, "index.html")

class ClientListView(ListView):
    model = Client
    template_name = 'binarycity/client_list.html'
    context_object_name = 'clients'

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
        context['contacts'] = Contact.objects.all()
        context['linked_contacts'] = self.object.contacts.all()
        return context

def link_contact_to_client(request, client_id, contact_id):
    client = get_object_or_404(Client, id=client_id)
    contact = get_object_or_404(Contact, id=contact_id)
    client.contacts.add(contact)
    messages.success(request, f'Contact {contact.get_full_name()} linked to {client.name}')
    return redirect('client_update', pk=client_id)

def unlink_contact_from_client(request, client_id, contact_id):
    client = get_object_or_404(Client, id=client_id)
    contact = get_object_or_404(Contact, id=contact_id)
    client.contacts.remove(contact)
    messages.success(request, f'Contact {contact.get_full_name()} unlinked from {client.name}')
    return redirect('client_update', pk=client_id)

class ContactListView(ListView):
    model = Contact
    template_name = 'binarycity/contact_list.html'
    context_object_name = 'contacts'

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
        context['clients'] = Client.objects.all()
        context['linked_clients'] = self.object.clients.all()
        return context

def link_client_to_contact(request, contact_id, client_id):
    contact = get_object_or_404(Contact, id=contact_id)
    client = get_object_or_404(Client, id=client_id)
    contact.clients.add(client)
    messages.success(request, f'Client {client.name} linked to {contact.get_full_name()}')
    return redirect('contact_update', pk=contact_id)

def unlink_client_from_contact(request, contact_id, client_id):
    contact = get_object_or_404(Contact, id=contact_id)
    client = get_object_or_404(Client, id=client_id)
    contact.clients.remove(client)
    messages.success(request, f'Client {client.name} unlinked from {contact.get_full_name()}')
    return redirect('contact_update', pk=contact_id)