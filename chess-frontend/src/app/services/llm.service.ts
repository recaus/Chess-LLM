import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class LlmService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  renderLevel(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/render-level`, data);
  }

  performAction(data: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/perform-action`, data);
  }
}
