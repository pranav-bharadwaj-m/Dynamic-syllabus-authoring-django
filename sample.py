from weasyprint import HTML
html = '''<html><body>
<table style=\"border-collapse:collapse;width:100%;\">
{% for i in range(60) %}
<tr><td style=\"border:1px solid #000;padding:5px;\">Row content line here number {{ i }}</td></tr>
{% endfor %}
</table></body></html>'''
HTML(string=html).write_pdf('test_break.pdf')
print('done')