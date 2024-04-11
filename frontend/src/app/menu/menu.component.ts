import { Component, Input, EventEmitter, Output } from '@angular/core';
import { ThemePalette } from '@angular/material/core';
import { Router } from '@angular/router';


@Component({
  selector: 'app-menu',

  templateUrl: './menu.component.html',
  styleUrl: './menu.component.scss'
})
export class MenuComponent {
  clickedItem: 'Query' | 'Reports' | 'History' | 'Saved'|'Operations Mode' | 'My workspace'| 'Team workspaces' |'Recent' |'Shared with me'|'Trash'|'Templates'  |undefined;
  color: ThemePalette = 'accent';
  checked = false;
  disabled = true;
// @Input() chekckuserType: any ;
@Output() selectedTab = new EventEmitter<string>();

    userType: any;
    constructor(public _router: Router) {
      }
  ngOnInit(){
    this.clickedItem = 'Query';
    this.selectedTab.emit(this.clickedItem);

    // this.userType= this.checkuserType;
    
  }

  onClick(item: 'Query' | 'Reports' | 'History'| 'Saved' |'Operations Mode'| 'My workspace' |'Team workspaces' | 'Recent' |'Shared with me' | 'Trash' | 'Templates' ) {
        this.clickedItem = item;
        this.selectedTab.emit(this.clickedItem);
    
  }
}
