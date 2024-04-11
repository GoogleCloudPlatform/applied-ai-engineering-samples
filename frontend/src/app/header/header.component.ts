import { Component } from '@angular/core';
import { LoginService } from '../shared/services/login.service';
import { HomeService } from '../shared/services/home.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
    constructor(public homeService: HomeService
        ) { }

ngOnInit(){

}
}
