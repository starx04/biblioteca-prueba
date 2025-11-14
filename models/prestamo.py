# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class Prestamo(models.Model):
	_name = 'biblioteca.prestamo'
	_description = 'Préstamo de libro'

	name = fields.Char(string='Referencia', readonly=True)
	libro_id = fields.Many2one('biblioteca.libro', string='Libro', required=True)
	usuario_id = fields.Many2one('biblioteca.usuario', string='Usuario', required=True)
	personal_id = fields.Many2one('biblioteca.personal', string='Procesado por')
	fecha_prestamo = fields.Date(string='Fecha préstamo', default=fields.Date.context_today)
	fecha_devolucion_estimada = fields.Date(string='Fecha devolución estimada')
	fecha_devolucion_real = fields.Date(string='Fecha devolución real')
	state = fields.Selection([('borrowed', 'Prestado'), ('returned', 'Devuelto'), ('overdue', 'Retrasado')], string='Estado', default='borrowed')
	multa_amount = fields.Float(string='Multa calculada', compute='_compute_multa', store=True)
	multa_ids = fields.One2many('biblioteca.multa', 'prestamo_id', string='Multas')

	DAILY_FEE = 1.0  # tarifa por día de retraso (puede adaptarse)

	@api.model
	def create(self, vals):
		# generar una referencia simple
		if not vals.get('name'):
			seq = self.env['ir.sequence'].sudo().next_by_code('biblioteca.prestamo') if self.env.ref('biblioteca_prueba.biblioteca_prestamo_seq', raise_if_not_found=False) else None
			vals['name'] = seq or 'PREST-' + (fields.Date.context_today(self) or date.today()).strftime('%Y%m%d')
		loan = super(Prestamo, self).create(vals)
		return loan

	@api.depends('fecha_devolucion_estimada', 'fecha_devolucion_real')
	def _compute_multa(self):
		today = fields.Date.context_today(self)
		for rec in self:
			if rec.fecha_devolucion_estimada:
				end_date = rec.fecha_devolucion_real or today
				# calcular días de retraso
				try:
					days_overdue = (fields.Date.from_string(end_date) - fields.Date.from_string(rec.fecha_devolucion_estimada)).days
				except Exception:
					days_overdue = 0
				days_overdue = days_overdue if days_overdue > 0 else 0
				rec.multa_amount = days_overdue * rec.DAILY_FEE
				# actualizar estado
				if rec.fecha_devolucion_real:
					rec.state = 'returned'
				else:
					rec.state = 'overdue' if days_overdue > 0 else 'borrowed'
			else:
				rec.multa_amount = 0.0

	@api.constrains('libro_id')
	def _check_available_copies(self):
		for rec in self:
			if rec.libro_id and rec.libro_id.available_copies <= 0:
				raise ValidationError('No hay copias disponibles para el libro seleccionado.')
