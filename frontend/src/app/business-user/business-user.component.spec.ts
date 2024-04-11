import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BusinessUserComponent } from './business-user.component';

describe('BusinessUserComponent', () => {
  let component: BusinessUserComponent;
  let fixture: ComponentFixture<BusinessUserComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BusinessUserComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BusinessUserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
