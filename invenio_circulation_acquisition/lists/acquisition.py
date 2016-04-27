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

"""invenio-circulation-acquisition list classes."""


import invenio_circulation_acquisition.models as models

from flask import render_template


class BaseAcquisitions(object):
    """invenio-circulation-acquisition list base class providing the UI."""

    positive_actions = None
    negative_actions = None

    @classmethod
    def entrance(cls):
        """List class function providing first stage user interface."""
        q = 'current_status:{0} acquisition_type:{1}'.format(
                cls.current_status, cls.acquisition_type)
        acquisition_lcs = models.AcquisitionLoanCycle.search(q)
        return render_template('lists/base_acquisitions.html',
                               acquisition_lcs=acquisition_lcs,
                               active_nav='lists',
                               positive_actions=cls.positive_actions,
                               negative_actions=cls.negative_actions)

    @classmethod
    def data(cls):
        """List class function providing the lists data."""
        q = 'current_status:{0} acquisition_type:{1}'.format(
                cls.current_status, cls.acquisition_type)
        return [{'id': x.id,
                 'item': cls._make(x),
                 'type': cls.type,
                 'positive_actions': cls.positive_actions,
                 'negative_actions': cls.negative_actions}
                for x in models.AcquisitionLoanCycle.search(q)]

    @classmethod
    def _make(cls, loan_cycle):
        item = {}
        for name, accessor in zip(cls.table_header, cls.item_accessors):
            accessors = accessor.split('.')
            tmp = loan_cycle
            try:
                for access in accessors:
                    tmp = tmp.__getattribute__(access)
            except AttributeError:
                tmp = None
            item[name] = tmp

        return item


class RequestedPurchase(BaseAcquisitions):
    """invenio-circulation-acquisition list to show the requested purchases."""

    table_header = ['Borrower', 'CCID', 'Record']
    item_accessors = ['user.name', 'user.ccid', 'item.record.title']
    type = 'Purchase Request'
    current_status = models.AcquisitionLoanCycle.STATUS_REQUESTED
    acquisition_type = models.AcquisitionLoanCycle.TYPE_PURCHASE
    positive_actions = [('confirm_acquisition_request', 'CONFIRM',
                         'acquisition_confirmation')]
    negative_actions = [('cancel_acquisition_request', 'CANCEL')]


class OrderedPurchase(BaseAcquisitions):
    """invenio-circulation-acquisition list to show the ordered purchases."""

    current_status = models.AcquisitionLoanCycle.STATUS_ORDERED
    acquisition_type = models.AcquisitionLoanCycle.TYPE_PURCHASE
    positive_actions = [('deliver_acquisition', 'DELIVER', None)]
    negative_actions = [('cancel_acquisition_request', 'CANCEL')]


class RequestedAcquisition(BaseAcquisitions):
    """invenio-circulation-acquisition list showing requested acquisitions."""

    current_status = models.AcquisitionLoanCycle.STATUS_REQUESTED
    acquisition_type = models.AcquisitionLoanCycle.TYPE_ACQUISITION
    positive_actions = [('confirm_acquisition_request', 'CONFIRM',
                         'acquisition_vendor_price')]
    negative_actions = [('cancel_acquisition_request', 'CANCEL')]


class OrderedAcquisition(BaseAcquisitions):
    """invenio-circulation-acquisition list showing ordered acquisitions."""

    current_status = models.AcquisitionLoanCycle.STATUS_ORDERED
    acquisition_type = models.AcquisitionLoanCycle.TYPE_ACQUISITION
    positive_actions = [('deliver_acquisition', 'DELIVER', None)]
    negative_actions = [('cancel_acquisition_request', 'CANCEL')]
