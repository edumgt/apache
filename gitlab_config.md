## https ( SSL ) 사용에 대한 우회방법

## git ssl 검증 무력화
```
git config --global http.sslVerify false
```


## Windows의 Git Credential Manager(GCM)가 “HTTP 원격으로 자격증명 전송”을 차단해서 나는 겁니다. 방금 설정하신 credential.unsafeAllowedHosts / GCM_ALLOW_UNENCRYPTED_HTTP는 이 에러를 푸는 키가 아니고, GCM 쪽에서 요구하는 키는 credential.allowUnsafeRemotes (또는 환경변수 GCM_ALLOW_UNSAFE_REMOTES) 입니다.
```
git config --global credential.allowUnsafeRemotes true
git config --global --get credential.allowUnsafeRemotes
```
## 로컬 GitLab이 ID/Password로 되면 그대로 입력
## 예를들어 root 접속 사용 시 
```
docker exec -it gitlab bash -lc "cat /etc/gitlab/initial_root_password"
```

