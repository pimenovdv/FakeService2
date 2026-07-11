import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ApiService } from './api';
import { Screen, RestMetadata } from '../models/screen.model';

describe('ApiService', () => {
  let service: ApiService;
  let httpMock: HttpTestingController;
  const baseUrl = '';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [ApiService]
    });
    service = TestBed.inject(ApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify(); // Ensure no outstanding requests
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should call start endpoint', () => {
    const dummyScreen: Screen = {
      id: 'screen1',
      header: 'Test Screen',
      content: 'This is a test',
      components: [],
      buttons: []
    };

    service.start('service-1').subscribe(screen => {
      expect(screen).toEqual(dummyScreen);
    });

    const req = httpMock.expectOne(`${baseUrl}/api/screens/start`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ service_id: 'service-1' });
    req.flush(dummyScreen);
  });

  it('should call next_step endpoint', () => {
    const dummyScreen: Screen = {
      id: 'screen2',
      header: 'Next Screen',
      content: 'This is the next test',
      components: [],
      buttons: []
    };

    service.nextStep('service-1', 'screen1', { q1: 'yes' }).subscribe(screen => {
      expect(screen).toEqual(dummyScreen);
    });

    const req = httpMock.expectOne(`${baseUrl}/api/screens/next_step`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({
      service_id: 'service-1',
      screen_id: 'screen1',
      answers: { q1: 'yes' }
    });
    req.flush(dummyScreen);
  });

  it('should make dynamic GET call', () => {
    const metadata: RestMetadata = {
      endpoint: '/api/data/cities',
      method: 'GET',
      params: { country: 'US' }
    };

    service.dynamicCall(metadata).subscribe(data => {
      expect(data).toEqual(['New York', 'Los Angeles']);
    });

    const req = httpMock.expectOne(`${baseUrl}/api/data/cities?country=US`);
    expect(req.request.method).toBe('GET');
    req.flush(['New York', 'Los Angeles']);
  });

  it('should make dynamic POST call', () => {
    const metadata: RestMetadata = {
      endpoint: '/api/data/search',
      method: 'POST',
      params: { query: 'test' }
    };

    service.dynamicCall(metadata).subscribe(data => {
      expect(data).toEqual({ result: 'found' });
    });

    const req = httpMock.expectOne(`${baseUrl}/api/data/search`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ query: 'test' });
    req.flush({ result: 'found' });
  });
});
