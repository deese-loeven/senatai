import re

with open('app.py', 'r') as f:
    content = f.read()

# Add Decimal import at the top if not present
if "from decimal import Decimal" not in content:
    # Find the imports section and add Decimal import
    content = content.replace(
        "import os",
        "import os\nfrom decimal import Decimal"
    )

# Use Decimal arithmetic instead of float
content = re.sub(
    r"estimated_dividend = balance \* 0\.50",
    "estimated_dividend = balance * Decimal('0.50')",
    content
)

with open('app.py', 'w') as f:
    f.write(content)

print("✅ Converted to Decimal arithmetic!")
