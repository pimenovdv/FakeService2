cat << 'PATCH_EOF' > /tmp/single_file.patch
<<<<<<< SEARCH
                if (successfulUploads.length < filesArray.length) {
                   this.uploadError = `Only ${successfulUploads.length} out of ${filesArray.length} files uploaded successfully.`;
                }
                const currentFiles = Array.isArray(this.value) ? this.value : [];
                this.onValueChange([...currentFiles, ...successfulUploads]);
            }
          })
=======
                if (successfulUploads.length < filesArray.length) {
                   this.uploadError = `Only ${successfulUploads.length} out of ${filesArray.length} files uploaded successfully.`;
                }
                const currentFiles = (this.def.multiple && Array.isArray(this.value)) ? this.value : [];
                this.onValueChange(this.def.multiple ? [...currentFiles, ...successfulUploads] : successfulUploads);
            }
          })
>>>>>>> REPLACE
PATCH_EOF
python3 -c "
import sys
with open('frontend/src/app/components/file-control/file-control.ts', 'r') as f: content = f.read()
with open('/tmp/single_file.patch', 'r') as f: patch = f.read()
search = patch.split('<<<<<<< SEARCH\n')[1].split('=======\n')[0]
replace = patch.split('=======\n')[1].split('>>>>>>> REPLACE\n')[0]
if search in content:
  with open('frontend/src/app/components/file-control/file-control.ts', 'w') as f: f.write(content.replace(search, replace))
  print('Patch applied successfully')
else:
  print('Search string not found')
"
