import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PrismComponent } from './prism.component';

describe('MenuComponent', () => {
  let component: PrismComponent;
  let fixture: ComponentFixture<PrismComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PrismComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(PrismComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
