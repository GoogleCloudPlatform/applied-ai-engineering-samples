import {Component} from '@angular/core';
import {MatTableModule} from '@angular/material/table';

export interface ReportData {
  name: string;
  ownedBy: string;
  lastOpened: string;
}

const ELEMENT_DATA: ReportData[] = [
  { name: 'Analysis Jan 2022', ownedBy: 'John Smith', lastOpened: 'Feb 10, 2022'},
  { name: 'Analysis Jan 2022', ownedBy: 'John Smith', lastOpened: 'Feb 10, 2022'},
  { name: 'Analysis Jan 2022', ownedBy: 'John Smith', lastOpened: 'Feb 10, 2022'},
  { name: 'Analysis Jan 2022', ownedBy: 'John Smith', lastOpened: 'Feb 10, 2022'},
  { name: 'Analysis Jan 2022', ownedBy: 'John Smith', lastOpened: 'Feb 10, 2022'},
  { name: 'Analysis Jan 2022', ownedBy: 'John Smith', lastOpened: 'Feb 10, 2022'}
];

/**
 * @title Basic use of `<table mat-table>`
 */
@Component({
    selector: 'app-results',
    templateUrl: './reports.component.html',
    styleUrl: './reports.component.scss'
})
export class ReportsComponent {
  displayedColumns: string[] = ['name', 'ownedBy', 'lastOpened'];
  dataSource = ELEMENT_DATA;
}
