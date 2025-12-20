-- ============================================
-- 물품신청받기 앱 RLS 활성화 스크립트
-- ============================================

-- Step 1: RLS 활성화
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE pending_cart ENABLE ROW LEVEL SECURITY;
ALTER TABLE submitted_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE submission_summary ENABLE ROW LEVEL SECURITY;

-- Step 2: 서비스 역할만 접근 가능하도록 정책 설정
CREATE POLICY "service_role_policy" ON users
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_policy" ON pending_cart
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_policy" ON submitted_items
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "service_role_policy" ON submission_summary
    FOR ALL USING (auth.role() = 'service_role');

-- ✅ 완료!
