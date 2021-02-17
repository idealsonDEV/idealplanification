#!/usr/bin/python
# -*- coding: utf-8 -*-

from openerp import netsvc
from openerp.osv import osv, fields
from openerp import api
from datetime import datetime, date, timedelta, time
from dateutil.relativedelta import relativedelta
from collections import OrderedDict as ord
import itertools


def intSec2floatTime(intsec):
    (hour, temp1) = divmod(intsec, 3600)
    (tmin, tsec) = divmod(temp1, 60)
    minute = tmin / 60.0
    second = tsec / 3600.0
    return hour + minute + second


class mrp_production2(osv.osv):

    _inherit = ['mrp.production']
    _columns = {'total_hour': fields.float(string='Heure de travail')}
    _defaults = {'total_hour': 0.0}


class PlaniticationChrono(osv.osv):

    _name = 'mrp.production.idealplanification.chrono'
    _rec_name = 'ar_name'
    _inherit = ['mail.thread']
    _columns = {
        'ar_name': fields.char(string='Article'),
        'ar_desc': fields.char(string='Description'),
        'ar_time': fields.integer(string='Temps (en seconde)'),
        'ar_use': fields.boolean(string='Utiliser'),
        }
    _defaults = {'ar_use': True}


    # def _compute_time(self):
    #   for each in self:
    #       res =

class PlaniticationDays(osv.osv):

    _name = 'mrp.production.idealplanification.setdays'
    _inherit = ['mail.thread']
    _rec_name = 'day_date'
    _columns = {
        'day_date': fields.date(string='Date'),
        'day_val': fields.many2many('mrp.production.idealplanification.chrono'
                                    , 'setdays_chrono_rel',
                                    string='Articles'),
        'day_hour': fields.float(string='Heure de travail'),
        'day_use': fields.boolean(string='Utiliser'),
        }
    _defaults = {'day_hour': 8.0, 'day_use': True}


class PlaniticationCycle(osv.osv):

    _name = 'mrp.production.idealplanification.cycle'
    _inherit = ['mail.thread']
    _columns = {
        'cy_seq': fields.integer(string='Sequance'),
        'cy_val': fields.many2many('mrp.production.idealplanification.chrono'
                                   , 'cycle_chrono_rel',
                                   string='Articles'),
        'cy_if_ens': fields.boolean(string='Ensemble'),
        'cy_if_oth': fields.boolean(string='Autres'),
        'cy_if_spe': fields.boolean(string='Special'),
        }
    _defaults = {'cy_if_ens': False, 'cy_if_spe': False}

    @api.multi
    def name_get(self):
        result = []
        for cyc in self:
            lt = ''
            for val in cyc.cy_val:
                lt += ' ' + val.ar_name
            name = str(cyc.cy_seq) + ' :' + lt
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
        'use_cm': fields.boolean(string='Prendre en compte sans contre-mesure'
                                 ),
        }
    _defaults = {
        'date_debut': date.today() + timedelta(days=01),
        'date_fin': date.today() + relativedelta(months=+3),
        'date_rest': date(2199, 01, 01),
        'std_hour': 8.0,
        'use_cm': True,
        }

    @api.one
    def get_chrono(self, dataone):
        cr = self._cr
        uid = self._uid
        ids = self._ids
        context = {}

        chrono_obj = \
            self.pool.get('mrp.production.idealplanification.chrono')
        chrono_srh = chrono_obj.search(cr, uid, [('ar_time', '!=',
                0.0), ('ar_use', '!=', False)])
        chrono_dic = ord()
        for chn in chrono_obj.browse(cr, uid, chrono_srh,
                context=context):
            chu = ord()
            chu['ar_name'] = chn.ar_name
            chu['ar_desc'] = chn.ar_desc
            chu['ar_time'] = chn.ar_time
            chu['ar_use'] = chn.ar_use
            chrono_dic[chn.ar_name] = chu
        chrono = 0
        for chn in chrono_dic:
            if dataone['nomenclature'] != False:
                if chn != 'Autres':
                    if dataone['article'].find(chrono_dic[chn]['ar_name']) != -01:
                        if chrono_dic[chn]['ar_desc'] == False:
                            chrono += chrono_dic[chn]['ar_time']
                            break
                        elif chrono_dic[chn]['ar_desc'] != False:
                            if dataone['description'].find(chrono_dic[chn]['ar_desc']) != -01:
                                chrono += chrono_dic[chn]['ar_time']
                                break
            else:
                    chrono += chrono_dic['Autres']['ar_time']
                    break
        if dataone['moustiquaire'] == True:
                if dataone['article'] != u'Moustiquaire coulissante' \
                    or dataone['article'] != u'Moustiquaire fixe':
                    chrono += 6 * 60
                if dataone['description'].find('4VTX') != -01:
                    chrono += 6 * 60
        if dataone['intermediaire'] == u'avec':
                if dataone['description'].find('1VTL') != -01:
                    chrono += 2 * 60 + 30
                elif dataone['description'].find('2VTX') != -01:
                    chrono += 5 * 60
                elif dataone['description'].find('3VTX') != -01:
                    chrono += 7 * 60 + 30
                elif dataone['description'].find('4VTX') != -01:
                    chrono += 9 * 60 + 50
                else:
                    chrono += 3 * 60
        if dataone['laque'] == True:
                chrono += 4 * 60
        chrono *= dataone['division']
        chrono *= dataone['quantite']
        return chrono

    @api.one
    def organiser(self):
        cr = self._cr
        uid = self._uid
        ids = self._ids
        context = {}

        # raise osv.except_osv("Erreur!",self)
        # obtenir les données

        prod_obj = self.pool.get('mrp.production')
        stok_obj = self.pool.get('stock.picking')
        setdays_obj = \
            self.pool.get('mrp.production.idealplanification.setdays')
        chrono_obj = \
            self.pool.get('mrp.production.idealplanification.chrono')
        cycle_obj = \
            self.pool.get('mrp.production.idealplanification.cycle')

        # obtenir les stock
        # # recherche les info stock

        stok_srh = stok_obj.search(cr, uid, [
            ('date', '>=', self.date_debut + ' 00:00:00'),
            ('date', '<=', self.date_fin + ' 03:00:00'),
            ('state', '!=', 'draft'),
            ('state', '!=', 'cancel'),
            ('state', '!=', 'assigned'),
            ('state', '!=', 'done'),
            ('pack_operation_exist', '=', True),
            ('min_date', '!=', False),
            ])

        # # collect

        stok_dic = ord()
        for sk in stok_obj.browse(cr, uid, stok_srh, context=context):
            sdu = ord()
            sdu['date'] = sk.date
            sdu['origin'] = sk.origin
            sdu['ref_wh'] = sk.name
            sdu['priority'] = sk.priority
            stok_dic[sk.name] = sdu

        # obtenir les prod
        # # creer une list des SO

        lst_SO = []
        for s in stok_dic:
            lst_SO.append(stok_dic[s]['origin'])

        # # recherche les info prod

        if self.use_cm == False:
            prod_srh = prod_obj.search(cr, uid, [('origin', 'in',
                    lst_SO), ('hauteur', '>', 0), ('largeur', '>', 0), ('state', '=', 'draft')])
        else:
            prod_srh = prod_obj.search(cr, uid, [('origin', 'in',
                    lst_SO), ('state', '=', 'draft')])

        # # collect

        prod_dic = ord()
        for prd in prod_obj.browse(cr, uid, prod_srh, context=context):
            pdu = ord()
            pdu['ref_mo'] = prd.name
            pdu['article'] = prd.product_id.display_name
            pdu['origin'] = prd.origin
            pdu['description'] = prd.description
            pdu['standard'] = prd.is_printable
            pdu['intermediaire'] = prd.intermediaire
            pdu['laque'] = prd.laque
            pdu['moustiquaire'] = prd.moustiquaire
            pdu['division'] = prd.nb_division
            pdu['nomenclature'] = prd.bom_id.display_name
            pdu['quantite'] = prd.product_qty
            pdu['tms'] = prd.tms
            prod_dic[prd.name] = pdu

        # # unifier prod et stok

        merged_dic = ord()
        for i in prod_dic:
            for j in stok_dic:
                if prod_dic[i]['origin'] == stok_dic[j]['origin']:
                    merged_dic[i] = prod_dic[i]
                    for keys in stok_dic[j].keys():
                        merged_dic[i][keys] = stok_dic[j][keys]
        for i in merged_dic:

            # raise osv.except_osv("Erreur!",(self.date_debut))

            merged_dic[i]['deadline'] = \
                (datetime.strptime(merged_dic[i]['date'],
                 '%Y-%m-%d %H:%M:%S')
                 - datetime.strptime(self.date_debut + ' 00:00:00',
                 '%Y-%m-%d %H:%M:%S')).days

        #raise osv.except_osv("Erreur!", str(merged_dic))
            # raise osv.except_osv("Erreur!", intSec2floatTime(self.get_chrono(dataone=merged_dic[i])[0]))

        # creer les dates de prod
        # # obtenir le cycle

        cycle_srh = cycle_obj.search(cr, uid, [('cy_seq', '!=', 0),
                ('cy_seq', '!=', False), ('cy_val', '!=', False)])
        cycle_dic = ord()
        for cy in cycle_obj.browse(cr, uid, cycle_srh, context=context):
            cyu = ord()
            cyu['seq'] = cy.cy_seq
            cyu['cy_if_ens'] = cy.cy_if_ens
            cyu['cy_if_spe'] = cy.cy_if_spe
            lst_val = []
            for val in cy.cy_val:
                lst_val.append(val.ar_name)
            cyu['val'] = lst_val
            cycle_dic[cy.cy_seq] = cyu

        # # obtenir les jour deja set

        setdays_srh = setdays_obj.search(cr, uid, [('day_date', '>=',
                self.date_debut), ('day_date', '<=', self.date_fin)])
        setdays_dic = ord()
        for day in setdays_obj.browse(cr, uid, setdays_srh,
                context=context):
            dayu = ord()
            dayu['day_date'] = day.day_date
            lst_val = []
            for val in day.day_val:
                lst_val.append(val.ar_name)
            dayu['day_val'] = lst_val

            #raise osv.except_osv('Erreur!', type(day.day_date))

            dayu['day_hour'] = day.day_hour
            dayu['day_use'] = day.day_use
            dayu['deadline'] = (datetime.strptime(day.day_date
                                + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
                                - datetime.strptime(self.date_debut
                                + ' 00:00:00', '%Y-%m-%d %H:%M:%S'
                                )).days

        # # set total_hour et nombre (dic1)

            prod_srh2 = prod_obj.search(cr, uid, [('date_planned', '>='
                    , dayu['day_date'] + ' 00:00:00'), ('date_planned',
                    '<=', dayu['day_date'] + ' 20:59:59'),
                    ('description', 'like', 'npDpc'), ('state', '=',
                    'draft')])
            total_hour = 0
            nb_art = 0
            lst_mo = []
            for prd in prod_obj.browse(cr, uid, prod_srh2,
                    context=context):
                pdu = ord()
                pdu['ref_mo'] = prd.name
                pdu['article'] = prd.product_id.display_name
                pdu['origin'] = prd.origin
                pdu['description'] = prd.description
                pdu['standard'] = prd.is_printable
                pdu['intermediaire'] = prd.intermediaire
                pdu['laque'] = prd.laque
                pdu['moustiquaire'] = prd.moustiquaire
                pdu['division'] = prd.nb_division
                pdu['nomenclature'] = prd.bom_id.display_name
                pdu['quantite'] = prd.product_qty
                pdu['tms'] = prd.tms
                pdu['total_hour'] = self.get_chrono(dataone=pdu)[0]
                total_hour += pdu['total_hour']
                nb_art += pdu['quantite']
                lst_mo.append(prd.name)
            dayu['total_hour'] = intSec2floatTime(total_hour)
            dayu['nb_art'] = nb_art
            dayu['mos'] = lst_mo
            setdays_dic[day.day_date] = dayu

        # # creer les nouvelles date

        startday = datetime.strptime(self.date_debut + ' 00:00:00',
                '%Y-%m-%d %H:%M:%S')
        endday = datetime.strptime(self.date_fin + ' 00:00:00',
                                   '%Y-%m-%d %H:%M:%S')
        ite = 0
        for (day_c, catcy) in itertools.izip((day for day in (startday
                + timedelta(n) for n in itertools.count()) if day.weekday() not in [5, 6]),
                itertools.cycle(cycle_dic.keys())):
            if day_c.date() == endday.date():
                #raise osv.except_osv("Erreur!", (day_c))
                break
            else:
                ite += 01
            day_i = str(date(day_c.year,day_c.month,day_c.day))
            if day_i not in setdays_dic.keys():
                setdays_dic[day_i] = ord()
                setdays_dic[day_i]['day_date'] = day_i
                setdays_dic[day_i]['deadline'] = (day_c - startday).days
                setdays_dic[day_i]['day_val'] = cycle_dic[catcy]['val']
                if day_c.weekday() in [5, 6]:
                    setdays_dic[day_i]['day_hour'] = 0.0
                    setdays_dic[day_i]['day_use'] = False
                    setdays_dic[day_i]['total_hour'] = 0.0
                    setdays_dic[day_i]['nb_art'] = 0
                    setdays_dic[day_i]['mos'] = []
                else:
                    if cycle_dic[catcy]['cy_if_ens'] == True:
                        setdays_dic[day_i]['day_hour'] = self.std_hour - intSec2floatTime(3.0 * 60 * 60)
                        setdays_dic[day_i]['day_use'] = True
                        setdays_dic[day_i]['total_hour'] = 0.0
                        setdays_dic[day_i]['nb_art'] = 0
                        setdays_dic[day_i]['mos'] = []
                    else:
                        setdays_dic[day_i]['day_hour'] = self.std_hour
                        setdays_dic[day_i]['day_use'] = True
                        setdays_dic[day_i]['total_hour'] = 0.0
                        setdays_dic[day_i]['nb_art'] = 0
                        setdays_dic[day_i]['mos'] = []
        #raise osv.except_osv("Erreur!", str(setdays_dic))
        # affecter les prod aux date

        sort_prod_dic = sorted(merged_dic.items(), key=lambda item: \
                               item[01]['deadline'])
        ignore = []
        for day in setdays_dic:
            if setdays_dic[day]['day_use'] == True:
                for moo in sort_prod_dic:
                    mo = moo[0]
                    if mo not in ignore:
                        if merged_dic[mo]['article'] in setdays_dic[day]['day_val']:
                            raise
                            if setdays_dic[day]['total_hour'] + intSec2floatTime(self.get_chrono(dataone=merged_dic[mo])[0]) < setdays_dic[day]['day_hour']:
                                if merged_dic[mo]['deadline'] < 0:
                                    merged_dic[mo]['date_planned'] = day + ' 00:00:00'
                                    merged_dic[mo]['total_hour'] = intSec2floatTime(self.get_chrono(dataone=merged_dic[mo])[0])
                                    setdays_dic[day]['total_hour'] += merged_dic[mo]['total_hour']
                                    setdays_dic[day]['nb_art'] += merged_dic[mo]['quantite']
                                    setdays_dic[day]['mos'].append(mo)
                                    ignore.append(mo)
                                elif merged_dic[mo]['deadline'] >= 0:
                                    if merged_dic[mo]['deadline'] < setdays_dic[day]['deadline'] + 14:
                                        merged_dic[mo]['date_planned'] = day + ' 00:00:00'
                                        merged_dic[mo]['total_hour'] = intSec2floatTime(self.get_chrono(dataone=merged_dic[mo])[0])
                                        setdays_dic[day]['total_hour'] += merged_dic[mo]['total_hour']
                                        setdays_dic[day]['nb_art'] += merged_dic[mo]['quantite']
                                        setdays_dic[day]['mos'].append(mo)
                                        ignore.append(mo)
                        elif merged_dic[mo]['article'] not in setdays_dic[day]['day_val']:
                            if 'Autres' in setdays_dic[day]['day_val']:
                                if setdays_dic[day]['total_hour'] + intSec2floatTime(self.get_chrono(dataone=merged_dic[mo])[0]) < setdays_dic[day]['day_hour']:
                                    if merged_dic[mo]['deadline'] < 0:
                                        merged_dic[mo]['date_planned'] = day + ' 00:00:00'
                                        merged_dic[mo]['total_hour'] = intSec2floatTime(self.get_chrono(dataone=merged_dic[mo])[0])
                                        setdays_dic[day]['total_hour'] += merged_dic[mo]['total_hour']
                                        setdays_dic[day]['nb_art'] += merged_dic[mo]['quantite']
                                        setdays_dic[day]['mos'].append(mo)
                                        ignore.append(mo)
                                    elif merged_dic[mo]['deadline'] >= 0:
                                        if merged_dic[mo]['deadline'] < setdays_dic[day]['deadline'] + 14:
                                            merged_dic[mo]['date_planned'] = day + ' 00:00:00'
                                            merged_dic[mo]['total_hour'] = intSec2floatTime(self.get_chrono(dataone=merged_dic[mo])[0])
                                            setdays_dic[day]['total_hour'] += merged_dic[mo]['total_hour']
                                            setdays_dic[day]['nb_art'] += merged_dic[mo]['quantite']
                                            setdays_dic[day]['mos'].append(mo)
                                            ignore.append(mo)

        for _ in range(0, 6):
            for i in range(0, len(setdays_dic) - 01):
                j1 = list(setdays_dic.keys())[i]
                j2 = list(setdays_dic.keys())[i + 01]
                jour1 = datetime.strptime(j1 + ' 00:00:00',
                        '%Y-%m-%d %H:%M:%S')
                jour2 = datetime.strptime(j2 + ' 00:00:00',
                        '%Y-%m-%d %H:%M:%S')
                if setdays_dic[j1]['total_hour'] \
                    + setdays_dic[j2]['total_hour'] \
                    <= setdays_dic[j1]['day_hour']:
                    if jour1.weekday() < jour2.weekday() \
                        and setdays_dic[j1]['day_use'] == True:
                        for mo in setdays_dic[j2]['mos']:
                            if merged_dic[mo]['description'
                                    ].find('npDpc') != -01:
                                pass
                            else:
                                merged_dic[mo]['date_planned'] = j1 + ' 00:00:00'
                                setdays_dic[j1]['total_hour'] += merged_dic[mo]['total_hour']
                                setdays_dic[j2]['total_hour'] -= merged_dic[mo]['total_hour']
                                setdays_dic[j1]['nb_art'] += merged_dic[mo]['quantite']
                                setdays_dic[j2]['nb_art'] -= merged_dic[mo]['quantite']
                                setdays_dic[j1]['mos'].append(mo)
                                setdays_dic[j2]['mos'].remove(mo)
                                for val in setdays_dic[j2]['day_val']:
                                    if val not in setdays_dic[j1]['day_val']:
                                        setdays_dic[j1]['day_val'].append(val)
        printt = ""
        for day in setdays_dic:
            printt += "Calendar "+ str(day)+ " deadline "+ str(setdays_dic[day]["deadline"])+"\n"
            printt += "    "+str(setdays_dic[day]["day_val"])+"\n"
            printt += "    "+str(setdays_dic[day]["mos"])+"\n"
            printt += "    "+str(setdays_dic[day]["total_hour"])+"\n"
            printt += "    "+str(setdays_dic[day]["nb_art"])+"\n"

        raise osv.except_osv("Erreur!", printt)
        # Enregister dans la base les nouvelles date et heure total


        # envoyer vers date des restes
        # # recherche date

        prod_srh1 = prod_obj.search(cr, uid, [('date_planned', '>=',
                                    self.date_debut + ' 00:00:00'),
                                    ('date_planned', '<=',
                                    self.date_fin + ' 03:00:00'),
                                    ('description', 'not like', 'npDpc'
                                    ), ('state', '=', 'draft')])

        # # vers date reste

        for p in prod_obj.browse(cr, uid, prod_srh1, context=context):
            prod_obj.write(cr, uid, [p['id']],{'date_planned': self.date_rest + ' 00:00:00'})


        for day in setdays_dic:
            for moid in setdays_dic[day]['mos']:

                #raise osv.except_osv("Erreur!", day)
                j = datetime.strptime(day + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
                srh = prod_obj.search(cr, uid, [('name', '=', moid)])
                bro = prod_obj.browse(cr, uid, srh or False, context=context)
                for b in bro:
                    prod_obj.write(cr, uid, [b['id']],{'date_planned': j })
                                    #'total_hour': intSec2floatTime(self.get_chrono(dataone=merged_dic[moid])[0])})
                    raise osv.except_osv("Erreur!", (b.name,b.date_planned, merged_dic[moid]['total_hour'], merged_dic[moid]['deadline']))
        return True