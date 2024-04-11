import { Component } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';

@Component({
  selector: 'app-technical-user',
  templateUrl: './technical-user.component.html',
  styleUrl: './technical-user.component.scss'
})
export class TechnicalUserComponent {

  sqlSearchForm = new FormGroup({
    name: new FormControl(),
  });
}
