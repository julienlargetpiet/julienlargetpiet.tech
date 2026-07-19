import pandas as pd
from io import StringIO

html = """
<table>
  <tr><th>name</th><th>age</th><th>city</th></tr>
  <tr><td>Alice</td><td>25</td><td>Paris</td></tr>
  <tr><td>Bob</td><td>30</td><td>London</td></tr>
</table>
"""

df = pd.read_html(StringIO(html))[0]
print(df)

