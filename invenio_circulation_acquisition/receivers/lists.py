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

"""invenio-circulation-acquisition receiver to handle list signals."""


from invenio_circulation.signals import (lists_overview,
                                         lists_class)


def _lists_overview(sender, data):
    return {'name': 'acquisition_lists',
            'priority': 1.0,
            'result': [('Purchase Requests', 'requested_purchase'),
                       ('Ordered Purchase Requests', 'ordered_purchase'),
                       ('Acquisition Requests', 'requested_acquisition'),
                       ('Ordered Acquisition Requests',
                        'ordered_acquisition')]}


def _lists_class(link, data):
    from invenio_circulation_acquisition.lists.acquisition import *

    clazzes = {'requested_acquisition': RequestedAcquisition,
               'ordered_acquisition': OrderedAcquisition,
               'requested_purchase': RequestedPurchase,
               'ordered_purchase': OrderedPurchase}

    return {'name': 'acquisition_lists', 'result': clazzes.get(link)}

lists_overview.connect(_lists_overview)
lists_class.connect(_lists_class)
