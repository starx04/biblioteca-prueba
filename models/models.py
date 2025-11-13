# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date


class Autor(models.Model):
	_name = 'biblioteca.autor'
	_description = 'Autor de libros'

	name = fields.Char(string='Nombre', required=True)
	bio = fields.Text(string='Biografía')
	book_ids = fields.Many2many('biblioteca.libro', string='Libros', relation='biblioteca_libro_autor_rel', column1='autor_id', column2='libro_id')


class Editorial(models.Model):
	_name = 'biblioteca.editorial'
	_description = 'Editorial'

	name = fields.Char(string='Nombre', required=True)
	address = fields.Char(string='Dirección')
	phone = fields.Char(string='Teléfono')
	email = fields.Char(string='Email')
	book_ids = fields.One2many('biblioteca.libro', 'editorial_id', string='Libros')


class Usuario(models.Model):
	_name = 'biblioteca.usuario'
	_description = 'Usuario / Lector'

	name = fields.Char(string='Nombre', required=True)
	email = fields.Char(string='Email')
	phone = fields.Char(string='Teléfono')
	active = fields.Boolean(string='Activo', default=True)
	member_since = fields.Date(string='Miembro desde')
	loan_ids = fields.One2many('biblioteca.prestamo', 'usuario_id', string='Préstamos')
	fine_ids = fields.One2many('biblioteca.multa', 'usuario_id', string='Multas')


class Personal(models.Model):
	_name = 'biblioteca.personal'
	_description = 'Personal de la biblioteca'

	name = fields.Char(string='Nombre', required=True)
	role = fields.Char(string='Rol')
	employee_id = fields.Char(string='ID Empleado')
	notes = fields.Text(string='Notas')


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


