import { CUSTOM_ELEMENTS_SCHEMA, NgModule, importProvidersFrom } from "@angular/core";
import { AppComponent } from "./app.component";
import { LoginComponent } from "./login/login.component";
import { LoginButtonComponent } from "./login-button/login-button.component";
import { LoginService } from "./shared/services/login.service";
import { SharedService } from "./shared/services/shared.service";
import { provideFirestore,getFirestore } from "@angular/fire/firestore";
import { initializeApp, provideFirebaseApp } from "@angular/fire/app";
import { BrowserModule } from "@angular/platform-browser";
import { UserJourneyComponent } from "./user-journey/user-journey.component";
import { AppRoutingModule } from "./app-routing.module";
import { HomeComponent } from "./home/home.component";
import { HeaderComponent } from "./header/header.component";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatIconModule } from "@angular/material/icon";
import { MatButtonModule } from "@angular/material/button";
import { RouterLink } from "@angular/router";
import { MatTabsModule } from "@angular/material/tabs";
import { MatDividerModule } from "@angular/material/divider";
import { MatSelectModule } from "@angular/material/select";
import { MatInputModule } from "@angular/material/input";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatAutocompleteModule } from "@angular/material/autocomplete";
import { CommonModule, NgFor, NgIf } from "@angular/common";
import { BrowserAnimationsModule } from "@angular/platform-browser/animations";
import {MatListModule} from '@angular/material/list';
import {MatSidenavModule} from '@angular/material/sidenav';
import { MatExpansionModule} from '@angular/material/expansion';
import { MenuComponent } from "./menu/menu.component";
import { FormsModule, ReactiveFormsModule } from "@angular/forms";
import { BusinessUserComponent } from "./business-user/business-user.component";
import {MatTableModule} from '@angular/material/table';
import {MatCardModule} from '@angular/material/card';
import { HttpClientModule } from '@angular/common/http';
import { HomeService } from './shared/services/home.service';
import { provideAuth, getAuth } from '@angular/fire/auth';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import {ClipboardModule} from '@angular/cdk/clipboard';
import {MatSlideToggleModule} from '@angular/material/slide-toggle';
import { OperationalUserComponent } from './operational-user/operational-user.component';
import { NgChartsModule } from 'ng2-charts';
import { ReportsComponent } from './reports/reports.component';
import { TechnicalUserComponent } from './technical-user/technical-user.component';
import { AngularFireModule } from '@angular/fire/compat';
import { AngularFirestoreModule } from '@angular/fire/compat/firestore';
import { AngularFireAuth, AngularFireAuthModule } from '@angular/fire/compat/auth';
import { UserPhotoComponent } from "./user-photo/user-photo.component";
import { PrismComponent } from "./prism/prism.component";
import 'prismjs/components/prism-sql';
import { MatPaginatorModule } from "@angular/material/paginator";
import { OverlayModule } from "@angular/cdk/overlay";
import { LoadPopupComponent } from "./load-popup/load-popup.component";
import { SavedQueriesComponent } from './saved-queries/saved-queries.component';
import { HistoryComponent } from './history/history.component';
import { GoogleChartsModule } from "angular-google-charts";
import {MatRadioModule} from '@angular/material/radio';
import {firebaseConfig} from "../assets/constants"
@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    LoginButtonComponent,
    UserJourneyComponent,
    HomeComponent,
    HeaderComponent,
    MenuComponent,
    BusinessUserComponent,OperationalUserComponent,
    ReportsComponent,
    TechnicalUserComponent,
    UserPhotoComponent,
    PrismComponent,
    LoadPopupComponent,
    SavedQueriesComponent,
    HistoryComponent
  ],
  imports: [
    CommonModule,
    BrowserModule,
    ReactiveFormsModule,
    FormsModule,
    BrowserAnimationsModule,
    AppRoutingModule,
    // provideFirebaseApp(() => initializeApp(firebaseConfig)),
    // provideFirestore(() => getFirestore()),
    // provideAuth(() => getAuth()),

    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    RouterLink,
    MatTabsModule,
    MatDividerModule,
     NgIf,
    NgFor,
    MatSelectModule,
    MatInputModule,
    MatFormFieldModule,
    MatAutocompleteModule,
    MatListModule,
    MatSidenavModule,
    MatTableModule,
    MatExpansionModule,
    MatCardModule,
    HttpClientModule,
    MatProgressSpinnerModule,
    MatSnackBarModule,
    ClipboardModule,
    MatSlideToggleModule,
    NgChartsModule,
    AngularFireModule.initializeApp(firebaseConfig),
    AngularFirestoreModule,
    AngularFireAuthModule,
    MatPaginatorModule,
    OverlayModule,
    GoogleChartsModule,
    MatRadioModule
  ],
  providers: [
    importProvidersFrom([
        provideFirebaseApp(() => initializeApp(firebaseConfig)),
        provideFirestore(() => getFirestore()),
        provideAuth(() => getAuth()),
   LoginService,
   SharedService,
   HomeService,
   AngularFireAuth
   
    ]),
  ],
  bootstrap: [AppComponent],
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class AppModule { }
