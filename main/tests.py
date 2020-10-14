from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from . import models
from django.utils.text import slugify

class HomepageTests(SimpleTestCase):
    def setUp(self):
        url = reverse('home')
        self.response = self.client.get(url)

    def test_homepage_status_code(self):
        self.assertEqual(self.response.status_code,200)

    def test_homepage_template(self):
        self.assertTemplateUsed(self.response,'index.html')

    def test_homepage_contains_correct_html(self):
        self.assertContains(self.response,'Census Analytics')

    def test_homepage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there! I should not be on the page.')


class ContactpageTests(SimpleTestCase):
    def setUp(self):
        url = reverse('contact')
        self.response = self.client.get(url)
    
    def test_contactpage_status_code(self):
        self.assertEqual(self.response.status_code,200)

    def test_contactpage_template(self):
        self.assertTemplateUsed(self.response,'contact.html')

    def test_contactpage_contains_correct_html(self):
        self.assertContains(self.response,'Support:')

    def test_contactpage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there! I should not be on the page.')


class AboutpageTests(SimpleTestCase):
    def setUp(self):
        url = reverse('about')
        self.response = self.client.get(url)
    
    def test_aboutpage_status_code(self):
        self.assertEqual(self.response.status_code,200)

    def test_aboutpage_template(self):
        self.assertTemplateUsed(self.response,'about.html')

    def test_aboutpage_contains_correct_html(self):
        self.assertContains(self.response,'About Census Analytics')

    def test_aboutpage_does_not_contain_incorrect_html(self):
        self.assertNotContains(self.response, 'Hi there! I should not be on the page.')
    
class DashboardpageTests(TestCase):

    def setUp(self):
        self.user=get_user_model().objects.create_user(
            first_name="Rick",
            last_name="Hiller",
            email="rhiller@gmail.com",
            password="aldrich123",
        )
     
    def test_dashboardpage_status_code(self):
        self.client.login(email="rhiller@gmail.com",password="aldrich123")
        response = self.client.get(reverse('client_dashboard'))
        self.assertEqual(response.status_code,200)

    def test_dashboardpage_template(self):
        self.client.login(email="rhiller@gmail.com",password="aldrich123")
        response = self.client.get(reverse('client_dashboard'))
        self.assertTemplateUsed(response,'client_dashboard.html')

    def test_dashboardpage_contains_correct_html(self):
        self.client.login(email="rhiller@gmail.com",password="aldrich123")
        response = self.client.get(reverse('client_dashboard'))
        self.assertContains(response,'Client #')

    def test_dashboardpage_does_not_contain_incorrect_html(self):
        self.client.login(email="rhiller@gmail.com",password="aldrich123")
        response = self.client.get(reverse('client_dashboard'))
        self.assertNotContains(response, 'Hi there! I should not be on the page.')

class ClientTests(TestCase):

    def setUp(self):
        self.user=get_user_model().objects.create_user(
            id=1,
            first_name="Rick",
            last_name="Hiller",
            email="rhiller@gmail.com",
            password="aldrich123",
        )
        self.user=get_user_model().objects.get(first_name="Rick")
        self.test_client = models.client.objects.create(name="Test Client",number=1.0,slug='test-client')
        self.test_client.users.add(self.user)
        self.test_client.save()

    def test_client_listing(self):
        self.assertEqual(f'{self.test_client.name}','Test Client')
        self.assertEqual(self.test_client.number,1.0)
        self.assertEqual(f'{self.test_client.slug}','test-client')
        self.assertEqual(self.test_client.users.all()[0],self.user)

    def test_client_list_view_for_logged_in_user(self):
        self.client.login(email="rhiller@gmail.com",password="aldrich123")
        response=self.client.get(reverse('client_dashboard'))
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"1.0")
        self.assertTemplateUsed(response,'client_dashboard.html')

    def test_client_list_view_for_logged_out_user(self):
        self.client.logout()
        response = self.client.get(reverse('client_dashboard'))

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'%s?next=/dashboard/' % (reverse('account_login')))
        response = self.client.get('%s?next=/dashboard/' % (reverse('account_login')))
        self.assertContains(response,'Use a local account to log in.')

class CreateClientTests(TestCase):

    def setUp(self):
        self.user=get_user_model().objects.create_user(
            first_name="Rick",
            last_name="Hiller",
            email="rhiller@gmail.com",
            password="aldrich123",
        )
        self.user=get_user_model().objects.get(first_name="Rick")
        self.test_client = models.client.objects.create(name="Test Client",number=1.0,slug='test-client')
        self.test_client.users.add(self.user)
        self.test_client.save()

    def test_create_client_form(self):
        name="Test Client #2"
        slug = slugify(name)
        new_client = models.client.objects.create(name=name,number=2.0,slug=slug)
        
        self.assertEqual(models.client.objects.all().count(),2)
        self.assertEqual(models.client.objects.all()[1].name,name)
        self.assertEqual(models.client.objects.all()[1].number,2.0)
    
    def test_create_client_view_for_logged_in_user(self):
        self.client.login(email="rhiller@gmail.com",password="aldrich123")
        response=self.client.get(reverse('create_client'))
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"Client Name")
        self.assertTemplateUsed(response,'new_client.html')

    def test_create_client_view_for_logged_out_user(self):
        self.client.logout()
        response = self.client.get(reverse('create_client'))
        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,'%s?next=/dashboard/create_client' % (reverse('account_login')))
        response = self.client.get('%s?next=/dashboard/create_client' % (reverse('account_login')))
        self.assertContains(response,'Use a local account to log in.')

    def test_create_client_assigned_to_multiple_users(self):
        emma= get_user_model().objects.create_user(
            email="testuser@gmail.com",
            password = "aldrich123",
            first_name = "Emma",
            last_name = "Wagner",
        )
        emma= get_user_model().objects.get(first_name="Emma")
        rick = get_user_model().objects.get(first_name="Rick")

        self.test_client.users.add(emma)
        self.test_client.save()

        self.assertEqual(self.test_client.users.all()[0],rick)
        self.assertEqual(self.test_client.users.all()[1],emma)

    def test_new_client_shows_up_for_multiple_users(self):
        #Creating a new user
        emma= get_user_model().objects.create_user(
            email="testuser@gmail.com",
            password = "aldrich123",
            first_name = "Emma",
            last_name = "Wagner",
        )
        emma= get_user_model().objects.get(first_name="Emma")

        #Adding the existing client to the new users dashboard
        self.test_client.users.add(emma)
        self.test_client.save()
 
        #Logging in as the main user and making sure the client shows up on their dashboard
        self.client.login(email="rhiller@gmail.com",password="aldrich123")
        response=self.client.get(reverse('client_dashboard'))
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"1.0")
        self.assertTemplateUsed(response,'client_dashboard.html')

        #Logging out of the first user
        self.client.logout()

        #Logging in as the new user and making sure the client shows up on their dahsboard.
        self.client.login(email="testuser@gmail.com",password="aldrich123")
        response=self.client.get(reverse('client_dashboard'))
        self.assertEqual(response.status_code,200)
        self.assertContains(response,"1.0")
        self.assertTemplateUsed(response,'client_dashboard.html')

    def test_client_with_same_name(self):
        self.assertRaises(Exception,models.client.objects.create(name="Test Client",number=2.0))

        self.assertRaises(Exception,models.client.objects.create(name="New Test Client",number=1.0))


        