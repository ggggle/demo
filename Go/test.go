package main

import (
    "fmt"
    "time"
)

func main()  {
    fmt.Println("start run")
    go func() {
        select {
        case <-time.After(time.Second *10):
        }
        fmt.Println("runtine run")
    }()
    fmt.Println("run")
    fmt.Println("end")
    select {
    case <-time.After(time.Second * 20):
        
    }
}