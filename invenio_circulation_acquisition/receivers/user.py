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

"""invenio-circulation-acquisition receiver to handle user signals."""


from invenio_circulation.signals import user_current_holds


def _user_current_holds(sender, data):
    import invenio_circulation_acquisition.models as models

    from flask import render_template

    user_id = data
    SR = models.AcquisitionLoanCycle.STATUS_REQUESTED
    SO = models.AcquisitionLoanCycle.STATUS_ORDERED
    TR = models.AcquisitionLoanCycle.TYPE_ACQUISITION
    TP = models.AcquisitionLoanCycle.TYPE_PURCHASE

    q = 'user_id:{0} current_status:{1} acquisition_type:{2}'

    def _search(status, additional_status):
        query = q.format(user_id, status, additional_status)
        return [clc for clc in models.AcquisitionLoanCycle.search(query)]

    requested_acquisition = _search(SR, TR)
    requested_acquisition_heading = "Current Acquisition Requests"

    ordered_acquisition = _search(SO, TR)
    ordered_acquisition_heading = "Current Acquisition Orders"

    requested_purchase = _search(SR, TP)
    requested_purchase_heading = "Current Purchase Requests"

    ordered_purchase = _search(SO, TP)
    ordered_purchase_heading = "Current Purchase Orders"

    return {'name': 'acquisition', 'priority': 0.7,
            'result': [render_template('user/acquisition_holds.html',
                                       heading=requested_acquisition_heading,
                                       holds=requested_acquisition),
                       render_template('user/acquisition_holds.html',
                                       heading=ordered_acquisition_heading,
                                       holds=ordered_acquisition),
                       render_template('user/acquisition_holds.html',
                                       heading=requested_purchase_heading,
                                       holds=requested_purchase),
                       render_template('user/acquisition_holds.html',
                                       heading=ordered_purchase_heading,
                                       holds=ordered_purchase)]}

user_current_holds.connect(_user_current_holds)
