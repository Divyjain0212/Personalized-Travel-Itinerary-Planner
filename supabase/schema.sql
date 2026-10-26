create extension if not exists "pgcrypto";

create table if not exists public.trips (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references auth.users(id) on delete cascade,
  name text not null,
  destination text not null,
  duration_days integer not null check (duration_days between 1 and 30),
  budget text not null,
  saved_at timestamptz not null default now(),
  preferences jsonb not null,
  itinerary jsonb not null
);

alter table public.trips enable row level security;
create policy "Users manage their own trips" on public.trips
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);
