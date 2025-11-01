# Stock Picking Import Serials

### Overview
This module allows users to **import serial or lot numbers** directly from an **Excel file** into a stock picking in Odoo.  
It simplifies data entry for serialized inventory operations like receipts, internal transfers, and deliveries.

---

### Features
- Import serial/lot numbers from Excel.
- Works directly from the stock picking form view.
- Automatically links imported serials to the corresponding picking lines.
- Supports multiple file formats.
- Validation and error handling for duplicate or invalid serials.

---

### How It Works
1. Open any **Stock Picking** record (Receipt/Delivery/Internal Transfer).  
2. Click the **“Import Serials”** button.  
3. Select your Excel file.  
4. Review and confirm imported serials.

---

### File Format
Your Excel or CSV file should include:
| Product | Lot/Serial Number | Quantity |
|----------|------------------|-----------|
| Product A | SN0001 | 1 |
| Product B | SN0002 | 1 |

---

### Dependencies
- **Odoo 18.0**
- **Stock** module

---


### License
This module is licensed under the **LGPL-3** License.

---

### Version
**18.0.1.0.0**

