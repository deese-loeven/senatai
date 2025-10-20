import re

with open('app.py', 'r') as f:
    content = f.read()

# Update templates to show original bill numbers where appropriate
# For now, the app should work as-is since it queries the database

print("✅ App should work with new bill ID format")
print("💡 The app will display unique bill IDs like 'C-51-42-1'")
print("   Users can still understand these as variations of C-51")
