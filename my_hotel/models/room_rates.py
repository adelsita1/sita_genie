from odoo import fields, models, api


class RoomRates(models.Model):
    _name = 'hotel.room.rate'
    _description = 'Hotel Room Rates'

    name = fields.Many2one('hotel.room.type',required=True)
    occupancy=fields.Selection([
        ("single", "Single"),
        ("double", "Double"),
        ("triple", "Triple"),
        ("4 adults", "4 Adults"),
        ("5 adults", "5 Adults"),
        ("6 adults", "6 Adults"),
        ("7 adults", "7 Adults"),
        ("8 adults", "8 Adults"),
    ],requried=True,default="single",string="Occupancy (\"Adults\")")
    meal_type=fields.Selection([
        ("bed_only","Bed Only"),
        ("bed_breakfast","Bead and Breakfast"),
        ("half_board" ,"Half Board"),
        ("all_inclusive_soft","All Inclusive Soft"),
        ("all_inclusive_hard","All Inclusive Hard")],default="bed_only",string="Meal Type"
        )
    date_from = fields.Date(required=True,string="Date From")
    date_to = fields.Date(required=True,string="Date To")

    rate_egp = fields.Float(string="Rate For Egyptians EGP" ,required=True)
    rate_usd = fields.Float(string="Rate For Foreigners USD",required=True)


