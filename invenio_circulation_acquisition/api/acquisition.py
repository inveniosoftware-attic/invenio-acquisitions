# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""invenio-circulation-acquisition api handling AcquisitionLoanCycle."""


import datetime

from invenio_circulation.api.item import create as create_item
from invenio_circulation.api.event import create as create_event
from invenio_circulation.api.utils import email_notification
from invenio_circulation.api.utils import ValidationExceptions

from invenio_circulation.models import CirculationItem
from invenio_circulation_acquisition.models import AcquisitionLoanCycle


def _create_acquisition_temporary_item(record):
    acquisition_tmp = 'acquisition_temporary_no_value'
    status = CirculationItem.STATUS_ON_SHELF
    group = CirculationItem.GROUP_BOOK
    item = create_item(record.id, 1, acquisition_tmp, acquisition_tmp,
                       acquisition_tmp, acquisition_tmp,
                       acquisition_tmp, acquisition_tmp, status, group)
    item.additional_statuses.append('acquisition_temporary')
    item.save()

    return item


def request_acquisition(user, record, acquisition_type, copies,
                        payment_method, budget_code='', price='', currency='',
                        delivery=None, comments=''):
    """Request an acquisition for the given record to the given user.

    :param user: CirculationUser.
    :param record: Invenio Record.
    :param acquisition_type: Purchase or acquisition.
    :param payment_method: PAYMENT_METHOD_CASH or PAYMENT_METHOD_BUDGET_CODE.
    :param delivery: 'pick_up' or 'internal_mail'
    :param comments: Comments regarding the inter library loan.

    :return: Created IllLoanCycle
    """
    if not delivery:
        delivery = AcquisitionLoanCycle.DELIVERY_DEFAULT

    item = _create_acquisition_temporary_item(record)

    acquisition_clc = AcquisitionLoanCycle.new(
            current_status=AcquisitionLoanCycle.STATUS_REQUESTED,
            item=item, user=user,
            acquisition_type=acquisition_type,
            copies=copies,
            payment_method=payment_method,
            budget_code=budget_code,
            price=price,
            currency=currency,
            delivery=delivery,
            comments=comments,
            issued_date=datetime.datetime.now())

    if acquisition_type == 'acquisition':
        event = AcquisitionLoanCycle.EVENT_ACQUISITION_REQUEST
    elif acquisition_type == 'purchase':
        event = AcquisitionLoanCycle.EVENT_PURCHASE_REQUEST

    create_event(user_id=user.id, item_id=item.id,
                 acquisition_loan_cycle_id=acquisition_clc.id,
                 event=event)

    email_notification('acquisition_request', 'john.doe@cern.ch', user.email,
                       name=user.name, action='requested', items=item)

    return acquisition_clc


def try_confirm_acquisition_request(acquisition_loan_cycle):
    """Check the conditions to confirm a given acquisition.

    Checked conditions:
    * The current_status must be 'requested'.

    :param acquisition_loan_cycle: Requested inter library loan.
    """
    exceptions = []
    try:
        status = AcquisitionLoanCycle.STATUS_REQUESTED
        assert (acquisition_loan_cycle.current_status == status,
                'The acquisition loan cycle is in the wrong state')
    except AssertionError as e:
        exceptions.append(('acquisition', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def confirm_acquisition_request(acquisition_loan_cycle,
                                vendor_id, price, currency, comments=''):
    """Confirm the given acquisition.

    The acquisition_loan_cycles current_status will be set to 'ordered'.
    The provided vendor_id, price, currency and comments will be set.

    :param vendor_id: Id of the chosen AcquisitionVendor.

    :raise: ValidationExceptions
    """
    try:
        try_confirm_acquisition_request(acquisition_loan_cycle)
    except ValidationExceptions as e:
        raise e

    acquisition_loan_cycle.current_status = AcquisitionLoanCycle.STATUS_ORDERED
    acquisition_loan_cycle.vendor_id = vendor_id
    acquisition_loan_cycle.price = price
    acquisition_loan_cycle.currency = currency
    acquisition_loan_cycle.comments = comments
    acquisition_loan_cycle.save()

    create_event(acquisition_loan_cycle_id=acquisition_loan_cycle.id,
                 event=AcquisitionLoanCycle.EVENT_ACQUISITION_ORDERED)

    email_notification('acquisition_ordered', 'john.doe@cern.ch',
                       acquisition_loan_cycle.user.email,
                       acquisition_loan_cycle=acquisition_loan_cycle)


def try_receive_acquisition(acquisition_loan_cycle):
    """Check the conditions to receive a given acquisition.

    Checked conditions:
    * The current_status must be 'ordered'.

    :param acquisition_loan_cycle: Requested inter library loan.
    """
    exceptions = []
    try:
        status = AcquisitionLoanCycle.STATUS_ORDERED
        assert (acquisition_loan_cycle.current_status == status,
                'The acquisition loan cycle is in the wrong state')
    except AssertionError as e:
        exceptions.append(('acquisition', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def receive_acquisition(acquisition_loan_cycle):
    """Receive the given acquisition.

    The acquisition_loan_cycles current_status will be set to 'received'.

    :raise: ValidationExceptions
    """
    try:
        try_receive_acquisition(acquisition_loan_cycle)
    except ValidationExceptions as e:
        raise e

    status = AcquisitionLoanCycle.STATUS_RECEIVED
    acquisition_loan_cycle.current_status = status
    acquisition_loan_cycle.save()

    create_event(acquisition_loan_cycle_id=acquisition_loan_cycle.id,
                 event=AcquisitionLoanCycle.EVENT_ACQUISITION_RECEIVED)

    email_notification('acquisition_ordered', 'john.doe@cern.ch',
                       acquisition_loan_cycle.user.email,
                       acquisition_loan_cycle=acquisition_loan_cycle)


def try_cancel_acquisition_request(acquisition_loan_cycle):
    """Check the conditions to cancel a given acquisition.

    Checked conditions:
    * The current_status must be 'requested' or 'ordered'.

    :param acquisition_loan_cycle: Requested inter library loan.
    """
    exceptions = []
    try:
        status1 = AcquisitionLoanCycle.STATUS_REQUESTED
        status2 = AcquisitionLoanCycle.STATUS_ORDERED
        assert (acquisition_loan_cycle.current_status == status1 or
                acquisition_loan_cycle.current_status == status2,
                'The acquisition loan cycle is in the wrong state')
    except AssertionError as e:
        exceptions.append(('acquisition', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def cancel_acquisition_request(acquisition_loan_cycle, reason=''):
    """Cancel the given acquisition.

    The acquisition_loan_cycles current_status will be set to 'canceled'.

    :raise: ValidationExceptions
    """
    try:
        try_cancel_acquisition_request(acquisition_loan_cycle)
    except ValidationExceptions as e:
        raise e

    status = AcquisitionLoanCycle.STATUS_CANCELED
    acquisition_loan_cycle.current_status = status
    acquisition_loan_cycle.save()

    create_event(acquisition_loan_cycle_id=acquisition_loan_cycle.id,
                 event=AcquisitionLoanCycle.EVENT_ACQUISITION_CANCELED,
                 description=reason)


def try_decline_acquisition_request(acquisition_loan_cycle):
    """Check the conditions to decline a given acquisition.

    Checked conditions:
    * The current_status must be 'requested'.

    :param acquisition_loan_cycle: Requested inter library loan.
    """
    exceptions = []
    try:
        status = AcquisitionLoanCycle.STATUS_REQUESTED
        assert (acquisition_loan_cycle.current_status == status,
                'The acquisition loan cycle is in the wrong state')
    except AssertionError as e:
        exceptions.append(('acquisition', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def decline_acquisition_request(acquisition_loan_cycle):
    """Decline the given acquisition.

    The acquisition_loan_cycles current_status will be set to 'declined'.

    :raise: ValidationExceptions
    """
    try:
        try_decline_acquisition_request(acquisition_loan_cycle)
    except ValidationExceptions as e:
        raise e

    status = AcquisitionLoanCycle.STATUS_DECLINED
    acquisition_loan_cycle.current_status = status
    acquisition_loan_cycle.save()

    create_event(acquisition_loan_cycle_id=acquisition_loan_cycle.id,
                 event=AcquisitionLoanCycle.EVENT_ACQUISITION_DECLINED)

    email_notification('acquisition_declined', 'john.doe@cern.ch',
                       acquisition_loan_cycle.user.email,
                       acquisition_loan_cycle=acquisition_loan_cycle)


def try_deliver_acquisition(acquisition_loan_cycle):
    """Check the conditions to deliver a given acquisition.

    Checked conditions:
    * The current_status must be 'ordered'.

    :param acquisition_loan_cycle: Requested inter library loan.
    """
    exceptions = []
    try:
        status = AcquisitionLoanCycle.STATUS_ORDERED
        assert (acquisition_loan_cycle.current_status == status,
                'The acquisition loan cycle is in the wrong state')
    except AssertionError as e:
        exceptions.append(('acquisition', e))

    if exceptions:
        raise ValidationExceptions(exceptions)


def deliver_acquisition(acquisition_loan_cycle):
    """Deliver the given acquisition.

    The acquisition_loan_cycles current_status will be set to 'delivered'.

    :raise: ValidationExceptions
    """
    try:
        try_deliver_acquisition(acquisition_loan_cycle)
    except ValidationExceptions as e:
        raise e

    status = AcquisitionLoanCycle.STATUS_DELIVERED
    acquisition_loan_cycle.current_status = status
    acquisition_loan_cycle.save()

    create_event(acquisition_loan_cycle_id=acquisition_loan_cycle.id,
                 event=AcquisitionLoanCycle.EVENT_ACQUISITION_DELIVERED)

    email_notification('acquisition_delivery', 'john.doe@cern.ch',
                       acquisition_loan_cycle.user.email,
                       acquisition_loan_cycle=acquisition_loan_cycle)
