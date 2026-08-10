import os

frontend_dir = r"C:\Users\CHEMOGET\Desktop\3.1\software engineering\COURSE_REGISTRATION_SYSTEM\Course_Registration\frontend"

replacements = [
    ("Unit Registrations", "Course Registrations"),
    ("Unit Registration", "Course Registration"),
    ("unit registration", "course registration"),
    ("Unit Approvals", "Course Approvals")
]

for root, _, files in os.walk(frontend_dir):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            new_content = content
            for old, new in replacements:
                new_content = new_content.replace(old, new)
                
            if new_content != content:
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                print(f"Updated {f}")

print("Done updating frontend HTML files.")
