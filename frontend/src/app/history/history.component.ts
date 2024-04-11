import {Component} from '@angular/core';
import {MatTableModule} from '@angular/material/table';

/**
 * @title Basic use of `<table mat-table>`
 */
@Component({
    selector: 'app-history',
    templateUrl: './history.component.html',
    styleUrl: './history.component.scss'
})
export class HistoryComponent {
  displayedColumns: string[] = ['name', 'ownedBy', 'lastOpened'];
}
