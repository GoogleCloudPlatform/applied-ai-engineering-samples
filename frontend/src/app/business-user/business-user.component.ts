import { Component, ChangeDetectorRef, Output, EventEmitter } from '@angular/core';
import { LoginService } from '../shared/services/login.service';
import { FormControl, FormGroup } from '@angular/forms';
import { HomeService } from '../shared/services/home.service';
import { MatTabChangeEvent } from '@angular/material/tabs';
import { MatTableDataSource } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';
import { ChartConfiguration } from 'chart.js';
import { format } from 'sql-formatter';
import { ChartType } from 'angular-google-charts';


export interface Tabledata {
  city_id: string;


}


const ELEMENT_DATA: any[] = [];

@Component({
  selector: 'app-business-user',
  templateUrl: './business-user.component.html',
  styleUrl: './business-user.component.scss'
})
export class BusinessUserComponent {
  userLoggedIn: boolean = false;
  showchatboot: boolean = false;
  photoURL: any;
  generateSuccessMsg: boolean = false;
  insightResults: any[] = [];
  displayedColumns: string[] = [];
  dataSource: any[] = [];
  // dataSource = new MatTableDataSource();
  showProgressPreviewBar: boolean = false;
  resultLoader: boolean = false;
  selectedIndex: number = 1;
  thData: any[] = [];

  isSuggestions: boolean = true;
  suggestionList: any;

  showResult: boolean = false;
  generatedSql: any = {
    example_user_question: '',
    example_generated_sql: '', unfilteredSql: ''
  };
  emptyMsg: string = '';
  errMsg: string = '';
  @Output() updateStyleEvent = new EventEmitter<boolean>();
  setErrorCSS: boolean = false;

  public barChartLegend = true;
  public barChartPlugins = [];

  public barChartData: ChartConfiguration<'bar'>['data'] = {
    labels: ['2006', '2007', '2008', '2009', '2010', '2011', '2012'],
    datasets: [
      { data: [65, 59, 80, 81, 56, 55, 40], label: 'Series A' },
      { data: [28, 48, 40, 19, 86, 27, 90], label: 'Series B' }
    ]
  };

  public barChartOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: false,
  };
  isOpen: boolean = false;
  dataSet: string | undefined;
  showChart: boolean = false;
  pType = ChartType.PieChart;
  pCols = ['Value', 'Count'];
  pOpts = {
    width: 450,
    height: 250,

    backgroundColor: '#E4E4E4',
    'opacity': 100
    ,
    chartArea: {
      left: 10,
      right: 10, // !!! works !!!
      bottom: 20,  // !!! works !!!
      top: 20,
      width: "100%",
      height: "100%"
    },
    'legend': { 'position': 'bottom' }
  };
  pData = [['Value1', 1], ['Value2', 2], ['Value3', 3]];
  demo: any;
  result: any;
  res_data: any;
  showLoader: boolean = false;
  selectedFeedbackOption: any;
  dataSetName!: string;


  constructor(public loginService: LoginService, public homeService: HomeService,
    private snackBar: MatSnackBar, private change: ChangeDetectorRef) {
    this.loginService.getUserDetails().subscribe((res: any) => {
      this.userLoggedIn = true;
      this.photoURL = res?.photoURL
    });
  }
  sqlSearchForm = new FormGroup({
    name: new FormControl(),
  });

  onClickMarketingAssi() {
    this.showchatboot = true
  }

  ngOnInit() {
    this.dataSource = ELEMENT_DATA;
    this.homeService.databaseObservable.subscribe((response: any) => {
      if (response) {
        this.showResult = false;
        this.suggestionList = JSON.parse(response);
      }
      this.dataSet = this.homeService.getselectedDb();
      this.dataSetName = this.homeService.getselectedDbName()
    });
  }

  onSubmit() { }
  generate() {
    if (this.sqlSearchForm.controls.name?.value !== null) {
      this.showResult = false;
      this.showProgressPreviewBar = true;
      this.errMsg = '';
      this.homeService.generateSql(this.sqlSearchForm.controls.name?.value, this.homeService.getselectedDb()).subscribe((response: any) => {
        if (response && response.ResponseCode === 200) {
          this.showResult = true;
          this.generatedSql.example_user_question = this.sqlSearchForm.controls.name?.value;
          this.generatedSql.example_generated_sql = response.GeneratedSQL;
          this.generatedSql.unfilteredSql = response.GeneratedSQL;
          this.showProgressPreviewBar = false;

          this.selectedIndex = 1;
          this.change.markForCheck();
        }
        else {
          this.errMsg = response.Error;
          this.showProgressPreviewBar = false;

        }
      })
    } else {
      this.setErrorCSS = true;
    }
  }

  suggestionResult(selectedsql: any) {
    this.showResult = true;

    // this.generatedSql = selectedsql;
    this.generatedSql.example_user_question = selectedsql.example_user_question;
    this.generatedSql.example_generated_sql = format(selectedsql.example_generated_sql, { language: 'mysql' });
    this.generatedSql.unfilteredSql = selectedsql.example_generated_sql;

    this.updateStyleEvent.emit(this.showResult);

    this.selectedIndex = 1;
    this.change.markForCheck();

  }
  generateResultData(event: MatTabChangeEvent) {
    this.displayedColumns = [];
    const tab = event.tab.textLabel;
    this.resultLoader = true;

    if (tab === "Result") {
      // this.showChart = false;
      this.homeService.generateResultforSql(this.generatedSql.unfilteredSql, this.homeService.getselectedDb()).subscribe((res: any) => {
        // });
        // let str = 'select st.city_id from retail.sales as s join retail.stores as st on s.id_store = st.id_store group by st.city_id order by count(*) desc limit 1';
        //    this.homeService.generateResultforSql(str).subscribe((res : any) =>{
        if (res && res.ResponseCode === 200) {
          const data = JSON.parse(res.KnownDB);
          if (data.length === 0) {
            this.emptyMsg = 'No data found';
            this.resultLoader = false;
          } else {
            this.emptyMsg = '';
            for (var obj in data) {
              if (data.hasOwnProperty(obj)) {
                for (var prop in data[obj]) {
                  if (data[obj].hasOwnProperty(prop)) {
                    if (this.displayedColumns.indexOf(prop) === -1) {
                      this.displayedColumns.push(prop);
                    }
                  }
                }
              }
            }

            //  this.dataSource.push(data);
            this.resultLoader = false;
            //  this.dataSource = [...this.dataSource]
            this.dataSource = data;
            this.res_data = data;
          }
        } else {
          this.emptyMsg = res.Error;
          this.resultLoader = false;

        }
      });
    }
    else {
      this.resultLoader = false;
    }
  }
  visualizeBtn() {
    this.showLoader = true;
    this.homeService.generateViz(this.generatedSql.example_user_question, this.generatedSql.example_generated_sql, this.res_data).subscribe((res: any) => {
      const object = res.GeneratedChartjs;
      for (const [key, value] of Object.entries(object)) {
       // console.log(`Key: ${key}, Value: ${value}`);
        this.onChange(value)
      }
    })
  }
  onChange(demo: any) {
    this.showChart = true;
    this.showLoader = false;
    this.result = eval(demo);
  }
  thumbsUp(sql: any) {
    const sqlExist = this.suggestionList.some((res: { example_user_question: any; example_generated_sql: any; }) => res.example_user_question === sql.example_user_question && res.example_generated_sql === sql.unfilteredSql);
    if (!sqlExist) {
      this.homeService.thumbsUp(sql, this.homeService.getselectedDb()).subscribe((res: any) => {
        if (res && res.ResponseCode === 201) {
          this.showSnackbarCssStyles(res?.Message, 'Close', '10000')
          this.isOpen = true;

        } else {
          this.showSnackbarCssStyles(res?.Error, 'Close', '10000')
        }
      })
    } else {
      this.showSnackbarCssStyles('Data is present in the suggestion list', 'Close', '4000')
      // this.isOpen = true;
    }
  }
  showSnackbarCssStyles(content: any, action: any, duration: any) {
    let sb = this.snackBar.open(content, action, {
      duration: duration,
      //   panelClass: ['custom-snackbar', 'snackbar-success']

      panelClass: ["custom-style"]
    });
    sb.onAction().subscribe(() => {
      sb.dismiss();
    });
  }
  updateStyleItem(value: boolean) {
    this.updateStyleEvent.emit(value);
  }
  showContentCopiedMsg() {
    this.showSnackbarCssStyles("Content Copied", 'Close', '4000')
  }

  closeFeedback() {
    this.isOpen = false;
  }

  // onChange(_chartTYpe : any){
  //   this.showChart = true;
  //   const column = this.displayedColumns;
  //   const row = this.dataSource;

  //         google.charts.load('current', {'packages':['corechart']});  
  //       // Set a callback to run when the Google Visualization API is loaded.
  //       google.charts.setOnLoadCallback(function(){ drawChart(column, row) });

  //       // Callback that creates and populates a data table, 
  //       // instantiates the pie chart, passes in the data and
  //       // draws it.
  //       function drawChart(column: any[], row: any[]) {

  //       // Create the data table.
  //       var data = new google.visualization.DataTable();
  //       // const data = google.visualization.arrayToDataTable([
  //       //   row
  //       // ]);
  //       // column.forEach((element: any) => {
  //       //   data.addColumn(typeof element, element);

  //       // });

  //       data.addColumn('string', 'Product ID');
  //       data.addColumn('number', 'Count');

  //       data.addRows([
  //         ['P0125', 3],
  //         ['P0126', 1],
  //         ['P0128', 1],
  //         ['P0128', 2]
  //       ]);

  //       // Set chart options
  //       const options = {

  //                      'width':400,
  //                      'height':300
  //                     };

  //       // Instantiate and draw our chart, passing in some options.
  //       let chart: any
  //       if(_chartTYpe.target.value === 'Pie Chart'){


  //         chart= new google.visualization.PieChart(document.getElementById('chart_div')!);
  //         }
  //           if(_chartTYpe.target.value === 'Bar Chart'){


  //           chart= new google.visualization.BarChart(document.getElementById('chart_div')!);
  //           }
  //           if(_chartTYpe.target.value === 'Area Chart'){


  //             chart= new google.visualization.AreaChart(document.getElementById('chart_div')!);
  //             }
  //             if(_chartTYpe.target.value === 'Line Chart'){


  //               chart= new google.visualization.LineChart(document.getElementById('chart_div')!);
  //               }
  //               if(_chartTYpe.target.value === 'Scatter Chart'){


  //                 chart= new google.visualization.ScatterChart(document.getElementById('chart_div')!);
  //                 }
  //                 if(_chartTYpe.target.value === 'Bubble Chart'){


  //                   chart= new google.visualization.BubbleChart(document.getElementById('chart_div')!);
  //                   }

  //         chart.draw(data, options);

  //     }

  // }
  thumbsDown() {
    this.isOpen = true;
  }

  submitFeedback() {
    this.isOpen = false;
  }
  feedbackOption(val: any) {
    console.log(val);

    if (val == 0) {
      this.selectedFeedbackOption = 'Correct answer';
    } else if (val == 1) {
      this.selectedFeedbackOption = 'Easy to understand'
    } else {
      this.selectedFeedbackOption = 'Quick results'
    }
  }
}
