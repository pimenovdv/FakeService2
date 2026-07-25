cat << 'PATCH_EOF' > /tmp/file_control.patch
<<<<<<< SEARCH
  <div *ngIf="isUploading" class="mt-2 space-y-2">
=======
  <div *ngIf="def.multiple && value && value.length > 0 && !isUploading" class="mt-2 space-y-2">
    <div *ngFor="let file of value; let i = index"
         class="flex items-center justify-between p-2 bg-gray-50 border rounded text-sm cursor-move"
         draggable="true"
         (dragstart)="onDragStart($event, i)"
         (dragover)="onDragOver($event)"
         (drop)="onDrop($event, i)">
      <span class="truncate">{{ file.filename }}</span>
      <button type="button" (click)="removeFile(i)" class="text-red-500 hover:text-red-700 ml-2 focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </div>
  <div *ngIf="isUploading" class="mt-2 space-y-2">
>>>>>>> REPLACE
PATCH_EOF
python3 -c "
import sys
with open('frontend/src/app/components/file-control/file-control.html', 'r') as f: content = f.read()
with open('/tmp/file_control.patch', 'r') as f: patch = f.read()
search = patch.split('<<<<<<< SEARCH\n')[1].split('=======\n')[0]
replace = patch.split('=======\n')[1].split('>>>>>>> REPLACE\n')[0]
if search in content:
  with open('frontend/src/app/components/file-control/file-control.html', 'w') as f: f.write(content.replace(search, replace))
  print('Patch applied successfully')
else:
  print('Search string not found')
"
