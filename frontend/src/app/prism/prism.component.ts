import { Component, Input, EventEmitter, Output, ViewChild, ElementRef } from '@angular/core';
import * as Prism from 'prismjs';

@Component({
  selector: 'app-prism',

  templateUrl: './prism.component.html',
  styleUrl: './prism.component.scss'
})
export class PrismComponent {
  @ViewChild('codeEle') codeEle!: ElementRef;
  @Input() code?: string;
  @Input() language?: string;

  constructor() { }

  ngAfterViewInit() {
    Prism.highlightElement(this.codeEle.nativeElement);
  }
  ngOnChanges(changes: any): void {
    if (changes?.code) {
      if (this.codeEle?.nativeElement) {
        this.codeEle.nativeElement.textContent = this.code;
        Prism.highlightElement(this.codeEle.nativeElement);
      }
    }
  }
}
