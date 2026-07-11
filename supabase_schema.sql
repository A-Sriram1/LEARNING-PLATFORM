-- ============================================================
-- SkillForge AI — Supabase Database Schema
-- Run this in: Supabase Dashboard → SQL Editor → New Query
-- ============================================================

-- Enable UUID extension (already on by default in Supabase)
create extension if not exists "uuid-ossp";


-- ── USERS ────────────────────────────────────────────────────────────────
-- Mirrors auth.users (id is the Supabase Auth UUID)
create table public.users (
  id              uuid primary key references auth.users(id) on delete cascade,
  email           text unique not null,
  display_name    text not null,
  avatar_url      text,
  role            text not null default 'student',  -- 'student' | 'admin'
  xp              int  not null default 0,
  coins           int  not null default 0,
  level           int  not null default 1,
  streak_days     int  not null default 0,
  last_active_date date,
  created_at      timestamptz not null default now()
);

-- Auto-create a user row when someone signs up via Supabase Auth
create or replace function public.handle_new_user()
returns trigger language plpgsql security definer as $$
begin
  insert into public.users (id, email, display_name)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data->>'full_name', split_part(new.email,'@',1))
  );
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();


-- ── TOPICS ───────────────────────────────────────────────────────────────
create table public.topics (
  id         uuid primary key default uuid_generate_v4(),
  user_id    uuid not null references public.users(id) on delete cascade,
  title      text not null,
  slug       text not null,
  status     text not null default 'generating',  -- 'generating'|'ready'|'failed'
  created_at timestamptz not null default now()
);
create index idx_topics_user on public.topics(user_id);


-- ── TOPIC CONTENT ─────────────────────────────────────────────────────────
create table public.topic_contents (
  id           uuid primary key default uuid_generate_v4(),
  topic_id     uuid not null references public.topics(id) on delete cascade,
  section      text not null,   -- 'roadmap'|'theory'|'cheat_sheet'|'syntax'|'summary'
  content      jsonb not null,
  generated_at timestamptz not null default now()
);
create index idx_tc_topic on public.topic_contents(topic_id);


-- ── MCQs ─────────────────────────────────────────────────────────────────
create table public.mcqs (
  id            uuid primary key default uuid_generate_v4(),
  topic_id      uuid not null references public.topics(id) on delete cascade,
  difficulty    text not null default 'medium',   -- 'easy'|'medium'|'hard'
  question      text not null,
  options       jsonb not null,        -- ["A","B","C","D"]
  correct_index int  not null,
  explanation   text not null,
  why_wrong     jsonb,                 -- {"0":"reason","1":"reason",...}
  related_topic text,
  created_at    timestamptz not null default now()
);
create index idx_mcqs_topic on public.mcqs(topic_id);


-- ── MCQ ATTEMPTS ─────────────────────────────────────────────────────────
create table public.mcq_attempts (
  id             uuid primary key default uuid_generate_v4(),
  user_id        uuid not null references public.users(id) on delete cascade,
  mcq_id         uuid not null references public.mcqs(id) on delete cascade,
  selected_index int  not null,
  is_correct     bool not null,
  created_at     timestamptz not null default now()
);
create index idx_ma_user on public.mcq_attempts(user_id);


-- ── CODING PROBLEMS ──────────────────────────────────────────────────────
create table public.coding_problems (
  id                uuid primary key default uuid_generate_v4(),
  topic_id          uuid not null references public.topics(id) on delete cascade,
  title             text not null,
  difficulty        text not null default 'medium',
  prompt            text not null,
  starter_code      jsonb not null,   -- {"python":"...","java":"...","javascript":"..."}
  visible_test_cases jsonb not null,  -- [{"input":"...","output":"..."}]
  hidden_test_cases  jsonb not null,
  created_at        timestamptz not null default now()
);


-- ── SUBMISSIONS ───────────────────────────────────────────────────────────
create table public.submissions (
  id           uuid primary key default uuid_generate_v4(),
  user_id      uuid not null references public.users(id) on delete cascade,
  problem_id   uuid not null references public.coding_problems(id) on delete cascade,
  language     text not null,
  source_code  text not null,
  status       text not null default 'pending',  -- 'pending'|'accepted'|'wrong_answer'|'error'|'timeout'
  passed_cases int  not null default 0,
  total_cases  int  not null default 0,
  exec_time_ms float,
  memory_kb    float,
  ai_review    jsonb,   -- {time_complexity, space_complexity, suggestions[], style_notes[]}
  created_at   timestamptz not null default now()
);
create index idx_sub_user on public.submissions(user_id);


-- ── INTERVIEW SESSIONS ────────────────────────────────────────────────────
create table public.interview_sessions (
  id         uuid primary key default uuid_generate_v4(),
  user_id    uuid not null references public.users(id) on delete cascade,
  track      text not null,   -- 'frontend'|'backend'|'system_design'|'hr'|custom
  transcript jsonb not null default '[]',
  status     text not null default 'active',   -- 'active'|'completed'
  created_at timestamptz not null default now()
);


-- ── INTERVIEW REPORTS ────────────────────────────────────────────────────
create table public.interview_reports (
  id                  uuid primary key default uuid_generate_v4(),
  session_id          uuid not null references public.interview_sessions(id) on delete cascade,
  technical_score     float not null default 0,
  confidence_score    float not null default 0,
  grammar_score       float not null default 0,
  pronunciation_score float not null default 0,
  communication_score float not null default 0,
  suggestions         jsonb,   -- ["tip1","tip2",...]
  created_at          timestamptz not null default now()
);


-- ── GAMIFICATION ─────────────────────────────────────────────────────────
create table public.xp_events (
  id         uuid primary key default uuid_generate_v4(),
  user_id    uuid not null references public.users(id) on delete cascade,
  event_type text not null,   -- 'mcq_correct'|'submission_accepted'|'interview_done'|'streak'
  xp_gained  int  not null,
  created_at timestamptz not null default now()
);

create table public.badges (
  id          uuid primary key default uuid_generate_v4(),
  user_id     uuid not null references public.users(id) on delete cascade,
  badge_key   text not null,   -- 'first_topic'|'streak_7'|'ace_mcqs'|...
  awarded_at  timestamptz not null default now()
);


-- ── CHAT MESSAGES ─────────────────────────────────────────────────────────
create table public.chat_messages (
  id         uuid primary key default uuid_generate_v4(),
  user_id    uuid not null references public.users(id) on delete cascade,
  topic_id   uuid references public.topics(id) on delete set null,
  role       text not null,   -- 'user'|'assistant'
  content    text not null,
  created_at timestamptz not null default now()
);
create index idx_chat_user on public.chat_messages(user_id);


-- ── ROW LEVEL SECURITY ───────────────────────────────────────────────────
-- Enable RLS on all user-data tables
alter table public.users            enable row level security;
alter table public.topics           enable row level security;
alter table public.topic_contents   enable row level security;
alter table public.mcq_attempts     enable row level security;
alter table public.submissions      enable row level security;
alter table public.interview_sessions enable row level security;
alter table public.interview_reports  enable row level security;
alter table public.xp_events        enable row level security;
alter table public.badges           enable row level security;
alter table public.chat_messages    enable row level security;

-- Users can only read/write their own rows
create policy "users: own row" on public.users
  for all using (auth.uid() = id);

create policy "topics: own rows" on public.topics
  for all using (auth.uid() = user_id);

create policy "topic_contents: via topic" on public.topic_contents
  for all using (
    exists (select 1 from public.topics t where t.id = topic_id and t.user_id = auth.uid())
  );

create policy "mcq_attempts: own rows" on public.mcq_attempts
  for all using (auth.uid() = user_id);

create policy "submissions: own rows" on public.submissions
  for all using (auth.uid() = user_id);

create policy "interview_sessions: own rows" on public.interview_sessions
  for all using (auth.uid() = user_id);

create policy "interview_reports: via session" on public.interview_reports
  for all using (
    exists (select 1 from public.interview_sessions s where s.id = session_id and s.user_id = auth.uid())
  );

create policy "xp_events: own rows" on public.xp_events
  for all using (auth.uid() = user_id);

create policy "badges: own rows" on public.badges
  for all using (auth.uid() = user_id);

create policy "chat_messages: own rows" on public.chat_messages
  for all using (auth.uid() = user_id);

-- MCQs are readable by everyone (they're curriculum, not user data)
alter table public.mcqs enable row level security;
create policy "mcqs: read all" on public.mcqs for select using (true);
create policy "mcqs: insert by service" on public.mcqs for insert with check (auth.role() = 'service_role');
