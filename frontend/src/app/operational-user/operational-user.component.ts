import { Component, ChangeDetectorRef, Output, EventEmitter } from '@angular/core';
import { LoginService } from '../shared/services/login.service';
import { FormControl, FormGroup } from '@angular/forms';
import { HomeService } from '../shared/services/home.service';
import { MatTabChangeEvent } from '@angular/material/tabs';
import { MatTableDataSource } from '@angular/material/table';
import { MatSnackBar } from '@angular/material/snack-bar';

export interface Tabledata{
  city_id: string;

  
}


const ELEMENT_DATA: any[] = [
  ];



@Component({
  selector: 'app-operational-user',

  templateUrl: './operational-user.component.html',
  styleUrl: './operational-user.component.scss'
})
export class OperationalUserComponent {
  userLoggedIn: boolean = false;
  showchatboot: boolean = false;
  photoURL: any;
  generateSuccessMsg: boolean = false;
  insightResults: any[] = [];
  displayedColumns: string[] = [];
  dataSource : any[] = [];
// dataSource = new MatTableDataSource();
showProgressPreviewBar: boolean = false;
resultLoader: boolean = false;
selectedIndex:number =1;
  thData :any[]=[];
  
  isSuggestions : boolean = true;
  suggestionList: any;
   
  showResult: boolean = false;
    generatedSql: any ={example_user_question: '',
        example_generated_sql: ''};
    emptyMsg: string = '';
    errMsg: string = '';
    @Output() updateStyleEvent = new EventEmitter<boolean>();



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

  ngOnInit(){
this.dataSource = ELEMENT_DATA;
  this.homeService.databaseObservable.subscribe((response: any) =>{
    if(response){
        this.showResult = false;

        this.suggestionList = JSON.parse(response);
    }
    
  })
  }

  onSubmit(){}
  generate() {
    this.showResult = false;
    this.showProgressPreviewBar = true;
    this.errMsg = '';
     this.homeService.generateSql(this.sqlSearchForm.controls.name?.value, this.homeService.getselectedDb()).subscribe((response:any) =>{
        if(response && response.ResponseCode === 200){
            this.showResult = true;
            this.generatedSql.example_user_question = this.sqlSearchForm.controls.name?.value;
            this.generatedSql.example_generated_sql= response.GeneratedSQL;
            this.showProgressPreviewBar= false;

            this.selectedIndex = 1;
            this.change.markForCheck();
        }
        else{
            this.errMsg = response.Error;
            this.showProgressPreviewBar = false;

        }
    })
  }

  suggestionResult(selectedsql: any){
    this.showResult = true;
    this.generatedSql = selectedsql;
    this.updateStyleEvent.emit(this.showResult);

    this.selectedIndex = 1;
    this.change.markForCheck();

  }
  generateResultData(event: MatTabChangeEvent){
    //  this.dataSource =[];
    // this.dataSource = new MatTableDataSource();
    this.displayedColumns =[];
    const tab = event.tab.textLabel;
    this.resultLoader = true;

    if(tab==="Result")
     {
        this.homeService.generateResultforSql(this.generatedSql.example_generated_sql.replace(/(\r\n|\n|\r)/gm, "") , this.homeService.getselectedDb()).subscribe((res : any) =>{
        // });
        // let str = 'select st.city_id from retail.sales as s join retail.stores as st on s.id_store = st.id_store group by st.city_id order by count(*) desc limit 1';
        //    this.homeService.generateResultforSql(str).subscribe((res : any) =>{
          if(res && res.ResponseCode === 200){
                const data = JSON.parse(res.KnownDB);
                if(data.length === 0){
                    this.emptyMsg ='No data found';
                    this.resultLoader = false;
                }else{
                    this.emptyMsg ='';
                    for(var obj in data){
                        if(data.hasOwnProperty(obj)){
                        for(var prop in data[obj]){
                            if(data[obj].hasOwnProperty(prop)){
                               this.displayedColumns.push(prop);
                            }
                        }
                    }
                    }
                    
                    //  this.dataSource.push(data);
                     this.resultLoader = false;
                    //  this.dataSource = [...this.dataSource]
                  this.dataSource = data;
              

                }
            }    
        });
          }
          else{
            this.resultLoader = false;

          }
  }
  thumbsUp(sql: any){

    const sqlExist = this.suggestionList.some((res: { example_user_question: any; example_generated_sql: any; }) => res.example_user_question == sql.example_user_question && res.example_generated_sql === sql.example_generated_sql)
    console.log(sqlExist,'thumsup')
    if(!sqlExist){
        this.homeService.thumbsUp(sql, this.homeService.getselectedDb()).subscribe((res:any) => {
        if(res && res.ResponseCode === 201)
    {
        this.showSnackbarCssStyles(res?.Message, 'Close', '4000')

    }else{
        this.showSnackbarCssStyles(res?.Error, 'Close', '4000')

    }})
    }else{
            this.showSnackbarCssStyles('Data is present in the suggestion list', 'Close', '4000')
    
        
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

}
