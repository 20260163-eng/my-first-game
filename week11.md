

# 빌드 명령어
1. .spec 파일을 이용한 재빌드 명령어
pyinstaller game.spec
2. 오류 확인을 위한 디버깅용 빌드 명령어
pyinstaller --onefile --add-data "assets;assets" --name=MyGame game.py
3. 여러 폴더를 포함하는 배포용 빌드 명령어
pyinstaller --onefile --windowed ^
--add-data "assets;assets" ^
--add-data "fonts;fonts" ^
--add-data "sounds;sounds" ^
## resource_path() 를 써야 하는 이유
파이썬 코드를 PyInstaller로 실행 파일.exe로 만들때, 
이미지나 데이터 같은 외부 파일 경로가 안 터지고 무사히 불러와지도록 잡아주는 것입니다
## AI 활용 내역
pdf에 있는 내역을 직접 ai에게 주며 어떻게 파이선 코드에 적용하는지 전과 무슨 차이가 있고 이게 어떻게 연결되는지를 파악하는
용도로 사용했습니다
