import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SavedQueriesComponent } from './saved-queries.component';


describe('SavedQueriesComponent', () => {
  let component: SavedQueriesComponent;
  let fixture: ComponentFixture<SavedQueriesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SavedQueriesComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SavedQueriesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
