-- MULTI-TELECOM AI: new tables (reuses providers, recharge_plans, telecom_faqs, troubleshooting)
create extension if not exists vector;

create table users (
  user_id            bigint generated always as identity primary key,
  full_name          text not null,
  email              text not null unique,
  mobile_number      text not null unique check (mobile_number ~ '^[6-9][0-9]{9}$'),
  password_hash      text not null,
  role               text not null default 'user' check (role in ('user','admin')),
  preferred_provider_id bigint references providers(provider_id),
  is_active          boolean not null default true,
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now()
);

create table subscriptions (
  subscription_id    bigint generated always as identity primary key,
  user_id            bigint not null references users(user_id) on delete cascade,
  provider_id        bigint not null references providers(provider_id),
  plan_id            bigint not null references recharge_plans(plan_id),
  mobile_number      text not null,
  start_date         date not null,
  end_date           date not null,
  data_limit_mb      numeric(12,2),
  is_active          boolean not null default true,
  created_at         timestamptz not null default now(),
  check (end_date >= start_date)
);

create table usage_records (
  usage_id           bigint generated always as identity primary key,
  user_id            bigint not null references users(user_id) on delete cascade,
  usage_date         date not null,
  data_used_mb       numeric(12,2) not null default 0 check (data_used_mb >= 0),
  call_minutes       integer not null default 0 check (call_minutes >= 0),
  sms_count          integer not null default 0 check (sms_count >= 0),
  is_synthetic       boolean not null default true,
  unique (user_id, usage_date)
);

create table recharges (
  recharge_id        bigint generated always as identity primary key,
  user_id            bigint not null references users(user_id) on delete cascade,
  provider_id        bigint not null references providers(provider_id),
  plan_id            bigint not null references recharge_plans(plan_id),
  mobile_number      text not null,
  amount             numeric(10,2) not null check (amount > 0),
  payment_method     text not null default 'SIMULATED',
  status             text not null default 'SUCCESS' check (status in ('SUCCESS','FAILED','PENDING')),
  transaction_id     text not null unique,
  created_at         timestamptz not null default now()
);

create table complaints (
  complaint_id       bigint generated always as identity primary key,
  user_id            bigint not null references users(user_id) on delete cascade,
  category           text not null,
  description        text not null,
  priority           text not null default 'MEDIUM' check (priority in ('LOW','MEDIUM','HIGH')),
  status             text not null default 'OPEN'
                     check (status in ('OPEN','ASSIGNED','IN_PROGRESS','RESOLVED','CLOSED')),
  category_confidence numeric(5,4),
  assigned_to        bigint references users(user_id),
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now(),
  resolved_at        timestamptz
);

create table chat_history (
  message_id         bigint generated always as identity primary key,
  user_id            bigint not null references users(user_id) on delete cascade,
  session_id         uuid not null,
  role               text not null check (role in ('user','assistant')),
  message            text not null,
  intent             text,
  confidence         numeric(5,4),
  tool_used          text,
  sources            jsonb,
  created_at         timestamptz not null default now()
);

create table documents (
  document_id        bigint generated always as identity primary key,
  source_table       text not null,          -- 'telecom_faqs' or 'troubleshooting'
  source_id          bigint not null,
  provider_id        bigint references providers(provider_id),
  title              text not null,
  content            text not null,
  embedding          vector(384),            -- all-MiniLM-L6-v2 / multilingual MiniLM
  created_at         timestamptz not null default now(),
  unique (source_table, source_id)
);

-- Indexes
create index idx_subscriptions_user   on subscriptions(user_id, is_active);
create index idx_usage_user_date      on usage_records(user_id, usage_date desc);
create index idx_recharges_user       on recharges(user_id, created_at desc);
create index idx_complaints_user      on complaints(user_id);
create index idx_complaints_status    on complaints(status, priority);
create index idx_chat_user_session    on chat_history(user_id, session_id, created_at);
create index idx_documents_embedding  on documents using hnsw (embedding vector_cosine_ops);

-- Security: block direct access with the publishable key.
-- The FastAPI backend connects as the postgres role, which bypasses RLS.
alter table users          enable row level security;
alter table subscriptions  enable row level security;
alter table usage_records  enable row level security;
alter table recharges      enable row level security;
alter table complaints     enable row level security;
alter table chat_history   enable row level security;
alter table documents      enable row level security;