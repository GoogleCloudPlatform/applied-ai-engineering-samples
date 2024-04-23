import { Component, ElementRef } from '@angular/core';
import { LoginButtonComponent } from '../login-button/login-button.component';
import { Subscription } from 'rxjs';
import { Router } from '@angular/router';
import { Dialog } from '@angular/cdk/dialog';
import { LoginService } from '../shared/services/login.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  // standalone: true,
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  photoURL: string | undefined;
  subscription: Subscription | undefined;
  acceptAndAgreeButton: boolean = true;
  loginError = false;
  loginErrorMessage: any
  constructor(private _router: Router, public loginService: LoginService, private elementRef:ElementRef
    ,public dialog: Dialog, public snackbar : MatSnackBar) {
      this.loginService.getLoginError().subscribe((res: any) => {
        this.loginErrorMessage = res
        this.loginError = true;
      });
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
    if (!this.loginError) {
      this.userLoggedIn = true;
      this._router.navigate(['user-journey']);
    }
    else{
      this.showSnackbarCssStyles(this.loginErrorMessage,'Close',10000);
    }
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

  showSnackbarCssStyles(content: any, action: any, duration: any) {
    let sb = this.snackbar.open(content, action, {
      duration: duration,
      panelClass: ["custom-style"]
    });
    sb.onAction().subscribe(() => {
      sb.dismiss();
    });
  }
}
