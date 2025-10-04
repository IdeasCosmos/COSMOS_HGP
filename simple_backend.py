#!/usr/bin/env python3
"""
Simple COSMOS Backend Server
간단한 HTTP 서버로 Flask 없이 작동
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import time
from urllib.parse import parse_qs, urlparse

class CosmosHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """GET 요청 처리"""
        parsed_path = urlparse(self.path)

        # CORS 헤더 설정
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        if parsed_path.path == '/health':
            # Health check
            response = {
                'status': 'ok',
                'service': 'COSMOS-HGP Backend',
                'timestamp': time.time()
            }
        elif parsed_path.path == '/api/demo':
            # 데모 데이터 생성
            response = {
                'beads': self.generate_demo_beads(20)
            }
        else:
            response = {'error': 'Not found'}

        self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        """POST 요청 처리"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            data = json.loads(post_data.decode())

            if self.path == '/api/execute':
                # 실행 요청 처리
                response = {
                    'status': 'success',
                    'execution_result': {
                        'execution_path': self.generate_demo_beads(10),
                        'metrics': {
                            'total': 10,
                            'blocked': 2,
                            'avg_impact': 0.45
                        }
                    }
                }
            else:
                response = {'status': 'ok', 'received': data}
        except Exception as e:
            response = {'error': str(e)}

        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        """OPTIONS 요청 처리 (CORS preflight)"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def generate_demo_beads(self, count):
        """데모 구슬 데이터 생성"""
        beads = []
        bases = ['A', 'C', 'G', 'T']

        for i in range(count):
            codon = ''.join([bases[i % 4], bases[(i >> 2) % 4], bases[(i >> 4) % 4]])
            bead = {
                'id': f'bead_{int(time.time())}_{i}',
                'impact': round(0.1 + random.random() * 0.6, 3),
                'blocked': random.random() < 0.15,
                'cat': i % 7,
                'layer': (i % 7) + 1,
                'codon': codon,
                'timestamp': time.time()
            }
            beads.append(bead)

        return beads

    def log_message(self, format, *args):
        """로그 메시지 (조용하게)"""
        print(f"{self.address_string()} - {format % args}")


def run_server(port=5001):
    """서버 실행"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, CosmosHandler)
    print(f"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  🌌 COSMOS-HGP Simple Backend Server                         ║
    ║  ✅ Running on http://localhost:{port}                        ║
    ║                                                               ║
    ║  Endpoints:                                                   ║
    ║    GET  /health        - Health check                        ║
    ║    GET  /api/demo      - Demo data                           ║
    ║    POST /api/execute   - Execute COSMOS                      ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()


if __name__ == '__main__':
    run_server(5001)
