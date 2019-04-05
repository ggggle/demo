package main

import (
    "os"
    "fmt"
    "io/ioutil"
    "strings"
)

func getContent(path string) string {
    f, err := os.Open(path)
    if err != nil {
        fmt.Println(err)
        return ""
    }
    defer f.Close()
    contents, _ := ioutil.ReadAll(f)
    return string(contents)
}

func parseFH(efuContent string) []string {
    all_fh := make([]string, 0)
    lines := strings.Split(efuContent, "\n")
    // 第一行是头标题
    for i, lens := 1, len(lines); i < lens; i++ {
        line_split := strings.Split(lines[i], "\"")
        if (len(line_split) > 1) {
            path_split := strings.Split(line_split[1], "\\")
            if path_split_len := len(path_split); path_split_len > 1 {
                file_name := path_split[path_split_len-1]
                if !strings.Contains(file_name, "-") {
                    continue
                }
                // 去除文件名中的空格
                file_name = strings.Replace(file_name, " ", "", -1)
                name_split := strings.Split(file_name, ".")
                // 只处理常规项
                if len(name_split) == 2 {
                    all_fh = append(all_fh, strings.ToUpper(name_split[0]))
                }
            }
        }
    }
    return all_fh
}

func getDuplicate(allFH []string) {
    fh_map := make(map[string]bool)
    for _, v := range allFH {
        if _, exist := fh_map[v]; exist {
            fmt.Println(v)
        } else {
            fh_map[v] = true
        }
    }
}

func main() {
    getDuplicate(parseFH(getContent("all.efu")))
}
