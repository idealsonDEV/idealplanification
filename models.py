# -*- coding: utf-8 -*-
from openerp import netsvc
from openerp.osv import osv, fields
from openerp import api
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
from collections import OrderedDict as ord

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
    	'day_hour' : fields.float(string='Heure de travail'),
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
    _name = 'mrp.production.idealplanification.organisation'
    _inherit = ['mail.thread']
    _rec_name = 'id'
    _columns = {
    	'id': fields.char(string='Idenfifiant'),
        'date_debut': fields.date(string='Date de début'),
        'date_fin': fields.date(string='Date de fin'),
        'date_rest': fields.date(string='Date des restes'),
        'std_hour': fields.float(string='Heure de travail standard'),
        'use_cm': fields.boolean(string='Prendre en compte sans contre-mesure'),
    }
    _defaults = {
        'date_debut': date.today() + timedelta(days=1),
        'date_fin': date.today() + relativedelta(months=+3),
        'date_rest': date(2023,01,01),
        'std_hour': 8.0,
        'use_cm': True,
    }

    @api.one
    def organiser(self):
    	cr = self._cr
    	uid = self._uid
    	ids = self._ids
    	context = {}
	#raise osv.except_osv("Erreur!",self)
    	# obtenir les données
    	prod_obj = self.pool.get('mrp.production')
    	stok_obj = self.pool.get('stock.picking')
    	setdays_obj = self.pool.get('mrp.production.idealplanification.setdays')
    	chrono_obj = self.pool.get('mrp.production.idealplanification.chrono')
    	cycle_obj = self.pool.get('mrp.production.idealplanification.cycle')
    	# envoyer vers date des restes
    	## recherche date
    	prod_srh1 = prod_obj.search(cr, uid, [('date_planned', '>=', self.date_debut + ' 00:00:00'),
                                             ('date_planned', '<=', self.date_fin + ' 03:00:00')])
    	## vers date reste
    	#for p in prod_obj.browse(cr, uid, prod_srh1, context=context):
    	#	prod_obj.write(cr, uid, [p['id']], {'date_planned': self.date_rest + ' 00:00:00'})

    	# obtenir les stock
    	## recherche les info stock
    	stok_srh = stok_obj.search(cr, uid, [('date', '>=', self.date_debut + ' 00:00:00'),
                                             ('date', '<=', self.date_fin + ' 03:00:00'),
                                             ('state', '!=', 'draft'),
                                             ('state', '!=', 'cancel'),
                                             ('state', '!=', 'assigned'),
                                             ('state', '!=', 'done'),
                                             ('pack_operation_exist', '=' , True),
                                             ('min_date' , '!=' , False)])
    	## collect
    	stok_dic = ord()
    	for sk in stok_obj.browse(cr, uid, stock_srh, context=context):
    		sdu = ord()
    		sdu['date'] = sk.date
    		sdu['origin'] = sk.origin
    		sdu['ref'] = sk.name
    		sdu['priority'] = sk.priority
    		stok_dic[sk.name] = sdu

    	# obtenir les prod
    	## recherche les info prod
    	prod_srh = prod_obj.search(cr, uid, [()])

    	return True