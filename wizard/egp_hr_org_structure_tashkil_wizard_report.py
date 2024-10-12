from odoo import fields, models, api, _
from odoo.exceptions import UserError


class TashkilWizardReport(models.TransientModel):
    _name = "tashkil.wizard.report"
    _description = "Print Tashkil Selective Report"

    tashkil_ids = fields.Many2many('egp.tashkil', string='Tashkil')

    # if user does not select any Tashkil
    def generate_tashkil_wizard_report(self):
        # Check if any Tashkil records are selected
        if not self.tashkil_ids:
            raise UserError(_('Please select at least one Tashkil record before generating the report.'))

        # Preparing data for the report
        data = {
            'tashkil_ids': self.tashkil_ids.ids
        }
        return self.env.ref('egp_hr_org_structure.tashkil_wizard_report_action').report_action(self, data=data)

    # close wizard popup
    def action_cancel(self):
        return {
            'effect': {
                'fadeout': 'fast',
                'message': "Closed!!! \n Successfully Closed Wizard 😡",
                'type': 'rainbow_man',
            }
        }