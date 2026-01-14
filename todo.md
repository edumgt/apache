가능해요. 지금 올려주신 main.py는 게시판 API만 있는 상태라서(태그도 Health/Posts만 있음) 

main

, 여기에 OCR 엔진(Tesseract)을 FastAPI에서 직접 호출하는 엔드포인트를 추가하면 됩니다.

아래는 “같은 컨테이너 안에서 Tesseract 설치 + FastAPI가 subprocess로 OCR 실행” 방식(가장 단순/안정) 기준입니다.

1) requirements.txt 추가

파일 업로드를 받으려면 python-multipart가 필요합니다. (UploadFile/File 사용 시)

requirements.txt에 아래를 추가하세요. 

requirements

python-multipart==0.0.9

2) Dockerfile에 Tesseract(한글 포함) 설치 추가

기존 Dockerfile의 apt-get install 부분에 tesseract 패키지를 추가하세요.

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      curl \
      tesseract-ocr \
      tesseract-ocr-kor \
 && rm -rf /var/lib/apt/lists/*


tesseract-ocr-kor가 한글 학습데이터입니다. (컨테이너 안에서 tesseract --list-langs로 확인 가능)

3) main.py에 OCR API 추가
(1) import 추가

main.py 상단 import에 UploadFile, File을 추가하세요. 

main

from fastapi import FastAPI, HTTPException, Query, Path, Body, status, UploadFile, File


그리고 아래 import들도 추가:

import shutil
import subprocess
import tempfile
from pathlib import Path as P

(2) Swagger 태그에 OCR 추가

openapi_tags에 한 줄 추가: 

main

openapi_tags = [
    {"name": "Health", "description": "서버 상태/헬스체크"},
    {"name": "Posts", "description": "게시글 CRUD 및 검색/정렬/페이징"},
    {"name": "OCR", "description": "이미지 OCR (Tesseract)"},
]

(3) 응답 모델 + 엔드포인트 추가

파일 맨 아래(예: delete_post() 아래)에 붙여 넣으세요. 

main

class OcrResponse(BaseModel):
    text: str = Field(..., description="추출된 텍스트")
    lang: str = Field(..., description="사용한 언어 코드 (예: kor+eng)")
    psm: int = Field(..., description="Tesseract Page Segmentation Mode")


@app.post(
    "/api/ocr",
    tags=["OCR"],
    summary="이미지 OCR (Tesseract)",
    description="이미지(PNG/JPG 등)를 업로드하면 OCR로 텍스트를 추출합니다.",
    response_model=OcrResponse,
)
def ocr_image(
    file: UploadFile = File(..., description="OCR 대상 이미지 파일"),
    lang: str = Query("kor+eng", description="Tesseract 언어 코드 (예: kor, eng, kor+eng)"),
    psm: int = Query(6, ge=0, le=13, description="Tesseract PSM (기본 6: 단일 블록 텍스트)"),
):
    # 간단한 타입 체크(원하면 더 엄격히)
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능합니다.")

    suffix = P(file.filename or "").suffix or ".png"

    with tempfile.TemporaryDirectory() as td:
        td_path = P(td)
        in_path = td_path / f"input{suffix}"
        out_base = td_path / "out"

        # 업로드 파일 저장
        with open(in_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # tesseract 실행
        cmd = [
            "tesseract",
            str(in_path),
            str(out_base),
            "-l",
            lang,
            "--psm",
            str(psm),
        ]
        p = subprocess.run(cmd, capture_output=True, text=True)

        if p.returncode != 0:
            raise HTTPException(status_code=500, detail=(p.stderr or "tesseract failed"))

        txt_path = out_base.with_suffix(".txt")
        text = txt_path.read_text(encoding="utf-8", errors="ignore")

        return OcrResponse(text=text, lang=lang, psm=psm)

4) 실행
docker compose up --build

5) 테스트 (PowerShell)
curl -X POST "http://localhost:8000/api/ocr?lang=kor%2Beng&psm=6" `
  -F "file=@.\image.png"

참고: “OCR 엔진을 별도 컨테이너로” 분리하고 싶으면

FastAPI는 업로드만 받고

옆에 rapid-ocr-api 같은 OCR 서버 컨테이너를 붙인 뒤

FastAPI가 HTTP로 OCR 서버를 호출하는 구조도 가능합니다(스케일/분리 운영에 좋음)