# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class idealplanitication(models.Model):
#     _name = 'idealplanitication.idealplanitication'

#     name = fields.Char()

class PlaniticationChrono(models.Model):
    _name = 'mrp.production.idealplanitication.chrono'

    ar_name = fields.Char(string='Categorie')
    ar_time = fields.Float(string='Time', compute="_compute_time")
    ar_use = fields.Boolean(sting='Utiliser')

class PlaniticationDays(models.Model):
    _name = 'mrp.production.idealplanitication.setdays'

    day_date = fields.Date(string='Date')
    day_hour = fields.Float(string='Heur de travaille', compute="_compute_time")
    day_use = fields.Boolean(sting='Utiliser')

class PlaniticationCycle(models.Model):
    _name = 'mrp.production.idealplanitication.cycle'

    cy_seq = fields.Integer(string='Sequance')
    cy_val = fields.Char(string='Categorie')
    cy_if_ens = fields.Boolean(sting='Ensemble')
    cy_if_oth = fields.Boolean(sting='Autre')