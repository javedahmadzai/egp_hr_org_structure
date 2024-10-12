from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from lxml import etree


class InheritedJob(models.Model):
    _inherit = "hr.job"
    _rec_name = 'name'

    name = fields.Char(string='Job Position', tracking=True, required=True, index='trigram', translate=True)
    creation_year = fields.Integer(string='Creation Year', limit=4, tracking=True, )
    code = fields.Char(string='Code', tracking=True, )
    no_of_recruitment = fields.Integer(string='Target', copy=False,
                                       help='Number of new employees you expect to recruit.', default=1)
    position_activeness_check = [
        ('position_active', 'Active'),
        ('position_passive', 'In-Active'),
        ('position_under_process', 'In-Progress'),
    ]

    position_activeness_check = fields.Selection(
        selection=position_activeness_check,
        string='Position Status',
        required=True,
        tracking=True,
        default='position_active', widget='selection')

    # for printing the display value in xml report
    def get_position_activeness_check_label(self):
        label_mapping = {
            'position_active': 'Active',
            'position_passive': 'In-Active',
            'position_under_process': 'In-Progress'
        }
        return label_mapping.get(self.position_activeness_check, '')

    position_rank = fields.Selection([
        ('out_of_rank', 'Out of Rank'),
        ('superior_rank', 'مافوق رتبه'),
        ('1st_batch', '1'),
        ('2nd_batch', '2'),
        ('3rd_batch', '3'),
        ('4th_batch', '4'),
        ('5th_batch', '5'),
        ('6th_batch', '6'),
        ('7th_batch', '7'),
        ('8th_batch', '8')], string="Position Rank", default='3rd_batch', required=True,
        tracking=True)

    # for printing the display value in xml report
    def get_position_rank_choices_label(self):
        label_mapping = {
            'out_of_rank': 'Out of Rank',
            'superior_rank': 'مافوق رتبه',
            '1st_batch': '1',
            '2nd_batch': '2',
            '3rd_batch': '3',
            '4th_batch': '4',
            '5th_batch': '5',
            '6th_batch': '6',
            '7th_batch': '7',
            '8th_batch': '8',
        },
        return label_mapping.get(self.position_rank, '')

    def get_position_rank(self):
        label_mapping = {
            ('out_of_rank', 'Out of Rank'),
            ('superior_rank', 'مافوق رتبه'),
            ('1st_batch', '1'),
            ('2nd_batch', '2'),
            ('3rd_batch', '3'),
            ('4th_batch', '4'),
            ('5th_batch', '5'),
            ('6th_batch', '6'),
            ('7th_batch', '7'),
            ('8th_batch', '8')
        },
        return label_mapping.get(self.position_rank, '')

    color = fields.Integer(string='Color')
    work_location_id = fields.Many2one('hr.work.location', string='Work Location',
                                       default=lambda self: self.env['hr.work.location'].search([], limit=1, offset=2)[
                                           0])
    website_published = fields.Boolean(help='Set if the application is published on the website of the company.',
                                       groups="base.group_erp_manager")
    job_details = fields.Html(
        'Process Details',
        translate=True,
        help="Complementary information that will appear on the job submission page",
        sanitize_attributes=False,
        default="""
                <span class="text-muted small">Time to Answer</span>
                <h6>2 open days</h6>
                <span class="text-muted small">Process</span>
                <h6>1 Phone Call</h6>
                <h6>1 Onsite Interview</h6>
                <span class="text-muted small">Days to get an Offer</span>
                <h6>4 Days after Interview</h6>
            """,
        groups="base.group_erp_manager, hr.group_hr_user,egp_hr_recruitment.group_recruitment_amir,"
               "egp_hr_recruitment.group_recruitment_Karshanas")

    report_to_id = fields.Many2one('hr.job', string='Report To')
    custom_job_description = fields.Html(
        string='Job Description',
        default='''
               <h6>Job Objective:</h6> <br/> <br/> 
               <h6>Specialized Duties:</h6> <br/> <br/> 
               <h6>Managerial Duties:</h6> <br/> <br/> 
               <h6>Coordination Duties:</h6> <br/> <br/> 
               <h6>Employment Conditions (Education Level and Work Experience):</h6>
           '''
    )
    description = fields.Html(
        string='Job Summary',
        sanitize_attributes=False,
        default='هدف و توضیحات خلاصه در مورد بست مذکور!')

    department_id = fields.Many2one('hr.department', string='Department', check_company=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    _sql_constraints = [
        ('unique_job_position_name', 'unique(name, company_id, department_id)',
         'The name of the job position must be unique per department in company!'),
    ]

    @api.constrains('creation_year')
    def _check_creation_year(self):
        for record in self:
            if record.creation_year < 1300 or record.creation_year > 1500:
                raise ValidationError("Creation Year must be between 1300 and 1500.")

    # check the custom job description field length
    @api.constrains('custom_job_description')
    def _check_description_length(self):
        max_length = 2000
        for record in self:
            if record.description and len(record.description) > max_length:
                raise ValidationError(
                    f"The description field cannot exceed {max_length} characters. The current length is {len(record.description)} characters.")

    # prevent deletion when position state is active
    def unlink(self):
        for rec in self:
            if rec.position_activeness_check not in ['position_passive', 'position_under_process']:
                raise ValidationError(_("WARNING....\n Deletion is possible only in In-Active or In-Progress State"))
            return super(InheritedJob, self).unlink()
