-- 在 Supabase SQL Editor 中执行以下 SQL，创建成交记录表

CREATE TABLE IF NOT EXISTS transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  property_id TEXT NOT NULL,
  building TEXT DEFAULT '',
  area NUMERIC,
  decoration TEXT DEFAULT '',
  maintainer TEXT DEFAULT '',
  listing_price NUMERIC,
  listing_price_raw TEXT,
  transaction_price NUMERIC,
  transaction_price_raw TEXT,
  company TEXT DEFAULT '',
  date TEXT DEFAULT '',
  price_history JSONB DEFAULT '[]'::jsonb,
  update_count INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 房源编号唯一索引（去重依据）
CREATE UNIQUE INDEX IF NOT EXISTS idx_property_id ON transactions (property_id);

-- 允许公开读写（个人工具，无需认证）
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "允许所有操作" ON transactions FOR ALL USING (true) WITH CHECK (true);
