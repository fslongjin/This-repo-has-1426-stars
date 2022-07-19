package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"regexp"
	"strconv"
	"strings"
	"time"
)

type RepoInfo struct {
	RepoName string `json:"full_name"`
	Starts   int    `json:"watchers"`
}

type ReqBody struct {
	Name        string `json:"name"`
	Description string `json:"description"`
}

const (
	repoUrl     = "https://api.github.com/repos/fslongjin/This-project-has-N-stars"
	githubToken = "githubToken"
	logFile     = "log.txt"
)

var (
	regex   = regexp.MustCompile(`This-repo-has-(\d+)?-stars`)
	preStar = -1
)

//  getRepoInfo
//  @Description: 获取项目有多少个 star
//  @param repoName 项目名称
//  @return RepoInfo 仓库信息
//
func getRepoInfo(repoUrl string) (RepoInfo, error) {
	res := RepoInfo{}

	client := &http.Client{}
	req, err := http.NewRequest(http.MethodGet, repoUrl, nil)
	if err != nil {
		return res, err
	}
	req.Header.Add("Accept", "application/vnd.github.v3+json")

	resp, err := client.Do(req)
	if err != nil {
		return res, err
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return res, err
	}
	err = json.Unmarshal(body, &res)
	if err != nil {
		return res, err
	}
	return res, nil

}

//
//  updateRepoName
//  @Description: 更新仓库名称
//  @param info
//
func updateRepoName(info RepoInfo) {
	match := regex.FindStringSubmatch(info.RepoName)
	if len(match) < 2 {
		log.Println("not match: len <2", match)
		return
	}
	strStars := match[1]
	newStars, err := strconv.ParseInt(strStars, 10, 32)
	if err != nil {
		log.Println("parse int err:", err)
	}
	// 如果和之前的一致就返回
	if preStar == int(newStars) {
		log.Println("The number of stars has not changed")
		return
	}
	reqBody := ReqBody{
		Name:        fmt.Sprintf("This-repo-has-%d-stars", newStars),
		Description: fmt.Sprintf("这个仓库有%d个star，不信你试试", newStars),
	}
	reader := strings.NewReader(fmt.Sprintf("{\"name\":%s,\"description\":%s}", reqBody.Name, reqBody.Description))
	req, err := http.NewRequest(http.MethodPatch, repoUrl, reader)
	if err != nil {
		log.Println("NewRequest err:", err)
		return
	}
	req.Header.Add("Accept", "application/vnd.github.v3+json")
	req.Header.Add("Authorization", "token "+githubToken)
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		log.Println("Do err:", err)
		return
	}
	if resp.StatusCode != http.StatusOK {
		log.Print("request err:", resp.StatusCode)
	}
	preStar = int(newStars)
	log.Println("success")
}

func main() {
	f, err := os.Open(logFile)
	if err != nil {
		if !os.IsNotExist(err) {
			log.Panicf("run err ：%s", err)
		}
		f, _ = os.Create(logFile)
	}

	log.SetOutput(f)
	for {
		respInfo, err := getRepoInfo(repoUrl)
		if err != nil {
			log.Println("get repo info err:", err)
			continue
		}
		updateRepoName(respInfo)
		time.Sleep(time.Second * 3)
	}

}
