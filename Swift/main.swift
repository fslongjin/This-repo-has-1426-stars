import Foundation
let githubToken = ""
let repoUrl = "https://api.github.com/repos/fslongjin/This-project-has-N-stars"

/// MARK: Tool 
func getDictionaryFromJSONString(jsonString:String) ->NSDictionary{
    let jsonData:Data = jsonString.data(using: .utf8)!
    let dict = try? JSONSerialization.jsonObject(with: jsonData, options: .mutableContainers)
    if dict != nil {
        return dict as! NSDictionary
    }
    return NSDictionary()
}
func jsonToData(jsonDic:Dictionary<String, Any>) -> Data? {

    if (!JSONSerialization.isValidJSONObject(jsonDic)) {
        print("is not a valid json object")
        return nil
    }

    //利用自带的json库转换成Data
    //如果设置options为JSONSerialization.WritingOptions.prettyPrinted，则打印格式更好阅读
    let data = try? JSONSerialization.data(withJSONObject: jsonDic, options: [])
    //输出json字符串
    return data
}

/// MARK: func 
func getStart() {
    let url:URL = URL(string: repoUrl)!
    // 发送HTTP请求的的session对象
    let session = URLSession.shared
    // 构建请求request
    var request = URLRequest(url: url)
    request.httpMethod = "GET"
    request.setValue("token " + githubToken, forHTTPHeaderField: "Authorization")
    // 发一个get请求
    let task = session.dataTask(with: request as URLRequest) {(
        data, response, error) in

        guard let data = data, let _:URLResponse = response, error == nil else {
            print("getStart Error", error!)
            return
        }
        let dataString =  String(data: data, encoding: String.Encoding.utf8)
        let dict = getDictionaryFromJSONString(jsonString: dataString!)
        updateProjectName(name: dict["full_name"] as! String, stars: dict["watchers"] as! Int)
    }
    task.resume()
}

func updateProjectName(name:String, stars:Int) {
    let array = name.components(separatedBy:"-")
    let currentStars:String = array[array.count - 2];
    if (Int(currentStars) != stars - 100) {
        let newName = "This-repo-has-\(stars)-stars"
        let newData:[String: String] = [
            "name": newName,
            "description": "这个仓库有\(stars)个star，不信你试试",
        ]
        let newDataJson = jsonToData(jsonDic: newData)
        let url:URL = URL(string: repoUrl)!
        let session = URLSession.shared
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("token " + githubToken, forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = newDataJson! as Data
        let task = session.dataTask(with: request as URLRequest) {(
            data, response, error) in
            guard let data = data, let _:URLResponse = response, error == nil else {
                print("getStart Error", error!)
                return
            }
            let dataString =  String(data: data, encoding: String.Encoding.utf8)
            let dict = getDictionaryFromJSONString(jsonString: dataString!)
            print(dict)
        }
        task.resume()
    }
}
func loop () {
    // ⭐️ 
    getStart()
}

// 入口函数
func main() {
    while (true) {
        loop()
        Thread.sleep(forTimeInterval: 3.0)
    }
}

// gogogo
main()