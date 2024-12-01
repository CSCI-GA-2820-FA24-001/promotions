######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

# pylint: disable=function-redefined, missing-function-docstring
# flake8: noqa
"""
Web Steps

Steps file for web interactions with Selenium

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import logging
from datetime import datetime
from behave import when, then  # pylint: disable=no-name-in-module
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions


ID_PREFIX = "promotion_"
ACTION_PREFIX = ""


@when('I visit the "Home Page"')
def step_impl(context):
    """Make a call to the base URL"""
    context.driver.get(context.base_url)
    # Uncomment next line to take a screenshot of the web page
    # context.driver.save_screenshot('home_page.png')


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """Check the document title for a message"""
    assert message in context.driver.title


@then('I should not see "{text_string}"')
def step_impl(context, text_string):
    element = context.driver.find_element(By.TAG_NAME, "body")
    assert text_string not in element.text


@when("I set the ID with last created UUID")
def step_impl(context):
    element_id = (
        ACTION_PREFIX
        + ID_PREFIX
        + get_id_from_element_name("id").lower().replace(" ", "_")
    )
    element = context.driver.find_element(By.ID, element_id)
    element.clear()
    element.send_keys(context.last_created_uuid)


@when('I set the "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = (
        ACTION_PREFIX
        + ID_PREFIX
        + get_id_from_element_name(element_name).lower().replace(" ", "_")
    )
    element = context.driver.find_element(By.ID, element_id)

    if element_name == "Active Status":
        select = Select(element)
        if text_string == "Active":
            select.select_by_value("true")
        elif text_string == "Inactive":
            select.select_by_value("false")
    else:
        element.clear()
        element.send_keys(text_string)


@when('I select "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = (
        ACTION_PREFIX
        + ID_PREFIX
        + get_id_from_element_name(element_name).lower().replace(" ", "_")
    )
    element = Select(context.driver.find_element(By.ID, element_id))
    element.select_by_visible_text(text)


@then('I should see "{text}" in the "{element_name}" dropdown')
def step_impl(context, text, element_name):
    element_id = (
        ACTION_PREFIX
        + ID_PREFIX
        + get_id_from_element_name(element_name).lower().replace(" ", "_")
    )
    element = Select(context.driver.find_element(By.ID, element_id))
    assert element.first_selected_option.text == text


@then('the "{element_name}" field should be empty')
def step_impl(context, element_name):
    element_id = (
        ACTION_PREFIX
        + ID_PREFIX
        + get_id_from_element_name(element_name).lower().replace(" ", "_")
    )
    element = context.driver.find_element(By.ID, element_id)
    assert element.get_attribute("value") == ""


##################################################################
# These two function simulate copy and paste
##################################################################
@when('I copy the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    context.clipboard = element.get_attribute("value")
    logging.info("Clipboard contains: %s", context.clipboard)


@when('I paste the "{element_name}" field')
def step_impl(context, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(context.clipboard)


##################################################################
# This code works because of the following naming convention:
# The buttons have an id in the html hat is the button text
# in lowercase followed by '-btn' so the Clear button has an id of
# id='clear-btn'. That allows us to lowercase the name and add '-btn'
# to get the element id of any button
##################################################################


@when('I press the "{button}" button')
def step_impl(context, button):
    button_id = button.lower().replace(" ", "_") + "-btn"
    context.driver.find_element(By.ID, button_id).click()


@when('I switch to the "{tab}" tab')
def step_impl(context, tab):
    global ACTION_PREFIX
    ACTION_PREFIX = tab.lower().split(" ")[0] + "_"
    tab_id = tab.lower().replace(" ", "_") + "-tab"
    context.driver.find_element(By.ID, tab_id).click()


@then('I should see "{name}" in the search results')
def step_impl(context, name):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "promotion-data"), name
        )
    )
    assert found


@then(
    'I should see the promotion "{promotion_name}" between "{start_date}" and "{end_date}" in the search results'
)
def step_impl(context, promotion_name, start_date, end_date):
    table = context.driver.find_element(By.CSS_SELECTOR, "#promotion-data tbody")
    rows = table.find_elements(By.TAG_NAME, "tr")  # Get all rows in the table body

    start_date_dt = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S")
    end_date_dt = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S")

    found_promotion = False
    for row in rows:
        # ID | Name | Description | Product IDs | Start Date | End Date | Status | Creator | Updater | Created At | Updated At | Extra
        columns = row.find_elements(By.TAG_NAME, "td")
        name = columns[1].text
        start = datetime.strptime(columns[4].text, "%Y-%m-%dT%H:%M:%S")
        end = datetime.strptime(columns[5].text, "%Y-%m-%dT%H:%M:%S")

        if name == promotion_name and start_date_dt == start and end_date_dt == end:
            found_promotion = True
            break

    assert (
        found_promotion
    ), f"{promotion_name} not found between {start_date_dt} and {end_date_dt} in the search results."


@then(
    'I should see the promotion "{promotion_name}" with "{status}" Status in the search results'
)
def step_impl(context, promotion_name, status):
    table = context.driver.find_element(By.CSS_SELECTOR, "#promotion-data tbody")
    rows = table.find_elements(By.TAG_NAME, "tr")  # Get all rows in the table body

    found_promotion = False
    for row in rows:
        # ID | Name | Description | Product IDs | Start Date | End Date | Status | Creator | Updater | Created At | Updated At | Extra
        columns = row.find_elements(By.TAG_NAME, "td")
        name = columns[1].text
        found_status = columns[6].text.split()[0]

        if name == promotion_name and found_status == status:
            found_promotion = True
            break

    assert (
        found_promotion
    ), f"{promotion_name} not found with {status} status in the search results. The status is {found_status}"


@then('I should not see "{name}" in the results')
def step_impl(context, name):
    element = context.driver.find_element(By.ID, "promotion-data")
    assert name not in element.text


@then('I should see the message "{message}"')
def step_impl(context, message):
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element(
            (By.ID, "flash_message"), message
        )
    )
    assert found


@then("I should see the message with Promotion created successfully")
def step_impl(context):
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.visibility_of_element_located((By.ID, "flash_message"))
    )
    text = element.text

    assert text.startswith("Promotion created successfully.")

    promotion_id_text = text.replace(
        "Promotion created successfully. The Promotion ID is ", ""
    ).strip()

    assert len(promotion_id_text) > 0


##################################################################
# This code works because of the following naming convention:
# The id field for text input in the html is the element name
# prefixed by ID_PREFIX so the Name field has an id='pet_name'
# We can then lowercase the name and prefix with pet_ to get the id
##################################################################


@then('I should see "{text_string}" in the "{element_name}" field')
def step_impl(context, text_string, element_name):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    found = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.text_to_be_present_in_element_value(
            (By.ID, element_id), text_string
        )
    )
    assert found


@when('I change "{element_name}" to "{text_string}"')
def step_impl(context, element_name, text_string):
    element_id = ID_PREFIX + element_name.lower().replace(" ", "_")
    element = WebDriverWait(context.driver, context.wait_seconds).until(
        expected_conditions.presence_of_element_located((By.ID, element_id))
    )
    element.clear()
    element.send_keys(text_string)


def get_id_from_element_name(element_name: str):
    if element_name in ["Creator's UUID", "Updater's UUID"]:
        element_name = element_name.split("'")[0]
    elif element_name == "Additional MetaData":
        element_name = "extra"
    return element_name
