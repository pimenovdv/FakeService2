import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Player } from './player';
import { ApiService } from '../../services/api';
import { StateService } from '../../services/state';
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { Screen } from '../../models/screen.model';
import { vi, expect, describe, it, beforeEach } from 'vitest';

describe('Player', () => {
  let component: Player;
  let fixture: ComponentFixture<Player>;
  let mockApiService: any;
  let mockStateService: any;
  let mockActivatedRoute: any;

  beforeEach(async () => {
    mockApiService = {
      start: vi.fn().mockReturnValue(of({ id: 'test-screen' } as Screen))
    };

    mockStateService = {
      setScreen: vi.fn(),
      currentScreen$: of(null)
    };

    mockActivatedRoute = {
      paramMap: of({ get: () => 'test-service' })
    };

    await TestBed.configureTestingModule({
      imports: [Player],
      providers: [
        { provide: ApiService, useValue: mockApiService },
        { provide: StateService, useValue: mockStateService },
        { provide: ActivatedRoute, useValue: mockActivatedRoute }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Player);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should read service_id from route and call start', () => {
    expect(mockApiService.start).toHaveBeenCalledWith('test-service');
  });

  it('should set screen in state service when start is successful', () => {
    expect(mockStateService.setScreen).toHaveBeenCalledWith({ id: 'test-screen' });
    expect(component.loading).toBeFalsy();
    expect(component.error).toBeNull();
  });
});
