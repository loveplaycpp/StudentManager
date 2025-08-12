# StudentManager / Student Score Management System
<h4 align="right"><strong>English</strong> | <a href="README.md">简体中文</a>

## 1. Preface
This project was developed using Deepseek.com. There might be some deficiencies, bugs or missing features. If you find any, please submit them as issues or pull requests. This project has only been tested on the Docker image `deepnote/python:3.9`. I haven't tested it on other platforms. Please test it on this image before submitting a pull request. Thank you. This code is free of any restrictions and can be taken at will, but don't forget to give it a star.

## 2. Usage Instructions
### 1. Default Information
1. Default student account: `student ID`, default student password: `s123456`
2. Default admin account: `admin`, default admin password: `123456`
3. Default logout password: `same as admin password` ---
Please be sure to change the administrator password.
### 2. Running Methods (Change `main` to the actual file name)
#### 1. Source Code Method
1. Switch the command line working directory to the source code storage path.
2. Enter the command `python main.py`.
#### 2. Binary Method
1. Switch the command line working directory to the binary file storage path.
2. Enter the command `./main`. ---
### 3. Permissions
1. Administrator ! [](images/001.jpeg)
2. Student ! [](images/002.png)
### 4. File Storage
#### 1. File Storage Format and Location
Stored in the current location as `data.json`
#### 2. Storage Format
```json
{
  "students": {
    "001": {
      "name": "zhangsan",
      "chinese": 100.0,
      "math": 100.0,
      "english": 100.0,
      "total": 300.0,
      "average": 100.0
    }
  },
  "accounts": {
    "admin": {
      "password": "e10adc3949ba59abbe56e057f20f883e",
      "role": "admin"
    },
    "001": {
      "password": "e13f3643cc57e9c43577229842080912",
      "role": "student"
    }
  }
}
```
```
"name": "Name",
"chinese": Chinese score,
"math": Math score,
"english": English score,
"total": Total score,
"average": Average score,
"password": Password encrypted with MD5,
"role": Role, "admin" for administrator, "student" for student 
```
### 5. Log Out of the System
When an administrator logs out of the system, they may have made changes. Therefore, an administrator needs to confirm their password when logging out of the system. ! [](images/003.png)
## 3. Support
1. If you are interested in this project, please feel free to give it a star.
2. If you want to support this project, you are welcome to submit issues or pull requests.