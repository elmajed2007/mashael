# -*- coding: utf-8 -*-

from odoo import models, fields


class PenalityRule(models.Model):
    _name = 'hr.penalty.policy'
    _description = 'Penalty Policies'

    name = fields.Char(string='Group Name', required=True)
    line_ids = fields.One2many(comodel_name='hr.penalty.policy.line', inverse_name='penalty_id', string='Penalty Lines')


class PenalityRuleLine(models.Model):
    _name = 'hr.penalty.policy.line'
    _description = 'Penalty Lines'

    penalty_id = fields.Many2one(comodel_name='hr.penalty.policy', string='Penalty Policies')
    name = fields.Char(string='Rule Name', required=True)
    first = fields.Float('First Time', default=1)
    second = fields.Float('Second Time', default=1)
    third = fields.Float('Third Time', default=1)
    fourth = fields.Float('Fourth Time', default=1)
    fifth = fields.Float('Fifth Time', default=1)
