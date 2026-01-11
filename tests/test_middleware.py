import pytest
from django.test import RequestFactory
from orders.middleware import RequestMiddleware, get_current_request, get_client_ip


@pytest.mark.django_db
def test_request_context_available_in_signal():
    factory = RequestFactory()
    request = factory.get("/fake-url/")
    middleware = RequestMiddleware(lambda req: None)
    middleware.__call__(request)
    # After __call__, request should be cleaned
    assert get_current_request() is None


@pytest.mark.django_db
def test_ip_extraction_from_headers():
    factory = RequestFactory()
    request = factory.get("/fake-url/", REMOTE_ADDR="127.0.0.1")

    ip = get_client_ip(request)

    assert ip == "127.0.0.1"
