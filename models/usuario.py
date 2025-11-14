# -*- coding: utf-8 -*-

from odoo import models, fields


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
