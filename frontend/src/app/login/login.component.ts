import { Component, ElementRef } from '@angular/core';
import { LoginButtonComponent } from '../login-button/login-button.component';
import { Subscription } from 'rxjs';
import { Router } from '@angular/router';
import { Dialog } from '@angular/cdk/dialog';
import { LoginService } from '../shared/services/login.service';

@Component({
  // standalone: true,
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  photoURL: string | undefined;
  subscription: Subscription | undefined;
  acceptAndAgreeButton: boolean = true
  constructor(private _router: Router, public loginService: LoginService, private elementRef:ElementRef
    ,public dialog: Dialog) {
    this.subscription = this.loginService.getUserDetails().subscribe(res => {
      this.userLoggedIn = true;
      this.photoURL = res?.photoURL
    });
  }

  ngOnInit() {
   this.showLogIn()
  }

  userLoggedIn: boolean = false;
  navigateToUserJourney() {
    this.userLoggedIn = true;
    this._router.navigate(['user-journey'])
  }


  showLogIn(): void {
    const dialogRef = this.dialog.open(LoginButtonComponent, {
      disableClose: true,
      width: '350px',
      panelClass: 'login-container'
    });
  }

  checkboxChecked(event: any) {
    if (event.target.checked) {
      this.acceptAndAgreeButton = false
    } else {
      this.acceptAndAgreeButton = true
    }
  }
}
