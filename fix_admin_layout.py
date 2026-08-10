"""Fix admin pages: add layout.js script tag and buildFooter() call."""
import os, re, glob

admin_dir = 'frontend/admin'
for filepath in sorted(glob.glob(f'{admin_dir}/*.html')):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False
    fname = os.path.basename(filepath)

    # 1. Add layout.js after api.js if missing
    if 'layout.js' not in content and 'api.js' in content:
        old = '<script src="/assets/js/api.js"></script>'
        new = old + '\n    <script src="/assets/js/layout.js"></script>'
        content = content.replace(old, new, 1)
        changed = True
        print(f'  layout.js added: {fname}')

    # 2. Add buildFooter() after upgradeSidebarBrand() if missing
    if 'buildFooter()' not in content and 'layout.js' in content:
        if 'upgradeSidebarBrand();' in content:
            content = content.replace(
                'upgradeSidebarBrand();',
                'upgradeSidebarBrand();\n            buildFooter();',
                1
            )
            changed = True
            print(f'  buildFooter() added: {fname}')

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(f'  OK: {fname}')

print('Done.')
