from accounts.factories import UserFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from testing.base import BaseAPITest


class UserprofleTest(BaseAPITest):
    def setUp(self):
        self.test_user = UserFactory()
        super().setUp()

    def test_get_userprofile(self):
        url = reverse("accounts_userprofile")

        res: Response = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.test_user)
        res: Response = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # check company id is returned
        user_company = self.test_user.company_set.first()
        self.assertEqual(res.data.get("company_id"), user_company.id)

    def test_update_userprofile(self):
        url = reverse("accounts_userprofile")

        new_data = {
            "first_name": "new name",
            "last_name": "new last name",
        }

        res: Response = self.client.patch(url, new_data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_authenticate(user=self.test_user)
        res: Response = self.client.patch(url, new_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_user_registration_is_marked_as_completed(self):
        url = reverse("accounts_userprofile")
        complete_data = {
            "first_name": "new name",
            "mobile": "+233559899966",
            "email": "me@example.com",
        }
        self.client.force_authenticate(user=self.test_user)
        res: Response = self.client.patch(url, complete_data)
        self.assertTrue(res.data.get("is_registration_completed"))

        incomplete_data = {
            "first_name": "new name",
            "email": "me@example.com",
            "last_name": "",
            "mobile": "",
            "extension": "12345",
        }
        res: Response = self.client.patch(url, incomplete_data)
        self.assertFalse(res.data.get("is_registration_completed"))

    def test_update_profile_picture(self):
        self.client.force_authenticate(user=self.test_user)
        url = reverse("accounts_userprofile")

        new_data = {"profile_picture": self.generate_base64_photo_file()}

        res: Response = self.client.patch(url, new_data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(res.data.get("profile_picture"))

    def test_delete_account(self):
        self.client.force_authenticate(user=self.test_user)
        url = reverse("accounts_userprofile")

        deletion_data = {
            "reason": "not_useful",
            "notes": "Features don't meet my needs",
        }

        response = self.client.delete(url, deletion_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Refresh user from database
        self.test_user.refresh_from_db()
        self.assertFalse(self.test_user.is_active)
        self.assertEqual(self.test_user.deletion_reason, "not_useful")
        self.assertEqual(self.test_user.deletion_notes, deletion_data["notes"])
