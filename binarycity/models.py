from django.db import models
from django.core.validators import EmailValidator
import string
import random

class Client(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    client_code = models.CharField(max_length=6, unique=True, blank=True, db_index=True)
    contacts = models.ManyToManyField('Contact', related_name='clients', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'client_code']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.client_code:
            self.client_code = self.generate_client_code()
        super().save(*args, **kwargs)
    def generate_client_code(self):
        words = self.name.upper().split()
        if len(words) >= 3:
            name_part = ''.join(word[0] for word in words[:3])
        else:
            name_part = ''.join(word[0] for word in words)
            if len(name_part) < 3:
                if len(name_part) == 1:
                    base = name_part
                    second_letter = 'A'
                    third_letter = 'A'
                    while True:
                        counter = 1
                        while counter <= 999:
                            candidate_code = f"{base}{second_letter}{third_letter}{counter:03d}"
                            if not Client.objects.filter(client_code=candidate_code).exists():
                                return candidate_code
                            counter += 1
                        if third_letter == 'Z':
                            if second_letter == 'Z':
                                raise ValueError("No available client codes")
                            second_letter = chr(ord(second_letter) + 1)
                            third_letter = 'A'
                        else:
                            third_letter = chr(ord(third_letter) + 1)
                elif len(name_part) == 2:
                    base = name_part
                    padding_letter = 'A'
                    while True:
                        counter = 1
                        while counter <= 999:
                            candidate_code = f"{base}{padding_letter}{counter:03d}"
                            if not Client.objects.filter(client_code=candidate_code).exists():
                                return candidate_code
                            counter += 1
                        if padding_letter == 'Z':
                            raise ValueError("No available client codes")
                        padding_letter = chr(ord(padding_letter) + 1)

        base_code = name_part[:3]
        counter = 1
        while True:
            candidate_code = f"{base_code}{counter:03d}"
            if not Client.objects.filter(client_code=candidate_code).exists():
                return candidate_code
            counter += 1
    def get_contact_count(self):
        return self.contacts.count()

class Contact(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    surname = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(unique=True, validators=[EmailValidator()], db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name', 'surname']
        indexes = [
            models.Index(fields=['name', 'surname']),
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def get_full_name(self):
        return f"{self.name} {self.surname}"

    def get_client_count(self):
        return self.clients.count()

class NotificationClient(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    phone_number = models.CharField(max_length=20, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['phone_number']),
        ]

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

    def get_formatted_phone(self):
        """Format phone number for WhatsApp"""
        if not self.phone_number:
            return None
        clean_number = self.phone_number.replace('+', '').replace(' ', '').replace('-', '')
        if not clean_number.startswith('264'):
            clean_number = '264' + clean_number
        return clean_number
