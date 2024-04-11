import { Injectable } from '@angular/core';
import { Observable, ReplaySubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LoginService {

  constructor() { }
  private userDetails = new ReplaySubject<any>(1);
  userDetails$: Observable<any> = this.userDetails.asObservable();

  getUserDetails(): Observable<any> {
    return this.userDetails$;
}

sendUserDetails(message: any) {
  this.userDetails.next(message);
}
}
