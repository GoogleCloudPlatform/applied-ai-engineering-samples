import { Dialog } from '@angular/cdk/dialog';
import { Component } from '@angular/core';
import { LoginService } from '../shared/services/login.service';
import { SharedService } from '../shared/services/shared.service';

@Component({

  selector: 'app-load-popup',
  // standalone: true,
  templateUrl: './load-popup.component.html',
  styleUrl: './load-popup.component.scss'
})
export class LoadPopupComponent {
  photoURL: any;
  userLoggedIn: boolean = false;
  constructor(public fireservice: SharedService, public loginService: LoginService,
    public dialog: Dialog) {
  }}
