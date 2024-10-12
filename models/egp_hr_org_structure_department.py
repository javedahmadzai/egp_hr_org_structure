from odoo import fields, models, api
from random import randint
from odoo.exceptions import ValidationError


def _get_default_color(self):
    return randint(1, 11)


class InheritedDepartment(models.Model):
    _inherit = "hr.department"

    organization_year = fields.Char(string='Creation Year')
    code = fields.Char(string='Code')
    color = fields.Integer('Color Index', invisible=True, default=_get_default_color)
    egp_tashkil_id = fields.Many2one('egp.tashkil', string='Tashkil', invisible=True)

    _sql_constraints = [
        ('name_uniq', 'unique (code)', "Department code must be unique!!!"),
    ]
