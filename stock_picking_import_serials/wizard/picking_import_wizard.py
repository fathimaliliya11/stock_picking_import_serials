from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
import io
import csv
import re
import logging

_logger = logging.getLogger(__name__)

try:
    import openpyxl
except Exception:
    openpyxl = None


class StockPickingImportWizard(models.TransientModel):
    _name = 'stock.picking.import.wizard'
    _description = 'Import product serials into picking'

    picking_id = fields.Many2one(
        'stock.picking',
        string='Picking',
        required=True,
        default=lambda self: self.env.context.get('default_picking_id')
    )
    upload_file = fields.Binary('Upload File')
    filename = fields.Char('Filename')
    file_type = fields.Selection(
        [('csv', 'CSV'), ('xlsx', 'XLSX')],
        string='File Type',
        default='xlsx'
    )

    # -------------------------------------------------------------------------
    # Template Download
    # -------------------------------------------------------------------------
    def action_download_template(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/picking_import/download_template?picking_id={self.picking_id.id}&file_type={self.file_type}',
            'target': 'new',
        }

    # -------------------------------------------------------------------------
    # Helpers
    # -------------------------------------------------------------------------
    def _expand_serials(self, value):
        """Expand serial strings into a list: SN001, SN002-SN010."""
        if not value:
            return []
        parts = [p.strip() for p in re.split(r',|;', value) if p.strip()]
        result = []
        for p in parts:
            if '-' in p:
                left, right = p.split('-', 1)
                left, right = left.strip(), right.strip()
                m_left, m_right = re.search(r'(\d+)$', left), re.search(r'(\d+)$', right)
                if m_left and m_right:
                    num_left, num_right = m_left.group(1), m_right.group(1)
                    prefix = left[:m_left.start(1)]
                    start, end = int(num_left), int(num_right)
                    width = max(len(num_left), len(num_right))
                    for i in range(start, end + 1):
                        result.append(f"{prefix}{str(i).zfill(width)}")
                else:
                    result += [left, right]
            else:
                result.append(p)
        return result

    # -------------------------------------------------------------------------
    # Import Logic
    # -------------------------------------------------------------------------
    def action_import(self):
        self.ensure_one()
        if not self.upload_file:
            raise UserError(_("Please upload a file."))

        # Decode file
        file_content = base64.b64decode(self.upload_file)
        rows = []

        # Parse Excel
        if self.filename.endswith(('.xls', '.xlsx')):
            if not openpyxl:
                raise UserError(_("openpyxl is not installed. Please use CSV instead."))
            wb = openpyxl.load_workbook(io.BytesIO(file_content), data_only=True)
            ws = wb.active
            headers = [str(c).strip() if c else '' for c in next(ws.iter_rows(values_only=True))]
            for row in ws.iter_rows(min_row=2, values_only=True):
                if all(v is None for v in row):
                    continue
                row_dict = {headers[i]: (str(v).strip() if v is not None else '') for i, v in enumerate(row)}
                rows.append(row_dict)
        else:
            raise UserError(_("Unsupported file format. Upload XLSX file."))

        StockLot = self.env['stock.lot']
        MoveLine = self.env['stock.move.line']
        Product = self.env['product.product']

        # Remove existing move lines
        self.picking_id.move_line_ids.unlink()

        # Process each row
        for row in rows:
            product_id = str(row.get('ID') or '').strip()
            product_name = str(row.get('Product') or '').strip()
            qty = float(row.get('Quantity') or 0)
            lot_name = str(row.get('Lot / Serial Number(s)') or '').strip()
            exp_date = str(row.get('Expiration Date') or '').strip()

            if not product_id or not qty or not lot_name:
                continue

            # Find product
            product = Product.search([('id', '=', product_id)], limit=1)
            if not product:
                raise UserError(_("Product with name '%s' and id '%s' not found.") % (product_name, product_id))

            # Find corresponding stock move
            move = self.picking_id.move_ids.filtered(lambda m: m.product_id == product)
            if not move:
                raise UserError(_("No stock move found for product %s") % product.display_name)

            # Find or create lot
            lot = StockLot.search([('name', '=', lot_name), ('product_id', '=', product.id)], limit=1)
            if not lot:
                lot_vals = {
                    'name': lot_name,
                    'product_id': product.id,
                    'company_id': self.picking_id.company_id.id,
                }
                if exp_date:
                    lot_vals['expiration_date'] = exp_date
                lot = StockLot.create(lot_vals)
            else:
                if exp_date:
                    lot.write({'expiration_date': exp_date})

            # Create move line
            MoveLine.create({
                'picking_id': self.picking_id.id,
                'move_id': move.id,
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'quantity': qty,
                'lot_id': lot.id,
                'lot_name': lot.name,
                'location_id': move.location_id.id,
                'location_dest_id': move.location_dest_id.id,
            })

        return {'type': 'ir.actions.client', 'tag': 'reload'}

