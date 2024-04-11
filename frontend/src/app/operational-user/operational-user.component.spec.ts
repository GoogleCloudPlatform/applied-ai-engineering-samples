import { ComponentFixture, TestBed } from '@angular/core/testing';
import { OperationalUserComponent } from './operational-user.component';


describe('OperationalUserComponent', () => {
  let component: OperationalUserComponent;
  let fixture: ComponentFixture<OperationalUserComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OperationalUserComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OperationalUserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
