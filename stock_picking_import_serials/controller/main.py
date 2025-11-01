from odoo import http
from odoo.http import request
import io, csv

try:
    import xlsxwriter
except Exception:
    xlsxwriter = None


class PickingImportController(http.Controller):

    @http.route('/picking_import/download_template', type='http', auth='user')
    def download_template(self, picking_id=None, file_type="xlsx", **kwargs):
        """
        Download picking import template for a single picking.
        :param picking_id: ID of the picking (many2one)
        :param file_type: 'xlsx'
        """
        headers = ["Receipt Number", "ID", "Product", "Quantity", "Lot / Serial Number(s)", "Expiration Date"]

        # Get the picking record
        picking = request.env['stock.picking'].browse(int(picking_id)) if picking_id else None

        # XLSX Template
        if file_type.lower() == "xlsx" and xlsxwriter:
            out = io.BytesIO()
            wb = xlsxwriter.Workbook(out, {"in_memory": True})
            ws = wb.add_worksheet("template")

            # Write header
            for col, h in enumerate(headers):
                ws.write(0, col, h)

            row = 1
            if picking:
                for move in picking.move_ids_without_package:
                    ws.write(row, 0, picking.name or "")
                    ws.write(row, 1, move.product_id.id or "")
                    ws.write(row, 2, move.product_id.name or "")
                    ws.write(row, 3, int(move.product_uom_qty))
                    ws.write(row, 4, "")
                    ws.write(row, 6, "")
                    row += 1

            wb.close()
            content = out.getvalue()
            filename = "picking_import_template.xlsx"
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        return request.make_response(
            content,
            headers=[
                ("Content-Type", content_type),
                ("Content-Disposition", f'attachment; filename="{filename}"'),
            ],
        )


