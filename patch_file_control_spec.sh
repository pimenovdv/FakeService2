cat << 'PATCH_EOF' > /tmp/file_control_spec.patch
<<<<<<< SEARCH
  it('should handle null files properly', () => {
=======
  it('should allow removing a file', () => {
    component.value = [
      { filename: 'file1.txt' },
      { filename: 'file2.txt' },
      { filename: 'file3.txt' }
    ];

    component.removeFile(1);

    expect(component.value.length).toBe(2);
    expect(component.value[0].filename).toBe('file1.txt');
    expect(component.value[1].filename).toBe('file3.txt');
  });

  it('should set value to null if removing the last file', () => {
    component.value = [{ filename: 'file1.txt' }];
    component.removeFile(0);
    expect(component.value).toBeNull();
  });

  it('should handle drag and drop to reorder files', () => {
    component.value = [
      { filename: 'file1.txt' },
      { filename: 'file2.txt' },
      { filename: 'file3.txt' }
    ];

    // Simulate drag start on index 0
    const dragStartEvent = new Event('dragstart') as any;
    dragStartEvent.dataTransfer = {
      setData: vi.fn(),
      effectAllowed: ''
    };
    component.onDragStart(dragStartEvent, 0);
    expect(component.draggedIndex).toBe(0);

    // Simulate drop on index 2
    const dropEvent = new Event('drop') as any;
    dropEvent.preventDefault = vi.fn();
    component.onDrop(dropEvent, 2);

    expect(component.value.length).toBe(3);
    expect(component.value[0].filename).toBe('file2.txt');
    expect(component.value[1].filename).toBe('file3.txt');
    expect(component.value[2].filename).toBe('file1.txt');
    expect(component.draggedIndex).toBeNull();
  });

  it('should append files on subsequent uploads when multiple is true', () => {
    const inputElement = fixture.nativeElement.querySelector('input[type="file"]');

    // Initial state
    component.value = [{ filename: 'existing.txt' }];

    apiServiceSpy.uploadFile.mockImplementation((file: File) => {
        return of(
          { type: HttpEventType.UploadProgress, loaded: 100, total: 100 },
          new HttpResponse({ body: { file_id: `id_${file.name}`, url: `/mock-uploads/id_${file.name}/${file.name}`, filename: file.name } })
        );
    });

    Object.defineProperty(inputElement, 'files', {
        value: [new File([''], 'new.txt')],
        writable: true
    });
    inputElement.dispatchEvent(new Event('change'));

    expect(component.value.length).toBe(2);
    expect(component.value[0].filename).toBe('existing.txt');
    expect(component.value[1].filename).toBe('new.txt');
  });

  it('should handle null files properly', () => {
>>>>>>> REPLACE
PATCH_EOF
python3 -c "
import sys
with open('frontend/src/app/components/file-control/file-control.spec.ts', 'r') as f: content = f.read()
with open('/tmp/file_control_spec.patch', 'r') as f: patch = f.read()
search = patch.split('<<<<<<< SEARCH\n')[1].split('=======\n')[0]
replace = patch.split('=======\n')[1].split('>>>>>>> REPLACE\n')[0]
if search in content:
  with open('frontend/src/app/components/file-control/file-control.spec.ts', 'w') as f: f.write(content.replace(search, replace))
  print('Patch applied successfully')
else:
  print('Search string not found')
"
