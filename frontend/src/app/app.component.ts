import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  // standalone: true,
  // imports: [NgIf, NgFor,RouterOutlet,LoginComponent,LoginButtonComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'data-engineering-ui-app';
  config: any;
  constructor() {}
  ngOnInit() {}
}
