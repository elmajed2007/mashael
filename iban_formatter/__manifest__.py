# -*- coding: utf-8 -*-

##############################################
#
# Swing Entwicklung betrieblicher Informationssysteme GmbH
# (<http://www.swing-system.com>)
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# Copyright (C) ChriCar Beteiligungs- und Beratungs- GmbH
# all rights reserved
#    11-SEP-2009 (GK) created
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs.
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/> or
# write to the Free Software Foundation, Inc.,
# 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################
{'sequence': 500,
 "name": "Camptocamp IBAN formatting"
    , "version": "1.0"
    , "author": "ChriCar Beteiligungs- und Beratungs- GmbH"
    , "website": "http://www.camptocamp.at"
    , "description": """
validates check digits and formats IBAN in group by 4 characters

CAUTION 
- please make sure that the payment module removes the spaces again
- in case of strange errors please update your python-stdnum to >1.0
"""
    , "category": "Client Modules/Camptocamp"
    , "depends": ["base_iban"]
    , "init_xml": []
    , "demo": []
    , "data": [
    'views/iban_view.xml',
]
    , "auto_install": False
    , 'installable': True
    , 'application': False
 }
