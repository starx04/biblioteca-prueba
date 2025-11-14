# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Libro(models.Model):
	_name = 'biblioteca.libro'
	_description = 'Libro'

	name = fields.Char(string='Título', required=True)
	isbn = fields.Char(string='ISBN')
	author_ids = fields.Many2many('biblioteca.autor', string='Autores', relation='biblioteca_libro_autor_rel', column1='libro_id', column2='autor_id')
	editorial_id = fields.Many2one('biblioteca.editorial', string='Editorial')
	copies = fields.Integer(string='Copias totales', default=1)
	available_copies = fields.Integer(string='Copias disponibles', compute='_compute_available_copies', store=True)
	description = fields.Text(string='Descripción')

	@api.depends('copies')
	def _compute_available_copies(self):
		for record in self:
			# contar préstamos abiertos para este libro
			open_loans = self.env['biblioteca.prestamo'].search_count([('libro_id', '=', record.id), ('state', 'in', ('borrowed', 'overdue'))])
			record.available_copies = max(0, record.copies - open_loans)
