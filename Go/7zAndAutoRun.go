//配合7z.exe自动提取压缩包的内容并对其进行处理
package main

import (
    "os/exec"
    "bytes"
    "strings"
    "fmt"
    "regexp"
    "errors"
    "os"
    "sort"
    "strconv"
)

var EXTRA_FAST_DATA_DIR string = "./fast_data/"
var PARSE_EXE_DIR_PATH string = "../new/"
var OUTPUT_DIR string = "./out/"

func GetIncludeFile(zipFile string) (fileList []string) {
    args := []string{"l", zipFile}
    cmd := exec.Command("7z.exe", args...)
    w := bytes.NewBuffer(nil)
    cmd.Stdout = w
    cmd.Run()
    result := string(w.Bytes())
    reg,_ := regexp.Compile("(\\w+).dat")
    split := strings.Split(result, "\n")
    for _, v := range split{
        str := reg.FindString(v)
        if len(str) > 0{
            fileList = append(fileList, str)
            //fmt.Println(str)
        }
    }
    return
}

func ExtraOneFile(fileName string, zipFile string){
    fmt.Println("提取" + fileName + " from " + zipFile)
    args := []string{"e", zipFile, "-o" + EXTRA_FAST_DATA_DIR, fileName}
    cmd := exec.Command("7z.exe", args...)
    cmd.Run()
}

func FastParse(fileName string){
    date, data_type, e := GetDateType(fileName)
    if e==nil{
        args := []string{EXTRA_FAST_DATA_DIR + fileName, date, data_type}
        cmd := exec.Command(PARSE_EXE_DIR_PATH + "Level2slice.exe", args...)
        fmt.Printf("parse %v\n", args)
        cmd.Run()
    }else {
        fmt.Println(e.Error())
    }
    os.Remove(EXTRA_FAST_DATA_DIR + fileName)
}

func CleanAnd7z(fileName string)  {
    dataPath := "./data/"
    defer func(dataPath string) {
        if recover()!=nil{
            fmt.Println("CleanAnd7z error")
        }
        os.RemoveAll(dataPath)
    }(dataPath)
    date, data_type,_ := GetDateType(fileName)
    args := []string{"a", "-t7z", OUTPUT_DIR + data_type + "/" + date + ".7z", dataPath + "*"}
    cmd := exec.Command("7z.exe", args...)
    cmd.Run()
}

func GetDateType(fileName string) (date string, data_type string, err error) {
    defer func() {
        if recover()!=nil{
            err = errors.New("error " + fileName)
        }
    }()
    fileRune := []rune(fileName)
    //0 上交所  1 深交所
    if strings.Contains(fileName, "SZ5FAST"){
        data_type = "1"
        date = string(fileRune[7:15])
    } else {
        data_type = "0"
        date = string(fileRune[6:14])
    }
    return
}

func ParseFileList(fileList []string) (oneDayMap map[string][]int) {
    oneDayMap = make(map[string][]int)
    for _, v := range fileList{
        vrune := []rune(v)
        part1 := string(vrune[0:len(vrune)-4])
        str_split := strings.Split(part1, "_")
        time, _ := strconv.Atoi(str_split[1])
        oneDayMap[str_split[0]] = append(oneDayMap[str_split[0]], time)
    }
    return
}

func main()  {
    filePath := "Z:/FAST_SZ_201711.7z"
    fileList := GetIncludeFile(filePath)
    if (strings.Contains(filePath, "_SZ_")){
        oneDayMap := ParseFileList(fileList)
        for k, v := range oneDayMap{
            sort.Ints(v)
            for _, time := range v{
                time_str := strconv.Itoa(time)
                fileName := k + "_" + time_str + ".dat"
                ExtraOneFile(fileName, filePath)
                FastParse(fileName)
            }
            CleanAnd7z(k + ".dat")
        }
    } else {
        for _, v := range fileList{
            ExtraOneFile(v, filePath)
            FastParse(v)
            CleanAnd7z(v)
        }
    }
}