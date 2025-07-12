from django.contrib import admin
from .models import Client, Contact, NotificationClient

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_code', 'get_contact_count', 'created_at')
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

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('surname', 'name', 'email', 'get_client_count', 'created_at')
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
