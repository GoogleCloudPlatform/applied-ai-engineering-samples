import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserJourneyComponent } from './user-journey.component';

describe('UserJourneyComponent', () => {
  let component: UserJourneyComponent;
  let fixture: ComponentFixture<UserJourneyComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserJourneyComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(UserJourneyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
