import { TestBed } from '@angular/core/testing';

import { LlmServiceTsService } from './llm.service.ts.service';

describe('LlmServiceTsService', () => {
  let service: LlmServiceTsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LlmServiceTsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
