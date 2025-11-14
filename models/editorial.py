# -*- coding: utf-8 -*-

from odoo import models, fields


class Editorial(models.Model):
	_name = 'biblioteca.editorial'
	_description = 'Editorial'

	name = fields.Char(string='Nombre', required=True)
	address = fields.Char(string='Dirección')
	phone = fields.Char(string='Teléfono')
	email = fields.Char(string='Email')
	book_ids = fields.One2many('biblioteca.libro', 'editorial_id', string='Libros')
