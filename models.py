# -*- coding: utf-8 -*-
from openerp import netsvc
from openerp.osv import osv, fields
from openerp import api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

# class idealplanitication(models.Model):
#     _name = 'idealplanitication.idealplanitication'

#     name = fields.Char()

class PlaniticationChrono(osv.osv):
    _name = 'mrp.production.idealplanification.chrono'
    _rec_name = 'ar_name'
    _inherit = ['mail.thread']
    _columns = {
    	'ar_name' : fields.char(string='Article'),
    	'ar_desc' : fields.char(string='Description'),
    	'ar_time' : fields.integer(string='Temps (en seconde)'),
    	'ar_use' : fields.boolean(string='Utiliser'),
    }
     _defaults = {
     	'ar_use' : True,
     }
    #def _compute_time(self):
    #	for each in self:
    #		res = 

class PlaniticationDays(osv.osv):
    _name = 'mrp.production.idealplanification.setdays'
    _inherit = ['mail.thread']
    _rec_name = 'day_date'
    _columns = {
    	'day_date' : fields.date(string='Date'),
    	'day_val' : fields.many2many('mrp.production.idealplanification.chrono', 'setdays_chrono_rel', string='Articles'),
    	'day_hour' : fields.float(string='Heur de travaille'),
    	'day_use' : fields.boolean(string='Utiliser'),
    }
    _defaults = {
    	'day_hour' : 8.0,
     	'day_use' : True,
     }

class PlaniticationCycle(osv.osv):
    _name = 'mrp.production.idealplanification.cycle'
    _inherit = ['mail.thread']
    _columns = {
    	'cy_seq' : fields.integer(string='Sequance'),
    	'cy_val' : fields.many2many('mrp.production.idealplanification.chrono', 'cycle_chrono_rel', string='Articles'),
    	'cy_if_ens' : fields.boolean(string='Ensemble'),
    	'cy_if_spe' : fields.boolean(string='Special'),
    	'cy_if_oth' : fields.boolean(string='Autre'),
    }
    _defaults = {
    	'cy_if_ens' : False,
    	'cy_if_spe' : False,
    	'cy_if_oth' : False,
     }

    @api.multi
    def name_get(self):
    	result = []
    	for cyc in self:
    		lt = ""
    		for val in cyc.cy_val:
    			lt += " " + val.ar_name
    		name = str(cyc.cy_seq) + " :" +lt
    		result.append((cyc.id, name))
    	return result

class PlaniticationOrganisation(osv.osv):
	_name = "mrp.production.idealplanification.organisation"
    _columns = {
        'date_debut': fields.date('Date de début'),
        'date_fin': fields.date('Date de fin'),
        'use_cm': fiels.boolean('Prendre en compte sans contre-mesure'),
    }
    _defaults = {
        'date_debut': date.today() + timedelta(days=1),
        'date_fin': date.today() + relativedelta(months=+3),
        'use_cm': True,
    }
    def organiser(self):
    	pass
