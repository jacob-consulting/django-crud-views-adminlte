import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.urls import reverse

import crud_views_adminlte


def test_version():
    assert crud_views_adminlte.__version__ == "0.1.0"


def test_system_check_clean():
    call_command("check", fail_level="WARNING")


@pytest.mark.django_db
@pytest.mark.xfail(strict=True, reason="Task 3")
def test_list_page_renders(client):
    user = get_user_model().objects.create_superuser("admin", "admin@example.com", "admin")
    client.force_login(user)
    response = client.get(reverse("author-list"))
    assert response.status_code == 200
    assert 'class="app-main"' in response.content.decode()
