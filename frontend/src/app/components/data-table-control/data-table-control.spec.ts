import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DataTableControlComponent } from './data-table-control.component';
import { ComponentDef } from '../../models/screen.model';
import { FormsModule } from '@angular/forms';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('DataTableControlComponent', () => {
  let component: DataTableControlComponent;
  let fixture: ComponentFixture<DataTableControlComponent>;

  const mockDef: ComponentDef = {
    id: 'dt1',
    type: 'data_table',
    label: 'Test Data Table',
    components: [
      { id: 'col1', type: 'text', label: 'Column 1' },
      { id: 'col2', type: 'number', label: 'Column 2' }
    ]
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DataTableControlComponent, FormsModule, NoopAnimationsModule]
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DataTableControlComponent);
    component = fixture.componentInstance;
    component.def = mockDef;
    component.value = [];
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should add a row', () => {
    component.addRow();
    expect(component.value.length).toBe(1);
    expect(component.value[0]).toEqual({ col1: null, col2: null });
  });

  it('should update a cell', () => {
    component.addRow();
    component.onCellChange(0, 'col1', 'Test Value');
    expect(component.value[0].col1).toBe('Test Value');
  });

  it('should remove a row', () => {
    component.addRow();
    component.addRow();
    expect(component.value.length).toBe(2);

    component.removeRow(0);
    expect(component.value.length).toBe(1);
  });
});
