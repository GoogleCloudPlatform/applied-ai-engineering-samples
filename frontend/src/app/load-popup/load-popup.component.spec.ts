import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LoadPopupComponent } from './load-popup.component';

describe('LoadPopupComponent', () => {
  let component: LoadPopupComponent;
  let fixture: ComponentFixture<LoadPopupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoadPopupComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(LoadPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
