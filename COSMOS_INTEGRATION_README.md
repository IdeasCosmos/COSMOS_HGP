# COSMOS-HGP Complete Integration System

완전한 COSMOS-HGP 시스템을 다른 프로젝트에서 재사용할 수 있도록 정리한 통합 모듈입니다.

## 🚀 주요 기능

- **7계층 계층구조**: Quantum → Atomic → Molecular → Compound → Organic → Ecosystem → Cosmos
- **3가지 운영 모드**: Stability (안정성), Innovation (혁신), Adaptive (적응형)
- **DNA 코돈 기반 인코딩**: 64개 코돈을 통한 규칙 매핑
- **MetaBall 집계 시스템**: 마이크로에서 매크로로의 계층적 그룹핑
- **실시간 WebSocket 스트리밍**: Python 백엔드와 React 프론트엔드 실시간 연결
- **BeadFlow 물리 시뮬레이션**: 구슬들의 물리적 움직임과 충돌
- **React 대시보드**: 완전한 시각화 및 제어 인터페이스

## 📋 필요 조건

### Python 패키지
```bash
pip install flask flask-socketio flask-cors numpy pandas
```

### 시스템 요구사항
- Node.js 16+ 
- npm 또는 yarn
- Python 3.8+

## 🛠 설치 및 사용법

### 1. 기본 사용법

```python
from cosmos_integration_system import CosmosIntegrationSystem

# 시스템 초기화
cosmos = CosmosIntegrationSystem("my-cosmos-project")

# 전체 시스템 실행 (백엔드 + 프론트엔드)
cosmos.run_full_system(backend_port=5000, frontend_port=3000)
```

### 2. 개별 컴포넌트 실행

#### 백엔드만 실행
```python
cosmos = CosmosIntegrationSystem()
cosmos.start_backend(port=5000, debug=True)
```

#### 프론트엔드만 실행
```python
cosmos = CosmosIntegrationSystem()
cosmos.build_frontend("my_frontend")
cosmos.serve_frontend("my_frontend", port=3000)
```

### 3. 명령행에서 실행

```bash
# 전체 시스템 실행
python cosmos_integration_system.py --mode full

# 백엔드만 실행
python cosmos_integration_system.py --mode backend --backend-port 5000

# 프론트엔드만 실행  
python cosmos_integration_system.py --mode frontend --frontend-port 3000

# 디버그 모드
python cosmos_integration_system.py --mode full --debug
```

## 🌐 API 엔드포인트

### REST API

#### 시스템 상태 확인
```http
GET http://localhost:5000/health
```

#### COSMOS 실행
```http
POST http://localhost:5000/api/cosmos/execute
Content-Type: application/json

{
  "group": "standard_pipeline",
  "input": [1, 2, 3, 4, 5],
  "profile": "stability",
  "options": {
    "predict_risk": true,
    "return_annotations": true
  }
}
```

#### 설정 관리
```http
GET http://localhost:5000/api/cosmos/config
POST http://localhost:5000/api/cosmos/config
Content-Type: application/json

{
  "mode": "innovation",
  "threshold": 0.5
}
```

#### 통계 조회
```http
GET http://localhost:5000/api/cosmos/stats
```

### WebSocket 이벤트

#### 클라이언트 연결
```javascript
const socket = io('http://localhost:5000');

socket.on('connect', () => {
  console.log('Connected to COSMOS engine');
});

socket.on('execution_result', (data) => {
  console.log('Execution result:', data);
});

socket.on('config_updated', (data) => {
  console.log('Config updated:', data);
});
```

## 🎨 대시보드 기능

### 시각화 요소
- **7개 레이어 빈**: 각 계층별 처리 구역
- **라우터**: 중앙 의사결정 지점
- **아웃렛**: 최종 출력 지점
- **구슬(비드)**: 개별 규칙 실행을 나타내는 물리적 객체
- **경로**: 구슬의 이동 경로 (정상/차단 구분)

### 상호작용
- **모드 전환**: Stability ↔ Innovation ↔ Adaptive
- **임계값 조정**: 실시간 임계값 변경
- **실행 트리거**: 수동 실행 버튼
- **실시간 통계**: 실행 수, 캐스케이드 수, 평균 임팩트

### 색상 코딩
- 🟡 **황금색**: 정상 실행 (임팩트 < 임계값)
- 🟤 **갈색**: 주의 (임팩트 ≈ 임계값)
- ⚫ **검은색**: 차단됨 (임팩트 ≥ 임계값)
- 🔴 **빨간 점선**: 차단된 경로

## 🔧 커스터마이징

### 1. 새로운 계층 추가
```python
cosmos = CosmosIntegrationSystem()
cosmos.layers[8] = 'Galactic'  # 8번째 계층 추가
```

### 2. 실행 로직 수정
```python
def custom_execution_logic(self, group, input_data, profile, options):
    # 사용자 정의 실행 로직
    return result

cosmos._execute_cosmos_logic = custom_execution_logic
```

### 3. 프론트엔드 테마 변경
```python
# CosmosBeadFlowDashboard.jsx에서 테마 수정
const theme = {
  bg: '#1a1a1a',        # 다크 모드
  text: '#ffffff',
  gold: '#FFD700',
  // ...
};
```

## 📊 데이터 구조

### 실행 결과 형식
```json
{
  "execution_id": "exec_1696348800000",
  "group": "standard_pipeline",
  "profile": "stability",
  "input": [1, 2, 3, 4, 5],
  "metrics": {
    "total_impact": 1.25,
    "average_impact": 0.25,
    "blocked_count": 2,
    "cascade_depth": 1,
    "execution_path": [
      {
        "step": 1,
        "layer": "Quantum",
        "layer_number": 1,
        "impact": 0.1,
        "threshold": 0.33,
        "status": "PASSED",
        "blocked": false,
        "codon": "AAA",
        "rule": "rule_standard_pipeline_quantum",
        "timestamp": "2023-10-03T09:00:00"
      }
    ]
  },
  "mode": "stability",
  "timestamp": "2023-10-03T09:00:00",
  "status": "completed"
}
```

### 비드(구슬) 데이터 형식
```json
{
  "id": "exec_1696348800000_0",
  "impact": 0.25,
  "blocked": false,
  "cat": 0,
  "layer": 1,
  "codon": "AAA",
  "ruleName": "rule_standard_pipeline_quantum",
  "threshold": 0.33,
  "mode": "stability",
  "status": "PASSED",
  "timestamp": 1696348800000
}
```

## 🚀 프로덕션 배포

### 1. 백엔드 배포 (Gunicorn)
```bash
pip install gunicorn eventlet
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 cosmos_integration_system:app
```

### 2. 프론트엔드 빌드
```bash
cd cosmos_frontend
npm run build
```

### 3. Nginx 설정
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # React 정적 파일
    location / {
        root /path/to/cosmos_frontend/dist;
        try_files $uri /index.html;
    }

    # API 프록시
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # WebSocket 프록시
    location /socket.io {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## 🔍 문제 해결

### 1. WebSocket 연결 실패
```bash
# 포트 확인
lsof -i :5000

# 방화벽 확인
sudo ufw status
```

### 2. 프론트엔드 빌드 실패
```bash
# Node.js 버전 확인
node --version

# 의존성 재설치
rm -rf node_modules package-lock.json
npm install
```

### 3. CORS 오류
```python
# Flask-CORS 설정 확인
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

## 📚 확장 예제

### 1. 실제 COSMOS 엔진과 연결
```python
class RealCosmosIntegration(CosmosIntegrationSystem):
    def _execute_cosmos_logic(self, group, input_data, profile, options):
        # 실제 COSMOS 엔진 호출
        from your_cosmos_engine import CosmosEngine
        
        engine = CosmosEngine()
        result = engine.execute(group, input_data, profile, options)
        
        return self._format_result(result)
```

### 2. 데이터베이스 연동
```python
class DatabaseCosmosIntegration(CosmosIntegrationSystem):
    def __init__(self, db_connection):
        super().__init__()
        self.db = db_connection
    
    def _execute_cosmos_logic(self, group, input_data, profile, options):
        # 데이터베이스에서 실행 히스토리 저장
        result = super()._execute_cosmos_logic(group, input_data, profile, options)
        
        self.db.executions.insert_one(result)
        return result
```

### 3. 인증 추가
```python
from flask_jwt_extended import JWTManager, jwt_required

class SecureCosmosIntegration(CosmosIntegrationSystem):
    def _setup_routes(self):
        super()._setup_routes()
        
        JWTManager(self.app)
        
        @self.app.route('/api/cosmos/execute', methods=['POST'])
        @jwt_required()
        def secure_execute_cosmos():
            return super()._execute_cosmos_logic(...)
```

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

## 🤝 기여

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해주세요.

---

**COSMOS-HGP Integration System v2.0.0**  
*Hierarchical Gradient Propagation with Duality Architecture*
