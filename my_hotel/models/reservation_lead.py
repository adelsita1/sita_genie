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
            'rate',
            'date of reservation',
            "number of adults",
            "number of children"

        ]
        list_reservation = reservation_ai.extract_information(self.reservation_data, categories)
        html_content="<ul>"
        for category,value in list_reservation.items():
            print(f"category: {category}, value: {value}")
            not_found = '"Not found",'
            if value.lower() == not_found.lower() or value.lower() in not_found.lower():
                continue
            html_content+=f"<li><h3><strong>{category.replace("_"," ").title()} </strong> : {value}</h3></li>"
        html_content+=f"</ul>"

        self.description=html_content
