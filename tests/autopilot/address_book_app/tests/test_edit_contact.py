# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
# Copyright 2013 Canonical
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.

"""Tests for the Addressbook App"""

from testtools.matchers import Equals
from autopilot.matchers import Eventually

from address_book_app.address_book import data
from address_book_app.tests import AddressBookAppTestCase


class TestEditContact(AddressBookAppTestCase):
    """Tests edit a contact"""

    PHONE_NUMBERS = ['(333) 123-4567', '(333) 123-4568', '(222) 222-2222']

    def add_test_contact(self):
        test_contact = data.Contact('test', 'test')
        # TODO implement the filling of professional details.
        # --elopio - 2014-03-01
        test_contact.professional_details = []

        # execute add new contact
        contact_editor = self.main_window.go_to_add_contact()
        contact_editor.fill_form(test_contact)

        # Save contact
        self.main_window.save()

    def test_add_new_phone(self):
        self.add_contact("Fulano", "de Tal", [self.PHONE_NUMBERS[0]])
        edit_page = self.edit_contact(0)

        # Add a new phone
        edit_page.add_field('phones')

        # fill phone number
        phone_number_1 = self.app.main_window.select_single(
            "TextInputDetail",
            objectName="phoneNumber_1")
        self.type_on_field(phone_number_1, self.PHONE_NUMBERS[1])

        self.app.main_window.save()

        # go back to view page
        view_page = self.app.main_window.get_contact_view_page()
        self.assertThat(view_page.visible, Eventually(Equals(True)))

        # check if we have two phones"""
        phone_group = view_page.select_single(
            "ContactDetailGroupWithTypeView",
            objectName="phones")
        self.assertThat(phone_group.detailsCount, Eventually(Equals(2)))

        # check if the new value is correct
        phone_label_1 = view_page.select_single(
            "UCLabel",
            objectName="label_phoneNumber_1.0")
        self.assertThat(phone_label_1.text,
                        Eventually(Equals(self.PHONE_NUMBERS[1])))

    def test_remove_phone(self):
        contact_editor = self.app.main_window.go_to_add_contact()
        my_phones = []
        for n in self.PHONE_NUMBERS[1:3]:
            my_phones.append(data.Phone(type_='Mobile', number=n))

        test_contact = data.Contact(first_name="Fulano",
                                    last_name="de Tal",
                                    phones=my_phones)
        contact_editor.fill_form(test_contact)

        # clear phone 1
        phone_number_1 = contact_editor.wait_select_single(
            "TextInputDetail",
            objectName="phoneNumber_1")
        self.clear_text_on_field(phone_number_1)

        # Save contact
        self.app.main_window.save()

        # Go to contact view
        list_page = self.main_window.get_contact_list_page()

        # check if we have onlye one phone
        view_page = list_page.open_contact(0)
        phone_group = self.main_window.wait_select_single(
            "ContactDetailGroupWithTypeView",
            objectName="phones")
        self.assertThat(phone_group.detailsCount, Eventually(Equals(1)))

        # check if the new value is correct
        phone_label_1 = phone_group.wait_select_single(
            "UCLabel",
            objectName="label_phoneNumber_0.0")
        self.assertThat(phone_label_1.text,
                        Eventually(Equals(self.PHONE_NUMBERS[1])))

    def test_add_email(self):
        self.add_contact("Fulano", "")
        edit_page = self.edit_contact(0)
        edit_page.add_field("emails")

        # fill email address
        email_field = edit_page.select_single(
            "TextInputDetail",
            objectName="emailAddress_0")
        self.type_on_field(email_field, "fulano@internet.com.br")

        self.app.main_window.save()

        # go back to view page
        view_page = self.app.main_window.get_contact_view_page()
        self.assertThat(view_page.visible, Eventually(Equals(True)))

        # check if we have a new email
        email_group = self.main_window.select_single(
            "ContactDetailGroupWithTypeView",
            objectName="emails")
        self.assertThat(email_group.detailsCount, Eventually(Equals(1)))

        # check if the new value is correct
        email_label_1 = email_group.select_single(
            "UCLabel",
            objectName="label_emailAddress_0.0")
        self.assertThat(email_label_1.text,
                        Eventually(Equals("fulano@internet.com.br")))

    def test_remove_email(self):
        self.add_contact("Fulano", "de Tal", None, ["fulano@email.com"])
        edit_page = self.edit_contact(0)

        # clear email
        email_address_0 = edit_page.select_single(
            "TextInputDetail",
            objectName="emailAddress_0")
        self.clear_text_on_field(email_address_0)

        # Save contact
        self.app.main_window.save()

        # check if the email list is empty
        view_page = self.app.main_window.get_contact_view_page()
        emails_group = self.main_window.select_single(
            "ContactDetailGroupWithTypeView",
            objectName="emails")
        self.assertThat(emails_group.detailsCount, Eventually(Equals(0)))

    def test_clear_names(self):
        self.add_contact("Fulano", "de Tal")
        edit_page = self.edit_contact(0)

        first_name_field = edit_page.select_single(
            "TextInputDetail",
            objectName="firstName")
        last_name_field = edit_page.select_single(
            "TextInputDetail",
            objectName="lastName")

        # clear names
        self.clear_text_on_field(first_name_field)
        self.clear_text_on_field(last_name_field)

        # check if is possible to save a contact without name
        self.assertThat(edit_page.saveActionEnabled, Eventually(Equals(False)))

        # Cancel edit
        self.app.main_window.cancel()

        # Check if the names still there
        view_page = self.app.main_window.get_contact_view_page()
        self.assertThat(view_page.headerTitle, Eventually(Equals("Fulano de Tal")))

    def test_im_type(self):
        contact_editor = self.app.main_window.go_to_add_contact()
        alias = data.SocialAlias(type_="Skype", alias="im@account.com")
        test_contact = data.Contact(first_name="Fulano",
                                    last_name="de Tal",
                                    social_aliases=[alias])
        contact_editor.fill_form(test_contact)

        # Save contact
        self.app.main_window.save()

        # edit again
        edit_page = self.edit_contact(0)

        # Change Im type
        im_value_selector = edit_page.select_single(
            "ValueSelector",
            objectName="type_onlineAccount_0")
        self.pointing_device.click_object(im_value_selector)
        self.assertThat(im_value_selector.expanded, Eventually(Equals(True)))

        im_address_0 = edit_page.select_single(
            "TextInputDetail",
            objectName="imUri_0")

        # select the type with index = 0
        self.select_a_value(im_address_0, im_value_selector, 0)

        # save contact
        self.app.main_window.save()

        view_page = self.app.main_window.get_contact_view_page()

        # check if the type was saved correct
        im_type = view_page.select_single(
            "UCLabel",
            objectName="type_onlineAccount_0")
        self.assertThat(im_type.text, Eventually(Equals("Aim")))
