# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class idealplanitication(models.Model):
#     _name = 'idealplanitication.idealplanitication'

#     name = fields.Char()

class PlaniticationChrono(models.Model):
    _name = 'mrp.production.idealplanification.chrono'

    ar_name = fields.Char(string='Article')
    ar_desc = fields.Char(string='Description')
    ar_time = fields.Integer(string='Temps')
    ar_use = fields.Boolean(string='Utiliser')

    #def _compute_time(self):
    #	for each in self:
    #		res = 

class PlaniticationDays(models.Model):
    _name = 'mrp.production.idealplanification.setdays'

    day_date = fields.Date(string='Date')
    day_val = fields.Many2many('mrp.production.idealplanification.chrono', string='Arcile')
    day_hour = fields.Float(string='Heur de travaille')
    day_use = fields.Boolean(string='Utiliser')

class PlaniticationCycle(models.Model):
    _name = 'mrp.production.idealplanification.cycle'

    cy_seq = fields.Integer(string='Sequance')
    cy_val = fields.Many2many('mrp.production.idealplanification.chrono', string='Arcile')
    cy_if_ens = fields.Boolean(string='Ensemble')
    cy_if_spe = fields.Boolean(string='Special')
    cy_if_oth = fields.Boolean(string='Autre')