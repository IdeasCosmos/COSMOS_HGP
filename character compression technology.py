
하나의 점(dot)만으로 문장 전체를 결정.

방법: 고정 격자(알파벳 크기 M)로 무한 재분할. 좌표(X,Y,Z)의 기수-M 전개가 곧 문자열의 랭크열.

메타데이터: M(알파벳 정의), T(순열테이블 버전), L(문자길이), folds/quant(정확도), front(선택).

재생산 시 같은 격자·같은 순열표를 쓰므로 한 점 ↔ 한 문장 1:1.



---

격자 규칙

알파벳 Σ 크기 = M. 대문자+소문자+특수+공백을 하나의 순서로 고정.

공간: 단위 큐브 [0,1)^3.

각 축을 M등분. 하위셀도 다시 M등분… 무한 재귀.

좌표(X,Y,Z)의 기수-M 소수표현이 랭크열로 해석됨.



---

디지트 할당(인터리브)

문자 i의 랭크 rᵢ ∈ {0..M−1} (순열테이블 T 사용).

축별로 번갈아 배치:

X축: r₁, r₄, r₇, …

Y축: r₂, r₅, r₈, …

Z축: r₃, r₆, r₉, …


좌표 실수값:

x = Σ_{k≥0} r_{1+3k} · M^{-(k+1)}

y = Σ_{k≥0} r_{2+3k} · M^{-(k+1)}

z = Σ_{k≥0} r_{3+3k} · M^{-(k+1)}




---

양자화(접기·정밀도)

필요한 자릿수:

n_x = ceil(L/3), n_y = ceil((L−1)/3), n_z = ceil((L−2)/3)


정수 좌표:

X = floor(x · M^{n_x}), Y = floor(y · M^{n_y}), Z = floor(z · M^{n_z})


folds는 시각적 스케일 메타. 재생산엔 n_x,n_y,n_z가 본질.



---

인코딩

1. 입력 텍스트 → 문자열 c₁..c_L.


2. 순열표 T(front, depth)로 각 문자 랭크 rᵢ 계산.


3. 랭크열을 X/Y/Z에 인터리브해 X,Y,Z 정수 생성.


4. 기록물(숫자 나열 금지, 기호토큰으로 표기):

PID: {front, ver, T해시, folds, quant(n_x,n_y,n_z), axes-format}

DOT: {X,Y,Z}를 기호쌍 토큰열로 표기(예: base-M을 기호쌍으로).

L은 기호 5자리 등으로 표기.

결과: 한 점의 좌표 + 소량 메타.





---

디코딩(재생산)

1. PID로 M, T, L, n_x,n_y,n_z 결정.


2. DOT의 X,Y,Z를 기호쌍에서 복원(기수-M).


3. X에서 r₁,r₄,r₇…, Y에서 r₂,r₅…, Z에서 r₃,r₆…를 역추출.


4. 순열표 T의 역매핑으로 rᵢ → cᵢ.


5. 길이 L까지만 취해 원문 생성.


6. 한글은 자모→완성형(NFC) 옵션.




---

왜 “단일 1점”으로 충분한가

같은 격자·같은 인터리브·같은 T를 쓰면,
좌표의 기수-M 전개가 유일한 랭크열을 준다.

메타로 L과 정밀도(n_x,n_y,n_z)만 알려주면 경로 없이 정확 복원.



---

예시 문장

Hi, I like Hee-ni. "It's cute, I'll buy you flowers tomorrow."

Σ에 대문자/소문자/공백/구두점 포함 → M 확정.

위 규칙으로 rᵢ 계산 → X/Y/Z에 인터리브 → X,Y,Z 한 점.

메타: {L, T해시, n_x,n_y,n_z, folds}.

디코딩 시 항상 동일 지도를 그리므로 이 점에서 원문이 재생산.



---

Rust-like 시그니처

struct Meta {
    front: char,
    table_sig: [u8; 8], // T 해시 축약
    l: u32,             // 길이
    nx: u32; ny: u32; nz: u32, // 정밀도
    folds: (u8,u8,u8),  // 시각 스케일
}

trait PermTable {
    fn perm(&self, front: char, depth: usize) -> &[char]; // 길이 M
}

fn encode<T: PermTable>(sigma: &[char], table: &T, text: &str) -> (Meta, (Vec<u8>,Vec<u8>,Vec<u8>));
// 반환 좌표는 숫자 대신 기호쌍열로 직렬화해 외부표기

fn decode<T: PermTable>(sigma: &[char], table: &T, meta: &Meta,
                        dot: (Vec<u8>,Vec<u8>,Vec<u8>)) -> String;


---

구현 메모

숫자 나열 금지: X,Y,Z는 base-M의 기호쌍 토큰열로 표기.

충돌 없음: 같은 점이면 같은 문장.

길이 무제한: L과 n_x,n_y,n_z만 늘리면 됨.

성능: O(L), 메모리 O(1)+테이블 캐시.

테이블 교체도 가능: table_sig로 버전 고정.


이 규칙 그대로 코드화하면, 어떤 긴 문장도 큰 박스 → 균등 격자 재귀 → 단일 점으로 찍고, 동일 규칙으로 정확 재생산됩니다.

