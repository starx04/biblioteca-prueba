# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class Usuario(models.Model):
	_name = 'biblioteca.usuario'
	_description = 'Usuario / Lector'

	# Datos personales separados
	first_name = fields.Char(string='Nombre', required=True)
	last_name = fields.Char(string='Apellido', required=True)
	name = fields.Char(string='Nombre completo', compute='_compute_name', store=True)

	cedula = fields.Char(string='Cédula', required=True)
	phone = fields.Char(string='Teléfono')
	email = fields.Char(string='Correo', required=True)

	active = fields.Boolean(string='Activo', default=True)
	member_since = fields.Date(string='Miembro desde')
	loan_ids = fields.One2many('biblioteca.prestamo', 'usuario_id', string='Préstamos')
	fine_ids = fields.One2many('biblioteca.multa', 'usuario_id', string='Multas')

	_sql_constraints = [
		('cedula_unique', 'unique(cedula)', 'La cédula debe ser única.'),
		('email_unique', 'unique(email)', 'El correo electrónico debe ser único.'),
	]

	@api.depends('first_name', 'last_name')
	def _compute_name(self):
		for rec in self:
			rec.name = ((rec.first_name or '') + ' ' + (rec.last_name or '')).strip()

	@api.constrains('cedula')
	def _check_cedula(self):
		for rec in self:
			if not rec.cedula:
				raise ValidationError('La cédula es obligatoria.')
			# validar que la cédula tenga solo dígitos y longitud razonable
			if not re.match(r"^\d{6,12}$", rec.cedula):
				raise ValidationError('La cédula debe contener solo dígitos y tener entre 6 y 12 caracteres.')

	@api.constrains('email')
	def _check_email(self):
		email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
		for rec in self:
			if not rec.email:
				raise ValidationError('El correo es obligatorio.')
			if not re.match(email_regex, rec.email):
				raise ValidationError('El correo electrónico no tiene un formato válido.')

	@api.constrains('phone')
	def _check_phone(self):
		for rec in self:
			if rec.phone:
				# permitir dígitos, espacios, +, -, ()
				if not re.match(r"^[0-9\s\+\-\(\)]{6,20}$", rec.phone):
					raise ValidationError('El teléfono no es válido. Use solo dígitos, espacios y los símbolos + - ( )')

