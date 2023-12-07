package main

import (
	"log"
	"time"
    "fmt"
    "context"
    "os"
    "flag"

	"github.com/myzhan/boomer"
    "saxml/client/go/sax"
    "saxml/common/platform/env"
    _ "saxml/common/platform/register" //registers a platform
)

var globalBoomer *boomer.Boomer
var globalLm *sax.LanguageModel
var ctx context.Context

func foo(){
    start := time.Now()
    time.Sleep(100 * time.Millisecond)
    elapsed := time.Since(start)
    /*
    Report your test result as a success, if you write it in locust, it will looks like this
    events.request_success.fire(request_type="http", name="foo", response_time=100, response_length=10)
    */
    globalBoomer.RecordSuccess("http", "foo", elapsed.Nanoseconds()/int64(time.Millisecond), int64(10))
}

func lm_generate() {
    
    query := "Who are you ?"
    start := time.Now()
    response, err := globalLm.Generate(ctx, query)
    //time.Sleep(1000 * time.Millisecond)
    elapsed := time.Since(start)
    if err == nil {
        /*
        Report your test result as a success, if you write it in locust, it will looks like this
        events.request_success.fire(request_type="http", name="foo", response_time=100, response_length=10)
        */
        response_len := 0
        for _, generate := range response {
           response_len += len(generate.Text)
        } 

        globalBoomer.RecordSuccess("saxml.client", "lm.Generate", elapsed.Nanoseconds()/int64(time.Millisecond), int64(response_len)) 
    } else {

        globalBoomer.RecordFailure("saxml.client", "lm.Generate", elapsed.Nanoseconds()/int64(time.Millisecond), err.Error())  
    }

    
}



func main(){
    log.SetFlags(log.LstdFlags | log.Lshortfile)

    task := &boomer.Task{
        Name: "lm.Generate",
        // The weight is used to distribute goroutines over multiple tasks.
        Weight: 10,
        Fn: lm_generate,
    }

    model, err := sax.Open("/sax/test/llama7bfp16tpuv5e")
    if err != nil {
        fmt.Print("Error opening the model")
    } else {
        globalLm  = model.LM()
    }

    os.Setenv("SAX_ROOT", "gs://jk-saxml-admin-bucket/sax-root")
    
    ctx = context.Background()
    env.Get().Init(ctx)

    //numClients := 1
	//spawnRate := float64(1)
	//globalBoomer = boomer.NewStandaloneBoomer(numClients, spawnRate)
	//globalBoomer.AddOutput(boomer.NewConsoleOutput()) 
    // Start tasks
    //globalBoomer.Run(task)
	if !flag.Parsed() {
        fmt.Println("Parsing flags")
		flag.Parse()
	}

    globalBoomer = boomer.NewBoomer(boomer.masterHost, boomer.masterPort)
    globalBoomer.Run(task)
}


