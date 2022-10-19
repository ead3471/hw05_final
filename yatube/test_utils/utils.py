from django.forms import ModelForm
from django.test import TestCase, Client
from typing import Callable, Dict


def check_responses_of_given_urls(test_case: TestCase,
                                  client: Client,
                                  response_check_function: Callable,
                                  urls_and_expexted_values: Dict):
    """The function accepts responses from the given urls
       and checks if they match the expected values
       by the given responce_check_function """

    for url, expected_value in urls_and_expexted_values.items():
        with test_case.subTest(url=url, expected_value=expected_value):
            response = client.get(url)
            response_check_function(test_case, response, expected_value)


def check_status_code(test_case: TestCase, response, expected_value):
    test_case.assertEquals(response.status_code, expected_value)


def check_template(test_case: TestCase, response, expected_value):
    test_case.assertTemplateUsed(response, expected_value)


def check_redirect(test_case: TestCase, response, expected_value):
    test_case.assertRedirects(response, expected_value)


def check_form_fields_type(test_case: TestCase,
                           form: ModelForm,
                           fields: Dict):

    for field_name, expected_type in fields.items():
        with test_case.subTest(field_name=field_name,
                               expected_type=expected_type):
            field = form.fields.get(field_name)
            test_case.assertIsInstance(field, expected_type)
