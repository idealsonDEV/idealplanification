# -*- coding: utf-8 -*-
{
    'name': "idealplanitication",

    'summary': """
        Planification des ordres de fabrications en fonction des dates de livraison""",

    'description': """
        Planification des ordres de fabrications en fonction des dates de livraison
            - Chronometre des nomenclature
            - Configuration des journées
            - Vues des ordres planifiées
    """,

    'author': "Ratsimanandoka Andriamahery Idéalison",
    'website': "https://www.mim-madagascar.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Manufacturing',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'templates.xml',
        'views/chrono.xml',
        'views/setdays.xml',
        'views/cycle.xml',
        #'views/visual.xml',
    ],
    # only loaded in demonstration mode
    #'demo': [
    #    'demo.xml',
    #],
}