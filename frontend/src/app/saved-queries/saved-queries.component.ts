import {Component} from '@angular/core';
import {MatTableModule} from '@angular/material/table';

/**
 * @title Basic use of `<table mat-table>`
 */
@Component({
    selector: 'app-saved-queries',
    templateUrl: './saved-queries.component.html',
    styleUrl: './saved-queries.component.scss'
})
export class SavedQueriesComponent {
  displayedColumns: string[] = ['name', 'ownedBy', 'lastOpened'];
}
