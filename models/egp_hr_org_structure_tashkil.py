from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class Tashkil(models.Model):
    _name = 'egp.tashkil'
    _description = 'Tashkil Model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "creation_year desc, sequence_number desc"

    name = fields.Char(string='Name', Tracking=True)
    creation_year = fields.Integer(string='Tashkil Year', placeholder='Enter Creation Year', Tracking=True)
    sequence_number = fields.Char(string='Sequence Number', readonly=True, required=True, copy=False, default=
    lambda self: _("New"))
    image = fields.Image(string='Image')
    description = fields.Text(string='Description', Tracking=True)
    job_position_ids = fields.One2many('tashkil.line', 'egp_tashkil_id', string='Job Details')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('process', 'Under process'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ], string='Status', default='draft', Tracking=True)

    # Add attachment of document
    attachment = fields.Binary(string='Attachment', attachment=True)
    filename = fields.Char(string='Filename')

    # Tashkil line fields
    department_new_ids = fields.One2many('tashkil.line', 'egp_tashkil_id', string='New departments')
    position_new_ids = fields.One2many('tashkil.line', 'egp_tashkil_position_id', string='Newly Created Positions')
    department_change_ids = fields.One2many('tashkil.line', 'change_department_id', string="Change Department")

    # for printing the display of tashkil activeness check value in xml report
    def get_tashkil_activeness_check_label(self):
        label_mapping = {
            'draft': 'Draft',
            'process': 'Under process',
            'active': 'Active',
            'archived': 'Archived'
        }
        return label_mapping.get(self.state, '')

    def copy(self, default=None):
        if default is None:
            default = {}
        default['name'] = f"{self.name} -copy"

        # Duplicate the main record
        new_tashkil = super(Tashkil, self).copy(default=default)

        # Get the next sequence number and assign it to the duplicated record
        sequence_number = self.env['ir.sequence'].next_by_code('egp.tashkil')
        new_tashkil.sequence_number = sequence_number
        return new_tashkil

    @api.constrains('creation_year')
    def _check_creation_year(self):
        for record in self:
            if record.creation_year < 1300 or record.creation_year > 1500:
                raise ValidationError("Creation Year must be between 1300 and 1500.")

    @api.model
    def create(self, vals):
        vals['sequence_number'] = self.env['ir.sequence'].next_by_code('egp.tashkil')
        record = super(Tashkil, self).create(vals)
        # Change Tashkil state to 'process'
        record.state = 'process'
        return record

    # Add constraint for attachment to accept just PDF and DOCX file formats
    @api.constrains('attachment', 'filename')
    def _check_allowed_extensions(self):
        for record in self:
            if record.attachment and record.filename:
                extension = record.filename.split('.')[-1].lower()
                if extension not in ['pdf', 'docx']:
                    raise ValidationError(
                        f"Only PDF and Microsoft Word (DOCX) files are allowed. '{record.filename}' is not a valid file type.")

    active = fields.Boolean(default=True)

    changed_department_job_positions = fields.One2many(
        'tashkil.line', 'position_department_id',
        string='Changed Department')

    cancelled_job_positions = fields.One2many(
        'tashkil.line', 'cancel_position_id',
        string='Cancelled')

    cancelled_department_ids = fields.One2many(
        'tashkil.line', 'cancel_department',
        string="Cancel Department"
    )
    cancelled_department_name = fields.Char(related=cancelled_department_ids.name)

    def approve(self):
        for rec in self:
            # Set the state to 'active'
            rec.state = 'active'

            # Create new departments from `department_new_ids`
            for new_dep in rec.department_new_ids:
                dep = {
                    'name': new_dep.name,
                    'code': new_dep.department_code,
                    'organization_year': new_dep.department_creation_year if new_dep.department_creation_year else False,
                    'parent_id': new_dep.parent_department_id.id if new_dep.parent_department_id else False,
                }

                # Create the new department
                newly_created_department = self.env['hr.department'].create(dep)
                new_dep.department_id = newly_created_department.id

            # Create new positions from `position_new_ids`
            for new_position in rec.position_new_ids:
                position = {
                    'name': new_position.position_name,
                    'code': new_position.position_code,
                    'position_rank': new_position.position_rank,
                    # 'work_location_id': new_position.position_work_location,
                    'work_location_id': new_position.position_work_location.id if new_position.position_work_location else False,
                    'department_id': new_position.department_id.id if new_position.department_id else False,
                    'no_of_recruitment': new_position.position_no_of_recruit,
                    'creation_year': new_position.creation_year if new_position.creation_year else False,
                }
                # Create the new position in hr.job model
                newly_created_position = self.env['hr.job'].create(position)

            # Update job positions with new departments from `changed_department_job_positions`
            for change in rec.changed_department_job_positions:
                job_position = self.env['hr.job'].browse(change.job_id.id)
                if job_position:
                    job_position.write({
                        'department_id': change.position_change_department.id if change.position_change_department else False,
                    })

            # Update cancelled job positions to set position_check field to 'position_passive'
            for cancelled_job in rec.cancelled_job_positions:
                job_position = self.env['hr.job'].browse(cancelled_job.job_id.id)
                if job_position:
                    job_position.write({
                        'position_activeness_check': 'position_passive',
                    })

            # Archived cancelled departments to set department_active field to False
            for cancelled_dep in rec.cancelled_department_ids:
                department = self.env['hr.department'].browse(cancelled_dep.department_id.id)
                if department:
                    department.active = False

            # Update or change the parent of departments from `department_change_ids`
            for change in rec.department_change_ids:
                department = self.env['hr.department'].browse(change.department_id.id)
                if department:
                    department.write({
                        'parent_id': change.parent_department_id.id if change.parent_department_id else False,
                    })

    previous_tashkils = fields.One2many(
        'egp.tashkil', 'related_tashkil_id', string="Previous Tashkils", compute='_compute_previous_tashkils',
        store=False)

    related_tashkil_id = fields.Many2one('egp.tashkil', string="Related Tashkil")

    @api.depends('creation_year')
    def _compute_previous_tashkils(self):
        for record in self:
            # Fetch previous Tashkils based on the creation year being less than the current record's year
            previous_tashkils = self.env['egp.tashkil'].search([
                ('creation_year', '<', record.creation_year)
            ])
            record.previous_tashkils = previous_tashkils

    # set the Tashkil state to 'archive' when the Tashkil is Archived
    def archive(self):
        for rec in self:
            # Set the state to 'archived'
            rec.state = 'archived'

    # check the description field lenght
    @api.constrains('description')
    def _check_description_length(self):
        max_length = 1000
        for record in self:
            if record.description and len(record.description) > max_length:
                raise ValidationError(
                    f"The description field cannot exceed {max_length} characters. The current length is {len(record.description)} characters.")

    # prevent deletion when the state is activated
    def unlink(self):
        for rec in self:
            if rec.state not in ['draft', 'process']:
                raise ValidationError(_("WARNING....\n Deletion is possible only in Draft or Process State"))
            return super(Tashkil, self).unlink()
