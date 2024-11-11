from odoo import api, fields, models
from odoo.tools import float_compare


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    po_versions_count = fields.Integer(compute='compute_po_versions_count')

    def button_confirm(self):
        for order in self:
            # Check for changes and create version if needed before confirmation
            if order._has_changes_from_last_version():
                order.create_po_version()

            # Now confirm the order
            res = super(PurchaseOrder, order).button_confirm()
        return res

    def po_versions_action(self):
        return {
            'name': 'Po Versions',
            'view_mode': 'tree,form',
            'res_model': 'po.version',
            'type': 'ir.actions.act_window',
            'domain': [('purchase_order_id', '=', self.id)],
        }

    def compute_po_versions_count(self):
        for rec in self:
            versions = self.env['po.version'].search([('purchase_order_id', '=', rec.id)])
            rec.po_versions_count = len(versions)

    def _get_tracked_fields(self):
        """Returns list of fields to track changes"""
        return [
            'partner_id', 'partner_ref', 'currency_id',
            'date_approve', 'date_planned',
        ]

    def _get_last_version(self):
        """Get the last version record for this PO"""
        return self.env['po.version'].search([
            ('purchase_order_id', '=', self.id)
        ], order='create_date DESC, id DESC', limit=1)

    def _has_changes_from_last_version(self):
        """Check if current PO has changes compared to last version"""
        last_version = self._get_last_version()
        if not last_version:
            return True

        # Check main fields changes
        for field in self._get_tracked_fields():
            current_value = self[field].id if self[field] and hasattr(self[field], 'id') else self[field]
            last_value = last_version[field].id if last_version[field] and hasattr(last_version[field], 'id') else \
            last_version[field]
            if current_value != last_value:
                return True

        # Check order lines changes
        current_lines = self.order_line.sorted(lambda l: (l.product_id.id, l.price_unit))
        version_lines = last_version.order_line.sorted(lambda l: (l.product_id.id, l.price_unit))

        if len(current_lines) != len(version_lines):
            return True

        for current_line, version_line in zip(current_lines, version_lines):
            # Compare basic product info
            if current_line.product_id != version_line.product_id:
                return True

            # Compare line fields
            line_fields = ['product_qty', 'price_unit', 'name', 'qty_received', 'qty_invoiced']
            for field in line_fields:
                if current_line[field] != version_line[field]:
                    return True

            # Compare taxes
            if set(current_line.taxes_id.ids) != set(version_line.taxes_id.ids):
                return True

            # Compare computed fields
            computed_fields = ['price_subtotal', 'price_total', 'price_tax']
            for field in computed_fields:
                if float_compare(current_line[field], version_line[field], precision_digits=2) != 0:
                    return True

        return False

    def create_po_version(self):
        # Skip if already in purchase state (ignore post-confirmation changes)
        if self.state == 'purchase':
            return

        # Get next version number
        last_version = self._get_last_version()
        version_number = 1
        if last_version:
            try:
                version_number = int(last_version.name.replace('V', '')) + 1
            except ValueError:
                version_number = len(self.env['po.version'].search([
                    ('purchase_order_id', '=', self.id)
                ])) + 1

        # Check if version already exists
        existing_version = self.env['po.version'].search([
            ('purchase_order_id', '=', self.id),
            ('name', '=', f"V{version_number}")
        ], limit=1)

        if existing_version:
            return

        # Create new version
        version_vals = {
            'name': f"V{version_number}",
            'purchase_order_id': self.id,
            'partner_id': self.partner_id.id,
            'partner_ref': self.partner_ref,
            'date_approve': self.date_approve,
            'date_planned': self.date_planned,
            'currency_id': self.currency_id.id,
            'order_line': [],
        }

        # Prepare order lines
        for line in self.order_line:
            version_vals['order_line'].append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'product_qty': line.product_qty,
                'qty_received': line.qty_received,
                'qty_invoiced': line.qty_invoiced,
                'price_unit': line.price_unit,
                'taxes_id': [(6, 0, line.taxes_id.ids)],
                'price_subtotal': line.price_subtotal,
                'price_total': line.price_total,
                'price_tax': line.price_tax,
            }))

        self.env['po.version'].create(version_vals)

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        # Create initial version for new POs
        for record in res:
            record.create_po_version()
        return res

    @api.onchange('partner_id', 'partner_ref', 'currency_id', 'date_approve',
                  'date_planned', 'order_line', 'order_line.product_id',
                  'order_line.product_qty', 'order_line.price_unit',
                  'order_line.taxes_id')
    def _onchange_version_fields(self):
        if self.state != 'purchase' and not self._context.get('creating_version'):
            if self._has_changes_from_last_version():
                self.with_context(creating_version=True).create_po_version()

    def write(self, vals):
        res = super().write(vals)
        # Only create versions for changes before purchase state
        if 'order_line' in vals and self.state != 'purchase':
            if self._has_changes_from_last_version():
                self.with_context(creating_version=True).create_po_version()
        return res