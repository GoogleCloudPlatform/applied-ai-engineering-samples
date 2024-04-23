import { Component, ViewChild } from '@angular/core';
import { FormControl } from '@angular/forms';
import { HomeService } from '../shared/services/home.service';
import { ThemePalette } from '@angular/material/core';
import { MatSidenav } from '@angular/material/sidenav';
import { BreakpointObserver } from '@angular/cdk/layout';
import { LoginService } from '../shared/services/login.service';
import { Router } from '@angular/router';


@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss',
})
export class HomeComponent {
  title = 'material-responsive-sidenav';
  isCollapsed = true;
  organizationCtrl = new FormControl<string>('');

  organisation: any;
  organizationString: any;
  checkStyle: boolean | undefined;
  userType: String | undefined;
  color: ThemePalette = 'accent';
  checkSideNav: string | undefined;
  @ViewChild(MatSidenav)
  sidenav!: MatSidenav;
  isMobile = true;
  selectedDb: any;
  photoURL: any;

  constructor(private homeService: HomeService, private observer: BreakpointObserver , private _router : Router, private loginService : LoginService) { 
    this.loginService.getUserDetails().subscribe(message => {
      this.photoURL = message?.photoURL
    });
  }
  async ngOnInit() {
    if(!this.photoURL){
      this._router.navigate(['']);
    }
    this.observer.observe(['(max-width: 800px)']).subscribe((screenSize) => {
      if (screenSize.matches) {
        this.isMobile = true;
      } else {
        this.isMobile = false;
      }
    });

    if (this.homeService.checkuserType === undefined) {
      this.userType = 'Business';

    } else {
      this.userType = this.homeService.checkuserType;

    }
    this.organizationString = this.homeService.getAvailableDBList();
    // this.homeService.databaseSubject.subscribe((data: any) => {
    if (this.organizationString !== null && this.organizationString !== undefined) {
      this.organisation = JSON.parse(this.organizationString);
      this.selectedDb = this.organisation[0].table_schema.split("-")
      if (this.selectedDb.length === 2) {
        this.selectedDb[1] = this.selectedDb.slice(1).join("-"); // Merge elements from index 1 onwards
      }
      this.organizationCtrl.setValue(this.organisation[0].table_schema);
      this.homeService.setselectedDb(this.selectedDb[0]);
      this.homeService.setselectedDbName(this.selectedDb[1])
      this.homeService.sqlSuggestionList(this.selectedDb[0], this.selectedDb[1]).subscribe((data: any) => {
        if (data && data.ResponseCode === 200) {
          this.homeService.databaseSubject.next(data.KnownSQL);
        }
      })
    } else {
      this.homeService.getAvailableDatabases().subscribe((res: any) => {
        if (res && res.ResponseCode === 200) {
          // this.homeService.setAvailableDBList(res.KnownDB);
          this.organisation = JSON.parse(res.KnownDB);
          this.selectedDb = this.organisation[0].table_schema.split("-")
          this.organizationCtrl.setValue(this.organisation[0].table_schema);
          this.homeService.setselectedDb(this.selectedDb[0]);
          this.homeService.setselectedDbName(this.selectedDb[1])
          this.homeService.sqlSuggestionList(this.selectedDb[0], this.selectedDb[1]).subscribe((data: any) => {
            if (data && data.ResponseCode === 200) {
              this.homeService.databaseSubject.next(data.KnownSQL);
            }
          })
        }
      });
    }
  }

  changeDb(dbtype: any) {
    let selectedDbtype = dbtype.target.value.split("-");
    this.homeService.setselectedDb(selectedDbtype[0]);
    this.homeService.setselectedDbName(selectedDbtype[1])
    this.homeService.sqlSuggestionList(selectedDbtype[0], selectedDbtype[1]).subscribe((data: any) => {
      if (data && data.ResponseCode === 200) {
        this.homeService.databaseSubject.next(data.KnownSQL);
      }
    })
  }


  updateBackgroundStyle(data: boolean) {
    this.checkStyle = data;
  }
  checkSideNavTAb(data: any) {
    this.checkSideNav = data;
  }
  toggleMenu() {
    if (this.isMobile) {
      this.sidenav.toggle();
    } else {
      // do nothing for now
    }
  }


}
