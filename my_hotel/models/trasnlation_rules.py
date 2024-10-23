from odoo import fields, models, api


class TranslationRules(models.Model):
    _name = 'hotel.translation.rules'
    _description = 'Translation Rule'

    old_text = fields.Char(string="Old Text",required=True)
    lang=fields.Many2one('res.lang', string="Language",required=True)
    iso_code=fields.Char(string="Iso Code",related="lang.iso_code",store=True)
    new_text = fields.Char(string="New Text",required=True)


    @api.model
    def replace_words(self, given_text,lang_code):
        print("given_text",given_text)
        print("lang_code",lang_code)
        all_rules=self.env['hotel.translation.rules'].search([("iso_code","=",lang_code)])
        print("all_rules",all_rules)
        if all_rules:
            for rule in all_rules:
                if rule.old_text.lower() in given_text.lower():
                    given_text=given_text.lower().strip().replace(rule.old_text.lower(),rule.new_text.title())
                    print("rule.old_text",rule.old_text)
                    print("rule.new_text",rule.new_text)
                    print("given_text",given_text)
        print("given text after replacement",given_text)
        return given_text


