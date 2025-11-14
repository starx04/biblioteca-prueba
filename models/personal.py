# -*- coding: utf-8 -*-

from odoo import models, fields


class Personal(models.Model):
	_name = 'biblioteca.personal'
	_description = 'Personal de la biblioteca'

	name = fields.Char(string='Nombre', required=True)
	role = fields.Char(string='Rol')
	employee_id = fields.Char(string='ID Empleado')
	notes = fields.Text(string='Notas')
