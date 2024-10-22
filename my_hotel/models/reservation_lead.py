from odoo import fields, models, api
from ..utils.open_ai_helper import PDFQuestionAnswerer

class ReservationLead(models.Model):
    _inherit = "crm.lead"

    nationality = fields.Many2one('res.country', string='Nationality', store=True,
                                  readonly=False)

    reservation_data=fields.Text(string='Reservation Data')

    def get_reservation_data_from_ai(self):
        reservation_ai=PDFQuestionAnswerer()
        categories = [
            'name of room',
            'rate'
        ]
        list_reservation = reservation_ai.extract_information(self.reservation_data, categories)
        for category,value in list_reservation.items():
            print(f"category: {category}, value: {value}")

