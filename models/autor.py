# -*- coding: utf-8 -*-

from odoo import models, fields


class Autor(models.Model):
	_name = 'biblioteca.autor'
	_description = 'Autor de libros'

	name = fields.Char(string='Nombre', required=True)
	bio = fields.Text(string='Biografía')
	book_ids = fields.Many2many('biblioteca.libro', string='Libros', relation='biblioteca_libro_autor_rel', column1='autor_id', column2='libro_id')
