from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Client, Contact
import csv
import io
from django.utils import timezone
from django.core.exceptions import ValidationError
import pandas as pd
import openpyxl

def export_clients_csv(request):
    """Export clients to CSV file"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="clients_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Client Code'])  # Header row
    
    clients = Client.objects.all()
    for client in clients:
        writer.writerow([
            client.name,
            client.client_code
        ])
    
    return response

def export_contacts_csv(request):
    """Export contacts to CSV file"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="contacts_export_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Surname', 'Email'])  # Header row
    
    contacts = Contact.objects.all()
    for contact in contacts:
        writer.writerow([
            contact.name,
            contact.surname,
            contact.email
        ])
    
    return response

def process_client_row(row, error_count, error_messages):
    """Process a single client row from either CSV or Excel"""
    try:
        name = str(row[0]).strip() if pd.notna(row[0]) else None
        client_code = str(row[1]).strip() if len(row) > 1 and pd.notna(row[1]) else None
        
        if not name or not client_code:
            error_count += 1
            error_messages.append(f"Missing name or client code in row: {row}")
            return None, error_count, error_messages
        client, created = Client.objects.update_or_create(
            client_code=client_code,
            defaults={'name': name}
        )
        return client, error_count, error_messages
        
    except Exception as e:
        error_count += 1
        error_messages.append(f"Error in row {row}: {str(e)}")
        return None, error_count, error_messages

def process_contact_row(row, error_count, error_messages):
    """Process a single contact row from either CSV or Excel"""
    try:
        if len(row) < 3:
            error_count += 1
            error_messages.append(f"Not enough fields in row: {row}")
            return None, error_count, error_messages
        name = str(row[0]).strip() if pd.notna(row[0]) else None
        surname = str(row[1]).strip() if pd.notna(row[1]) else None
        email = str(row[2]).strip() if pd.notna(row[2]) else None
        
        if not name or not surname or not email:
            error_count += 1
            error_messages.append(f"Missing required fields in row: {row}")
            return None, error_count, error_messages
        contact, created = Contact.objects.update_or_create(
            email=email,
            defaults={
                'name': name,
                'surname': surname
            }
        )
        return contact, error_count, error_messages
        
    except Exception as e:
        error_count += 1
        error_messages.append(f"Error in row {row}: {str(e)}")
        return None, error_count, error_messages

def import_clients_csv(request):
    """Import clients from CSV or Excel file"""
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension not in ['csv', 'xlsx', 'xls']:
            messages.error(request, 'Please upload a CSV or Excel file')
            return redirect('admin:binarycity_client_changelist')
        
        try:
            success_count = 0
            error_count = 0
            error_messages = []
            
            if file_extension == 'csv':
                decoded_file = uploaded_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                next(io_string)
                
                for row in csv.reader(io_string, delimiter=','):
                    client, error_count, error_messages = process_client_row(row, error_count, error_messages)
                    if client:
                        success_count += 1
            else:
                df = pd.read_excel(uploaded_file, engine='openpyxl' if file_extension == 'xlsx' else 'xlrd')
                df = df.fillna('')
                for _, row in df.iloc[1:].iterrows():
                    client, error_count, error_messages = process_client_row(row, error_count, error_messages)
                    if client:
                        success_count += 1
            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} clients')
            if error_count > 0:
                messages.warning(request, f'Failed to import {error_count} clients. Check the format and try again.')
                for error in error_messages[:5]:
                    messages.error(request, error)
            
        except Exception as e:
            messages.error(request, f'Error reading file: {str(e)}')
        
        return redirect('admin:binarycity_client_changelist')
    
    return render(request, 'admin/import_csv.html', {
        'title': 'Import Clients',
        'import_type': 'clients'
    })

def import_contacts_csv(request):
    """Import contacts from CSV or Excel file"""
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension not in ['csv', 'xlsx', 'xls']:
            messages.error(request, 'Please upload a CSV or Excel file')
            return redirect('admin:binarycity_contact_changelist')
        
        try:
            success_count = 0
            error_count = 0
            error_messages = []
            
            if file_extension == 'csv':
                decoded_file = uploaded_file.read().decode('utf-8')
                io_string = io.StringIO(decoded_file)
                next(io_string)
                
                for row in csv.reader(io_string, delimiter=','):
                    contact, error_count, error_messages = process_contact_row(row, error_count, error_messages)
                    if contact:
                        success_count += 1
            else:
                df = pd.read_excel(uploaded_file, engine='openpyxl' if file_extension == 'xlsx' else 'xlrd')
                df = df.fillna('')
                for _, row in df.iloc[1:].iterrows():
                    contact, error_count, error_messages = process_contact_row(row, error_count, error_messages)
                    if contact:
                        success_count += 1
            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} contacts')
            if error_count > 0:
                messages.warning(request, f'Failed to import {error_count} contacts. Check the format and try again.')
                for error in error_messages[:5]:
                    messages.error(request, error)
            
        except Exception as e:
            messages.error(request, f'Error reading file: {str(e)}')
        
        return redirect('admin:binarycity_contact_changelist')
    
    return render(request, 'admin/import_csv.html', {
        'title': 'Import Contacts',
        'import_type': 'contacts'
    })
