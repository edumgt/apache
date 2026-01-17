# DeepSeek 계열 LLM을 Docker로 설치하고 Web URI로 실행하기 (정리본)

> 목적: **Docker로 설치 → 브라우저(Web UI) 또는 HTTP API(Web URI)로 DeepSeek 계열 LLM 실행**

---

## 목차
1. [가장 쉬운 방법: Open WebUI + Ollama (웹 UI)](#1-가장-쉬운-방법-open-webui--ollama-웹-ui)
2. [OpenAI 호환 API가 필요하면: vLLM 서버 (웹 URI)](#2-openai-호환-api가-필요하면-vllm-서버-웹-uri)
3. [Docker Desktop 사용자라면: Docker Model Runner (OpenAI 호환 로컬 API)](#3-docker-desktop-사용자라면-docker-model-runner-openai-호환-로컬-api)
4. [빠른 선택 가이드](#빠른-선택-가이드)
5. [자주 겪는 이슈 체크리스트](#자주-겪는-이슈-체크리스트)

---

## 1) 가장 쉬운 방법: Open WebUI + Ollama (웹 UI)

**무엇이 좋은가?**
- 설치/운영이 단순함
- **브라우저로 바로 접속**해서 채팅 가능
- 로컬에서 모델 다운로드/실행까지 한 번에

**브라우저 접속 URI**
- `http://localhost:3000`

### (A) 올인원(권장): Open WebUI 이미지가 Ollama까지 포함

#### GPU 사용(NVIDIA)
```bash
docker run -d -p 3000:8080 --gpus=all   -v ollama:/root/.ollama   -v open-webui:/app/backend/data   --name open-webui --restart always   ghcr.io/open-webui/open-webui:ollama
```

#### CPU만 사용
```bash
docker run -d -p 3000:8080   -v ollama:/root/.ollama   -v open-webui:/app/backend/data   --name open-webui --restart always   ghcr.io/open-webui/open-webui:ollama
```

### (B) 모델 실행(예: DeepSeek-R1)
컨테이너 내부에 Ollama가 포함된 경우, Open WebUI에서 모델을 선택해도 되지만,
CLI로도 바로 실행할 수 있습니다:

```bash
ollama run deepseek-r1
```

> 참고: Ollama 모델은 첫 실행 시 다운로드가 진행될 수 있습니다.

---

## 2) OpenAI 호환 API가 필요하면: vLLM 서버 (웹 URI)

**무엇이 좋은가?**
- 서비스/앱에서 **OpenAI 호환 엔드포인트**로 호출하기 쉬움
- 성능/추론 서버로 자주 사용

**API Base URI**
- `http://localhost:8000/v1`

### Docker 실행 예시 (개념용)
> 아래는 “이런 형태로 띄운다”는 예시입니다. 모델명/옵션은 환경에 맞게 조정하세요.

```bash
docker run --gpus all -p 8000:8000   -v ~/.cache/huggingface:/root/.cache/huggingface   vllm/vllm-openai:latest   vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --dtype auto --api-key token-abc123
```

### 호출 예시(curl)
```bash
curl http://localhost:8000/v1/chat/completions   -H "Content-Type: application/json"   -H "Authorization: Bearer token-abc123"   -d '{
    "model":"deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
    "messages":[{"role":"user","content":"hello"}]
  }'
```

**포인트**
- `/v1/chat/completions` 형태는 “OpenAI 스타일” 호출 패턴입니다.
- Open WebUI에서도 “OpenAI Base URL”을 `http://host.docker.internal:8000/v1` 로 잡으면,
  vLLM을 백엔드로 붙여서 브라우저 UI로 쓸 수 있습니다(환경에 따라 주소/네트워크 설정 필요).

---

## 3) Docker Desktop 사용자라면: Docker Model Runner (OpenAI 호환 로컬 API)

**무엇이 좋은가?**
- Docker Desktop 환경에서 “로컬 모델 실행”을 빠르게 붙일 수 있음
- OpenAI 호환 API 스타일로 호출 가능

**TCP 포트 예시**
- `12434`

### 활성화 예시
```bash
docker desktop enable model-runner --tcp 12434
```

### 호출 예시(curl)
```bash
curl http://localhost:12434/engines/llama.cpp/v1/chat/completions   -H "Content-Type: application/json"   -d '{
    "model":"ai/smollm2",
    "messages":[{"role":"user","content":"Hello"}]
  }'
```

> 참고: 모델/엔진 경로는 설정/버전에 따라 달라질 수 있습니다.

---

## 빠른 선택 가이드

- **브라우저 UI로 바로 채팅하고 싶다**  
  → **Open WebUI + Ollama** (1번)

- **REST API(OpenAI 호환)로 앱/서비스에서 호출하고 싶다**  
  → **vLLM** (2번)

- **Docker Desktop 내장형 흐름으로 빠르게 테스트하고 싶다**  
  → **Docker Model Runner** (3번)

---

## 자주 겪는 이슈 체크리스트

### GPU 인식 문제
- NVIDIA GPU 사용 시:
  - Docker Desktop에서 GPU 사용 가능 설정 확인
  - `nvidia-smi`(호스트) 동작 확인
  - 컨테이너 실행 옵션에 `--gpus=all` 적용

### 포트 충돌
- `3000`, `8000`, `12434`가 이미 사용 중이면 다른 포트로 변경:
  - 예) `-p 33000:8080` (브라우저는 `http://localhost:33000`)

### Windows에서 컨테이너 ↔ 호스트 주소
- 컨테이너에서 호스트의 서비스를 부를 때 자주 쓰는 주소:
  - `host.docker.internal`
- 단, 환경/네트워크 모드에 따라 달라질 수 있음

---

## 참고 메모
- 실제 운영 목적이라면: 모델 크기(7B/14B/32B 등)와 VRAM/CPU/RAM, 배치/컨텍스트 길이에 맞춰 선택하세요.
- “딱 하나로 고정”해서 구성하려면:
  - **Windows + Docker Desktop + NVIDIA GPU 여부**만 알면 최적 조합을 바로 잡을 수 있습니다.

---

작성일: 2026-01-15 (Asia/Seoul)
