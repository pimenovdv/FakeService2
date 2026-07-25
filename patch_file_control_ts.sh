cat << 'PATCH_EOF' > /tmp/file_control_ts.patch
<<<<<<< SEARCH
  onFileChange(event: Event) {
=======
  draggedIndex: number | null = null;

  onDragStart(event: DragEvent, index: number) {
    this.draggedIndex = index;
    if (event.dataTransfer) {
      event.dataTransfer.effectAllowed = 'move';
      // Set some data to make Firefox allow the drag
      event.dataTransfer.setData('text/plain', index.toString());
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    if (event.dataTransfer) {
      event.dataTransfer.dropEffect = 'move';
    }
  }

  onDrop(event: DragEvent, dropIndex: number) {
    event.preventDefault();
    if (this.draggedIndex !== null && this.draggedIndex !== dropIndex) {
      const newValue = [...(this.value || [])];
      const movedItem = newValue.splice(this.draggedIndex, 1)[0];
      newValue.splice(dropIndex, 0, movedItem);
      this.onValueChange(newValue);
    }
    this.draggedIndex = null;
  }

  removeFile(index: number) {
    if (this.value && Array.isArray(this.value)) {
      const newValue = [...this.value];
      newValue.splice(index, 1);
      this.onValueChange(newValue.length > 0 ? newValue : null);
    }
  }

  onFileChange(event: Event) {
>>>>>>> REPLACE
<<<<<<< SEARCH
                if (successfulUploads.length < filesArray.length) {
                   this.uploadError = `Only ${successfulUploads.length} out of ${filesArray.length} files uploaded successfully.`;
                }
                this.onValueChange(successfulUploads);
            }
          })
=======
                if (successfulUploads.length < filesArray.length) {
                   this.uploadError = `Only ${successfulUploads.length} out of ${filesArray.length} files uploaded successfully.`;
                }
                const currentFiles = Array.isArray(this.value) ? this.value : [];
                this.onValueChange([...currentFiles, ...successfulUploads]);
            }
          })
>>>>>>> REPLACE
PATCH_EOF
python3 -c "
import sys
with open('frontend/src/app/components/file-control/file-control.ts', 'r') as f: content = f.read()
with open('/tmp/file_control_ts.patch', 'r') as f: patch = f.read()

blocks = patch.split('<<<<<<< SEARCH\n')[1:]
for block in blocks:
  search = block.split('=======\n')[0]
  replace = block.split('=======\n')[1].split('>>>>>>> REPLACE\n')[0]
  if search in content:
    content = content.replace(search, replace)
    print('Patch block applied')
  else:
    print('Search string not found in block:')
    print(search)

with open('frontend/src/app/components/file-control/file-control.ts', 'w') as f: f.write(content)
"
