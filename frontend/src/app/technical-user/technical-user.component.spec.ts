import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TechnicalUserComponent } from './technical-user.component';

describe('TechnicalUserComponent', () => {
  let component: TechnicalUserComponent;
  let fixture: ComponentFixture<TechnicalUserComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TechnicalUserComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(TechnicalUserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
