cat << 'PATCH_EOF' > /tmp/todo.patch
<<<<<<< SEARCH
## Completed Phases
- **Phases 1-53:** Core features, controls, routing, dynamic engine, actions, validation, testing, external integrations (`js-interpreter`, API), advanced components (Data Table, grouping, tooltips, animations, masks), and Rich Text Editor (`ngx-quill`).

## Planned Features
- [ ] **Phase 54:** Drag-and-drop File Reordering. Allow users to reorder uploaded files.
- [ ] **Phase 55:** PDF Export. Provide functionality to export a completed screen/form to a PDF document.
=======
## Completed Phases
- **Phases 1-54:** Core features, controls, routing, dynamic engine, actions, validation, testing, external integrations (`js-interpreter`, API), advanced components (Data Table, grouping, tooltips, animations, masks), Rich Text Editor (`ngx-quill`), and drag-and-drop file reordering.

## Planned Features
- [ ] **Phase 55:** PDF Export. Provide functionality to export a completed screen/form to a PDF document.
>>>>>>> REPLACE
PATCH_EOF
python3 -c "
import sys
with open('frontend/todo_front.md', 'r') as f: content = f.read()
with open('/tmp/todo.patch', 'r') as f: patch = f.read()
search = patch.split('<<<<<<< SEARCH\n')[1].split('=======\n')[0]
replace = patch.split('=======\n')[1].split('>>>>>>> REPLACE\n')[0]
if search in content:
  with open('frontend/todo_front.md', 'w') as f: f.write(content.replace(search, replace))
  print('Patch applied successfully')
else:
  print('Search string not found')
"
