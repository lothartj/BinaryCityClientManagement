from django.test import TestCase, Client as TestClient
from django.urls import reverse
from .models import Client, Contact
from .forms import ClientForm, ContactForm

class ClientModelTests(TestCase):
    def test_client_code_generation(self):
        client = Client.objects.create(name="Protea Hotel")
        self.assertEqual(len(client.client_code), 6)
        self.assertEqual(client.client_code[:3], "PRO")
        client = Client.objects.create(name="IT")
        self.assertEqual(len(client.client_code), 6)
        self.assertTrue(client.client_code[:3].startswith("IT"))

    def test_unique_client_code(self):
        client1 = Client.objects.create(name="Test")
        client2 = Client.objects.create(name="Test")
        self.assertNotEqual(client1.client_code, client2.client_code)
        self.assertEqual(client1.client_code[:3], client2.client_code[:3])

    def test_contact_count(self):
        client = Client.objects.create(name="Test Client")
        contact1 = Contact.objects.create(name="John", surname="Doe", email="john@test.com")
        contact2 = Contact.objects.create(name="Jane", surname="Doe", email="jane@test.com")
        
        self.assertEqual(client.get_contact_count(), 0)
        client.contacts.add(contact1, contact2)
        self.assertEqual(client.get_contact_count(), 2)

class ContactModelTests(TestCase):
    def test_email_validation(self):
        contact = Contact.objects.create(
            name="John",
            surname="Doe",
            email="john@example.com"
        )
        self.assertEqual(contact.email, "john@example.com")
        with self.assertRaises(Exception):
            Contact.objects.create(
                name="Jane",
                surname="Doe",
                email="john@example.com"
            )

    def test_full_name_format(self):
        contact = Contact.objects.create(
            name="John",
            surname="Doe",
            email="john@example.com"
        )
        self.assertEqual(contact.get_full_name(), "Doe John")

class ClientFormTests(TestCase):
    def test_valid_data(self):
        form = ClientForm({
            'name': 'Test Client',
        })
        self.assertTrue(form.is_valid())
        client = form.save()
        self.assertEqual(client.name, 'Test Client')

    def test_blank_data(self):
        form = ClientForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'name': ['This field is required.'],
        })

class ContactFormTests(TestCase):
    def test_valid_data(self):
        form = ContactForm({
            'name': 'John',
            'surname': 'Doe',
            'email': 'john@example.com',
        })
        self.assertTrue(form.is_valid())
        contact = form.save()
        self.assertEqual(contact.email, 'john@example.com')

    def test_blank_data(self):
        form = ContactForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(set(form.errors.keys()), set(['name', 'surname', 'email']))

class ViewTests(TestCase):
    def setUp(self):
        self.client = TestClient()
        self.test_client = Client.objects.create(name="Test Client")
        self.test_contact = Contact.objects.create(
            name="John",
            surname="Doe",
            email="john@example.com"
        )

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_client_list_view(self):
        response = self.client.get(reverse('client_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'binarycity/client_list.html')
        self.assertContains(response, "Test Client")

    def test_contact_list_view(self):
        response = self.client.get(reverse('contact_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'binarycity/contact_list.html')
        self.assertContains(response, "john@example.com")

    def test_client_create_view(self):
        response = self.client.post(reverse('client_create'), {
            'name': 'New Client',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Client.objects.filter(name='New Client').exists())

    def test_contact_create_view(self):
        response = self.client.post(reverse('contact_create'), {
            'name': 'Jane',
            'surname': 'Smith',
            'email': 'jane@example.com',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Contact.objects.filter(email='jane@example.com').exists())
