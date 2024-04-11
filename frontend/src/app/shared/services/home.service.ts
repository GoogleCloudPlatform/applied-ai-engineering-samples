import { Injectable } from '@angular/core';
import { HttpHeaders, HttpClient, HttpErrorResponse } from '@angular/common/http';
import { catchError, throwError, BehaviorSubject } from 'rxjs';
import { Observable } from 'rxjs';
import { ENDPOINT_TALK2DATA } from '../../../assets/constants'

@Injectable({
  providedIn: 'root'
})
export class HomeService {
  public databaseSubject = new BehaviorSubject(null);
  databaseObservable = this.databaseSubject.asObservable();
  private databaseList: any;
  private selectedDb: any;
  public checkuserType: any;
  public selectedDBType: any;
  DBType: any;
  config: any;

  constructor(public http: HttpClient) { }

  ngOnInit() { }
  getAvailableDatabases(): any {
    const header = {
      'Content-Type': 'application/json',
    }
    const requestOptions = {
      headers: new HttpHeaders(header),
    };

    return this.http.get(ENDPOINT_TALK2DATA + '/available_databases', requestOptions).pipe(catchError(this.handleError))
  }
  sqlSuggestionList(databasetype: any, dbtype: any) {

    const header = {
      'Content-Type': 'application/json',
    }
    const requestOptions = {
      headers: new HttpHeaders(header),
    };

    const body =
    {
      "user_database": databasetype
    }
    this.selectedDBType = dbtype;

    return this.http.post(ENDPOINT_TALK2DATA + '/get_known_sql', body, requestOptions)
      .pipe(catchError(this.handleError));

  }
  returnEndpointURL() {
    return ENDPOINT_TALK2DATA;
  }
  generateSql(userQuestion: any, databasetype: any) {

    const header = {
      'Content-Type': 'application/json',
    }
    const requestOptions = {
      headers: new HttpHeaders(header),
    };
    const body =
    {
      "user_question": userQuestion,
      "user_database": databasetype
    }
    let endpoint = ENDPOINT_TALK2DATA;

    return this.http.post(endpoint + "/generate_sql", body, requestOptions)
      .pipe(catchError(this.handleError));

  }
  private handleError(error: HttpErrorResponse) {
    if (error.error instanceof ErrorEvent) {
      console.error('An error occurred:', error.error);
    } else {
    }
    return throwError(
      'Something bad happened; please try again later.');
  }
  setAvailableDBList(databaseList: string) {
    this.databaseList = databaseList;
  }
  getAvailableDBList(): string {
    return this.databaseList;
  }
  setselectedDb(databaseList: any) {
    this.selectedDb = databaseList;
  }
  getselectedDb(): string {
    return this.selectedDb;
  }

  generateResultforSql(query: any, databasetype: any) {
    const header = {
      'Content-Type': 'application/json',
    }
    const requestOptions = {
      headers: new HttpHeaders(header),
    };
    const body =
    {
      "generated_sql": query,
      "user_database": databasetype
    }
    let endpoint = ENDPOINT_TALK2DATA;

    return this.http.post(endpoint + "/run_query", body, requestOptions)
      .pipe(catchError(this.handleError));
  }
  thumbsUp(sql: any, selectedDb: any) {

    const header = {
      'Content-Type': 'application/json',
    }
    const requestOptions = {
      headers: new HttpHeaders(header),
    };
    const body =
    {
      user_database: selectedDb,
      generated_sql: sql.example_generated_sql,
      user_question: sql.example_user_question
    }
    let endpoint = ENDPOINT_TALK2DATA;
    return this.http.post(endpoint + "/embed_sql", body, requestOptions)
      .pipe(catchError(this.handleError));
  }

  generateViz(question: any, query: any, result: any) {
    const header = {
      'Content-Type': 'application/json',
    }
    const requestOptions = {
      headers: new HttpHeaders(header),
    };
    const body =
    {
      "user_question": question,
      "sql_generated": query,
      "sql_results": result
    }
    return this.http.post(ENDPOINT_TALK2DATA + "/generate_viz", body, requestOptions)
      .pipe(catchError(this.handleError));
  }
}
