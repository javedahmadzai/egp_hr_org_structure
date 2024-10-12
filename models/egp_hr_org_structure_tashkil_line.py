from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class TashkilLine(models.Model):
    _name = "tashkil.line"

    name = fields.Char(string="Name")
    position_name = fields.Char(string="Position Name")
    department_id = fields.Many2one('hr.department', string='Department', store=True)
    position_code = fields.Char(string='Code')
    position_work_location = fields.Many2one('hr.work.location', string='Work Location')
    position_no_of_recruit = fields.Integer(string="Target", help='Number of new employees you expect to recruit.')
    code = fields.Char(string='Code')
    cancel_dep_code = fields.Char(related='department_id.code', string='Code')
    cancel_dep_year = fields.Char(related='department_id.organization_year', string='Code')
    department_code = fields.Char(string='Code')
    department_creation_year = fields.Integer(related='egp_tashkil_id.creation_year', string='Creation Year')
    position_rank = fields.Selection([
        ('out_of_rank', 'خارج رتبه'),
        ('superior_rank', 'مافوق رتبه'),
        ('1st_batch', '1'),
        ('2nd_batch', '2'),
        ('3rd_batch', '3'),
        ('4th_batch', '4'),
        ('5th_batch', '5'),
        ('6th_batch', '6'),
        ('7th_batch', '7'),
        ('8th_batch', '8'),
    ], string='Position Rank')

    position_status = fields.Selection([
        ('newly_created', 'Newly Created'),
        ('carried_from_last_year', 'Carried over from last year'),
        ('department_changed', 'Department changed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', required=True, default='newly_created')

    no_to_recruit = fields.Integer(string="No of vacancies", default=1)
    change_department_id = fields.Many2one('egp.tashkil', string='New Department')
    egp_tashkil_id = fields.Many2one('egp.tashkil', string='Tashkil', invisible=True)
    egp_tashkil_position_id = fields.Many2one('egp.tashkil', string='Tashkil', invisible=True)
    creation_year = fields.Integer(string='Creation Year', related='egp_tashkil_position_id.creation_year')
    parent_department_id = fields.Many2one('hr.department', string="Parent")

    # for change position
    job_id = fields.Many2one('hr.job', string='Job Position')
    position_department_id = fields.Many2one('egp.tashkil', string='Tashkil', invisible=True)
    position_change_department = fields.Many2one('hr.department', string='New Department')
    change_position_department_id = fields.Many2one('hr.department', string='Current Department',
                                                    related='job_id.department_id', store=True)
    change_position_code = fields.Char(related='job_id.code', string='Code')
    change_position_creation_year = fields.Integer(related='job_id.creation_year', string='Creation Year')
    change_position_rank = fields.Selection(related='job_id.position_rank', string='Position Rank',
                                            store=True)

    # for Cancel position
    cancel_position_id = fields.Many2one('egp.tashkil', string='Tashkil', invisible=True)
    position_check = fields.Selection([
        ('position_active', 'Active'),
        ('position_passive', 'In-Active'),
        ('position_under_process', 'In-Progress'),
    ], string='Status', required=True, default='position_passive')

    # for Cancel departments
    cancel_department = fields.Many2one('egp.tashkil', string="Cancel Department", invisible=True)
    department_active = fields.Boolean(string="Active", default=False)

    # Printing the display value of position status in xml report
    def get_position_status_label(self):
        label_mapping = {
            'newly_created': 'Newly Created',
            'carried_from_last_year': 'Carried over from last year',
            'department_changed': 'Department changed',
            'cancelled': 'In-Cancelled'
        }
        return label_mapping.get(self.position_status, '')

    # for printing the display of position activeness value in xml report
    def get_position_activeness_check_label(self):
        label_mapping = {
            'position_active': 'Active',
            'position_passive': 'In-Active',
            'position_under_process': 'In-Progress'
        }
        return label_mapping.get(self.position_activeness_check, '')

    # for printing the display value of position rank in xml report
    def get_position_position_rank_label(self):
        label_mapping = {
            'out_of_rank': 'خارج رتبه',
            'superior_rank': 'مافوق رتبه',
            '1st_batch': '1',
            '2nd_batch': '2',
            '3rd_batch': '3',
            '4th_batch': '4',
            '5th_batch': '5',
            '6th_batch': '6',
            '7th_batch': '7',
            '8th_batch': '8',
        }
        return label_mapping.get(self.position_rank, '')

    # for printing the display value of change position rank in xml report
    def get_change_position_rank_label(self):
        label_mapping = {
            'out_of_rank': 'خارج رتبه',
            'superior_rank': 'مافوق رتبه',
            '1st_batch': '1',
            '2nd_batch': '2',
            '3rd_batch': '3',
            '4th_batch': '4',
            '5th_batch': '5',
            '6th_batch': '6',
            '7th_batch': '7',
            '8th_batch': '8',
        }
        return label_mapping.get(self.change_position_rank, '')
