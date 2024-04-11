import { Injectable, inject } from '@angular/core';
import { LoginService } from './login.service';
import { Firestore } from '@angular/fire/firestore';
import { GoogleAuthProvider, getAuth, signInWithPopup } from '@firebase/auth';
import { getStorage } from "firebase/storage";
import { initializeApp } from '@angular/fire/app';
import { Auth } from '@angular/fire/auth';
import { AngularFireAuth } from '@angular/fire/compat/auth';
import firebase from 'firebase/compat';

@Injectable({
  providedIn: 'root'
})
export class SharedService {
    userData: any;
    private auth: Auth = inject(Auth);
  

  constructor(private fs: Firestore, public loginservice: LoginService,
    private afAuth: AngularFireAuth
    ) { }
  
 
  async googleSignin() {
    const provider = new GoogleAuthProvider();

    return await signInWithPopup(this.auth, provider)

      .then((result) => {
        return result.user
      }).
      catch(

        function(error) {
          // Handle Errors here.
          var errorCode = error.code;
          if (errorCode === 'auth/account-exists-with-different-credential') {
            alert('You have already signed up with a different auth provider for that email.');
            // If you are using multiple auth providers on your app you should handle linking
            // the user's accounts here.
          } else {
            console.error(error);
          }
        });
  }
  // async googleSignin() {
  //   return this.AuthLogin(new GoogleAuthProvider());
  // }
  // // Auth logic to run auth providers
  // AuthLogin(provider: firebase.auth.AuthProvider | GoogleAuthProvider) {
  //   return this.afAuth
  //     .signInWithPopup(provider)
  //     .then((result) => {
  //       console.log('You have been successfully logged in!');
  //     })
  //     .catch((error) => {
  //       console.log(error);
  //     });
  // }

}

