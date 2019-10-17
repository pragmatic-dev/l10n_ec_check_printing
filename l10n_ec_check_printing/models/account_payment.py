# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class account_payment(models.Model):
    _inherit = "account.payment"

    check_amount_in_words_ec = fields.Char(string='Importe en letras', compute='_compute_importe_letras')


    @api.one
    @api.depends('check_amount_in_words')
    def _compute_importe_letras(self):
        text = self.check_amount_in_words.split(' and ')[0]
        self.check_amount_in_words_ec = text + ' con ' + str(int((self.amount-int(self.amount))*100)) + '/100'

    @api.multi
    def do_print_checks(self):
        if self:
            check_layout = self[0].company_id.account_check_printing_layout
            # A config parameter is used to give the ability to use this check format even in other countries than US, as not all the localizations have one
            if check_layout != 'disabled' and (self[0].journal_id.company_id.country_id.code == 'EC' or bool(self.env['ir.config_parameter'].sudo().get_param('account_check_printing_force_ec_format'))):
                self.write({'state': 'sent'})
                return self.env.ref('l10n_ec_check_printing.%s' % check_layout).report_action(self)
        return super(account_payment, self).do_print_checks()

    move_line_rel_ids = fields.Many2many('account.move.line', 'payment_move_line_rel','payment_id','move_line_id', compute='_compute_move_line_rel_ids')

    @api.depends('reconciled_invoice_ids')
    def _compute_move_line_rel_ids(self):
        move_lines = []
        for payment in self:
            print(payment.reconciled_invoice_ids)
            for inv in payment.reconciled_invoice_ids:
                move_ids = []
                for reconcile in inv.payment_move_line_ids:
                    move_ids += [reconcile.move_id.id]
                pml = self.env['account.move.line'].search([('move_id', 'in', move_ids)])

                for pmt_move_line in pml:
                    # Valida si es una retefuente
                    if pmt_move_line.credit >0:
                        move_lines += [pmt_move_line.id]
        self.move_line_rel_ids = move_lines