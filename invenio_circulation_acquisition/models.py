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

"""invenio-circulation-acquisition database models."""


from invenio_circulation.models import ArrayType, CirculationObject
from invenio_db import db


class AcquisitionLoanCycle(CirculationObject, db.Model):
    """Data model to store acquisition information.

    Information associated with the acquisition loan cycle is stored in an
    object of this class.
    The assigned information include:
    * The corresponding user.
    * The corresponding item.
    * The corresponding vendor.
    * Prices and currencies.
    """

    __tablename__ = 'acquisition_loan_cycle'
    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    current_status = db.Column(db.String(255))
    additional_statuses = db.Column(ArrayType(255))
    item_id = db.Column(db.BigInteger,
                        db.ForeignKey('circulation_item.id'))
    item = db.relationship('CirculationItem')
    user_id = db.Column(db.BigInteger,
                        db.ForeignKey('circulation_user.id'))
    user = db.relationship('CirculationUser')
    vendor_id = db.Column(db.BigInteger,
                          db.ForeignKey('acquisition_vendor.id'))
    vendor = db.relationship('AcquisitionVendor')
    acquisition_type = db.Column(db.String(255))
    delivery = db.Column(db.String(255))
    copies = db.Column(db.BigInteger)
    comments = db.Column(db.String(255))
    payment_method = db.Column(db.String(255))
    budget_code = db.Column(db.String(255))
    invoice = db.Column(db.String(255))
    price = db.Column(db.String(255))
    currency = db.Column(db.String(255))
    issued_date = db.Column(db.DateTime)
    creation_date = db.Column(db.DateTime)
    modification_date = db.Column(db.DateTime)
    _data = db.Column(db.LargeBinary)

    STATUS_REQUESTED = 'requested'
    STATUS_ORDERED = 'ordered'
    STATUS_RECEIVED = 'received'
    STATUS_DELIVERED = 'delivered'
    STATUS_DECLINED = 'declined'
    STATUS_CANCELED = 'canceled'

    TYPE_ACQUISITION = 'acquisition'
    TYPE_PURCHASE = 'purchase'

    PAYMENT_METHOD_CASH = 'acquisition_payment_method_cash'
    PAYMENT_METHOD_BUDGET_CODE = 'acquisition_payment_method_cash_budget_code'

    EVENT_ACQUISITION_REQUEST = 'acquisition_requested'
    EVENT_PURCHASE_REQUEST = 'purchase_requested'
    EVENT_ACQUISITION_ORDERED = 'acquisition_ordered'
    EVENT_ACQUISITION_RECEIVED = 'acquisition_received'
    EVENT_ACQUISITION_DELIVERED = 'acquisition_delivered'
    EVENT_ACQUISITION_CANCELED = 'acquisition_canceled'
    EVENT_ACQUISITION_DECLINED = 'acquisition_declined'

    DELIVERY_DEFAULT = 'pick_up'

    _json_schema = {'type': 'object',
                    'title': 'Loan Cycle',
                    'properties': {
                        'id': {'type': 'integer'},
                        'item_id': {'type': 'integer'},
                        'user_id': {'type': 'integer'},
                        'vendor_id': {'type': 'integer'},
                        'delivery': {'type': 'string'},
                        'copies': {'type': 'integer'},
                        'comments': {'type': 'string'},
                        'payment_method': {'type': 'string'},
                        'budget_code': {'type': 'string'},
                        'price': {'type': 'string'},
                        'current_status': {'type': 'string'},
                        'issued_date': {'type': 'string'},
                        }
                    }


class AcquisitionVendor(CirculationObject, db.Model):
    """Data model to store information regarding utilized vendors."""

    __tablename__ = 'acquisition_vendor'
    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    notes = db.Column(db.String(255))
    _data = db.Column(db.LargeBinary)

    _json_schema = {'type': 'object',
                    'title': 'Loan Cycle',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'address': {'type': 'string'},
                        'email': {'type': 'string'},
                        'phone': {'type': 'string'},
                        'notes': {'type': 'string'},
                        }
                    }


entities = [('Acquisition Loan Cycle', 'acquisition_loan_cycle',
             AcquisitionLoanCycle),
            ('Acquisition Vendor', 'acquisition_vendor', AcquisitionVendor)]
