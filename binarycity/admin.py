from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from .models import Client, Contact, NotificationClient
from . import viewsexportimport

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_code', 'get_contact_count', 'action_buttons')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'client_code')
    readonly_fields = ('client_code', 'created_at', 'updated_at')
    ordering = ('name',)
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'client_code')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    def get_readonly_fields(self, request, obj=None):
        if obj:  
            return self.readonly_fields
        return ('created_at', 'updated_at')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(viewsexportimport.import_clients_csv), name='import_clients_csv'),
            path('export-csv/', self.admin_site.admin_view(viewsexportimport.export_clients_csv), name='export_clients_csv'),
        ]
        return custom_urls + urls

    def action_buttons(self, obj):
        return format_html(
            '<a class="button" href="{}">Export All</a>&nbsp;'
            '<a class="button" href="{}">Import CSV</a>',
            '/admin/binarycity/client/export-csv/',
            '/admin/binarycity/client/import-csv/'
        )
    action_buttons.short_description = 'Actions'
    action_buttons.allow_tags = True

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('surname', 'name', 'email', 'get_client_count', 'action_buttons')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'surname', 'email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('surname', 'name')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'surname', 'email')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        try:
            if ' ' in search_term:
                first, last = search_term.rsplit(' ', 1)
                queryset |= self.model.objects.filter(name__icontains=first, surname__icontains=last)
        except:
            pass
        return queryset, use_distinct

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(viewsexportimport.import_contacts_csv), name='import_contacts_csv'),
            path('export-csv/', self.admin_site.admin_view(viewsexportimport.export_contacts_csv), name='export_contacts_csv'),
        ]
        return custom_urls + urls

    def action_buttons(self, obj):
        return format_html(
            '<a class="button" href="{}">Export All</a>&nbsp;'
            '<a class="button" href="{}">Import CSV</a>',
            '/admin/binarycity/contact/export-csv/',
            '/admin/binarycity/contact/import-csv/'
        )
    action_buttons.short_description = 'Actions'
    action_buttons.allow_tags = True

@admin.register(NotificationClient)
class NotificationClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'phone_number')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    date_hierarchy = 'created_at'
    list_editable = ('is_active',)
    fieldsets = (
        ('Client Information', {
            'fields': ('name', 'phone_number', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        clean_term = search_term.replace('+', '').replace(' ', '').replace('-', '')
        if clean_term != search_term:
            queryset |= self.model.objects.filter(phone_number__icontains=clean_term)
        return queryset, use_distinct
