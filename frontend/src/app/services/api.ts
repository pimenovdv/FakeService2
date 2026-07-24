import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Screen, RestMetadata } from '../models/screen.model';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = ''; // Empty string so that calls use the proxy

  constructor(private http: HttpClient) { }

  start(serviceId: string): Observable<Screen> {
    return this.http.post<Screen>(`${this.baseUrl}/api/screens/start`, { service_id: serviceId });
  }

  nextStep(serviceId: string, currentScreenId: string, answers: Record<string, any>): Observable<Screen | any> {
    return this.http.post<Screen | any>(`${this.baseUrl}/api/screens/next_step`, {
      service_id: serviceId,
      current_screen_id: currentScreenId,
      answers: answers
    });
  }

  dynamicCall(metadata: RestMetadata): Observable<any> {
    const url = metadata.endpoint.startsWith('http') ? metadata.endpoint : `${this.baseUrl}${metadata.endpoint}`;
    if (metadata.method === 'POST') {
      return this.http.post<any>(url, metadata.params || {});
    } else {
      return this.http.get<any>(url, { params: metadata.params || {} });
    }
  }

  uploadFile(file: File): Observable<HttpEvent<any>> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<any>(`${this.baseUrl}/api/upload`, formData, {
      reportProgress: true,
      observe: 'events'
    });
  }
}
