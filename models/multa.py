# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date


class Multa(models.Model):
	_name = 'biblioteca.multa'
	_description = 'Multa por préstamo'

	name = fields.Char(string='Referencia')
	prestamo_id = fields.Many2one('biblioteca.prestamo', string='Préstamo', required=True)
	usuario_id = fields.Many2one('biblioteca.usuario', string='Usuario', related='prestamo_id.usuario_id', store=True)
	amount = fields.Float(string='Importe', required=True)
	paid = fields.Boolean(string='Pagada', default=False)
	reason = fields.Text(string='Motivo')

	@api.model
	def create(self, vals):
		if not vals.get('name'):
			vals['name'] = 'MULTA-' + (fields.Date.context_today(self) or date.today()).strftime('%Y%m%d')
		return super(Multa, self).create(vals)
