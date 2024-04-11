import { Component } from '@angular/core';
import { LoginService } from '../shared/services/login.service';
import { Subscription } from 'rxjs';
import { Router } from '@angular/router';
import { HomeService } from '../shared/services/home.service';
import { ThemePalette } from '@angular/material/core';
import { Observable } from 'rxjs';


@Component({
  selector: 'app-user-journey',
  // standalone: true,
  templateUrl: './user-journey.component.html',
  styleUrl: './user-journey.component.scss'
})
export class UserJourneyComponent {
  photoURL: string | undefined;
  subscription: Subscription | undefined;
  showProgressPreviewBar: boolean = false
  color: ThemePalette = 'accent';

  constructor(public _router: Router, public loginService: LoginService, public homeService: HomeService) {
    this.subscription = this.loginService.getUserDetails().subscribe(message => {
      this.photoURL = message?.photoURL
    });
  }
  ngOnInit() {
    this.homeService.DBType = 'BigQuery';
  }

  userJourneyList: any = [{
    userId: "User journey 1",
    // userImg: "/assets/Persona headshots/Marla.png",
    // userTitle: "Postgress Business User",
    userTitle: "Business User",
    userContent: [
      "Natural language questions to the database.",
    ]
  },
  {

    userId: "User journey 2",
    // userImg: "/assets/Persona headshots/Firefly professional headshot of african american man 82343.jpg",
    // userTitle: "Postgress Opertaional User",
    userTitle: "Technical User",
    userContent: [
      "Select dataset, project, schema information",
      "Log analysis & monitoring"]
  },
  {
    userId: "User journey 3",
    userTitle: "Opertaional User",
    userContent: [
      "Natural language questions to the database.",
    ]
  }
  ];

  async navigateToHome(userTitle: String) {

    if (userTitle === 'Business User') {
      this.homeService.checkuserType = 'Business';
      this.showProgressPreviewBar = true;
     // new Promise<any>(async res => {
       this.homeService.getAvailableDatabases().subscribe((res: any) => {
          console.log(res)
          if (res && res.ResponseCode === 200) {
            this.homeService.setAvailableDBList(res.KnownDB);
            this.showProgressPreviewBar = false;
            this._router.navigate(['home']);
          }
        })
    //  })
    }
    if (userTitle === 'Opertaional User') {
      this.homeService.checkuserType = 'Operational';
      this._router.navigate(['home']);

    }

    if (userTitle === 'Technical User') {
      this.homeService.checkuserType = 'Technical';
      this._router.navigate(['home']);

    }
  }
  radioChange(event: any) {
    this.homeService.DBType = event.value;
  }

}
