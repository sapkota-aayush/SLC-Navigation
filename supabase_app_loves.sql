-- Run this in Supabase SQL Editor (Dashboard → SQL Editor) to create the table for "Show some love" likes.
-- Table: app_loves (one row per tap; id and created_at are auto-filled)

create table if not exists public.app_loves (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now()
);

-- Optional: allow anonymous inserts from your backend (if using anon key).
-- If your backend uses the service_role key, RLS is bypassed and you can skip the policy.
alter table public.app_loves enable row level security;

create policy "Allow insert for everyone"
  on public.app_loves
  for insert
  with check (true);

-- Optional: prevent reads from anon (only backend with service_role can read counts).
create policy "No public read"
  on public.app_loves
  for select
  using (false);
