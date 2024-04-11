import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserPhotoComponent } from './user-photo.component';

describe('UserPhotoComponent', () => {
  let component: UserPhotoComponent;
  let fixture: ComponentFixture<UserPhotoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserPhotoComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(UserPhotoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
