from odoo import models


class AttendanceExcelReport(models.AbstractModel):
    _name = 'report.attendance_report_excel'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data=None, objs=None):
        # Define formats:
        name_format = workbook.add_format(
            {'bold': True, 'align': 'center', 'valign': 'vcenter', 'size': 14,
             'fg_color': '008000', 'font_color': 'white'})
        header_format = workbook.add_format(
            {'bold': True, 'align': 'center', 'valign': 'vcenter', 'size': 14,
             'font_color': 'white', 'border': 1, 'border_color': 'black', 'fg_color': 'F08080', })
        data_format = workbook.add_format(
            {'border': 1, 'border_color': 'black', 'align': 'center',
             'font_color': 'black', 'bold': True, 'size': 12,
             'valign': 'vcenter', })

        for record in data['records'][0]:
            # Define sheet(s):
            sheet_name = record[0] if record[0] else None
            sheet = workbook.add_worksheet(sheet_name)
            sheet.set_column('A:M', 15)

            # Write header row:
            sheet.merge_range('A1:D1', record[1], name_format)
            sheet.merge_range('E1:F1', record[0], name_format)
            if self.env.user.lang == 'ar_001' or self.env.user.lang == 'ar_SY':
                sheet.right_to_left()
                sheet.write(1, 0, 'اليوم', header_format)
                sheet.write(1, 1, 'التاريخ', header_format)
                sheet.write(1, 2, 'وقت الحضور', header_format)
                sheet.write(1, 3, 'الحضور الفعلي', header_format)
                sheet.write(1, 4, 'وقت الانصراف', header_format)
                sheet.write(1, 5, 'الانصراف الفعلي', header_format)
                sheet.write(1, 6, 'ساعات العمل', header_format)
                sheet.write(1, 7, 'ساعات اضافي', header_format)
                sheet.write(1, 8, 'ساعات التاخير', header_format)
                sheet.write(1, 9, 'ساعات الانصراف', header_format)
                sheet.write(1, 10, 'جزاء التاخير', header_format)
                sheet.write(1, 11, 'جزاء الانصراف', header_format)
                sheet.write(1, 12, 'ملاحظات', header_format)
                total = 'اجمالي'
            else:
                sheet.write(1, 0, 'Day', header_format)
                sheet.write(1, 1, 'Date', header_format)
                sheet.write(1, 2, 'Time in', header_format)
                sheet.write(1, 3, 'Punch in', header_format)
                sheet.write(1, 4, 'Time out', header_format)
                sheet.write(1, 5, 'Punch out', header_format)
                sheet.write(1, 6, 'Work Hours', header_format)
                sheet.write(1, 7, 'Extra Hours', header_format)
                sheet.write(1, 8, 'Actual Late', header_format)
                sheet.write(1, 9, 'Actual Diff', header_format)
                sheet.write(1, 10, 'Penalty Late', header_format)
                sheet.write(1, 11, 'Penalty Diff', header_format)
                sheet.write(1, 12, 'Notes', header_format)
                total = 'Total'

            # Write data rows:
            i = 3
            total_wh = 0
            total_eh = 0
            total_al = 0
            total_ad = 0
            total_pl = 0
            total_pd = 0
            for row_index, obj in enumerate(record[2], start=2):
                sheet.write_row(row_index, 0, obj.values(), data_format)
                # sheet.set_row(row_index, 18)
                total_wh += obj['work_hours']
                total_eh += obj['overtime_hours']
                total_al += obj['act_late']
                total_ad += obj['act_diff']
                total_pl += obj['pen_late']
                total_pd += obj['pen_diff']
                i += 1

            sheet.merge_range(f'A{i}:F{i}', total, name_format)
            sheet.write(i - 1, 6, total_wh, name_format)
            sheet.write(i - 1, 7, total_eh, name_format)
            sheet.write(i - 1, 8, total_al, name_format)
            sheet.write(i - 1, 9, total_ad, name_format)
            sheet.write(i - 1, 10, total_pl, name_format)
            sheet.write(i - 1, 11, total_pd, name_format)
