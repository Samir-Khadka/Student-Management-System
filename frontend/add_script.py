
import os

file_path = r'd:\Programs\Student-Management-System\frontend\index.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '<script src="js/dashboard.js"></script>'
replacement = '<script src="js/profile.js"></script>\n    <script src="js/dashboard.js"></script>'

if target in content:
    if 'js/profile.js' not in content:
        content = content.replace(target, replacement)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully added profile.js script tag")
    else:
        print("profile.js already exists")
else:
    print("Target script tag not found")
