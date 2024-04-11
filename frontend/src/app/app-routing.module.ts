import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { UserJourneyComponent } from './user-journey/user-journey.component';
import { HomeComponent } from './home/home.component';


const routes: Routes = [
  { path: '', component: LoginComponent },
  { path: 'user-journey', component: UserJourneyComponent },
  { path: 'home', component: HomeComponent },

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
