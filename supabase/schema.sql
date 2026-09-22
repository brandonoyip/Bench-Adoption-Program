-- Run once in the Supabase SQL editor. Import verified park inventory before launch.
create table public.benches (
  id integer primary key,
  area text not null,
  lat double precision not null check (lat between -90 and 90),
  lng double precision not null check (lng between -180 and 180)
);
create table public.adoptions (
  id bigint generated always as identity primary key,
  bench_id integer not null references public.benches(id),
  donor text not null check (char_length(donor) between 1 and 100),
  email text not null,
  starts timestamptz not null default now(),
  ends timestamptz not null,
  dedication text check (char_length(dedication) <= 240),
  check (ends > starts)
);
create index adoptions_bench_end on public.adoptions(bench_id, ends desc);
alter table public.benches enable row level security;
alter table public.adoptions enable row level security;
-- Public reads use RLS and column grants; contact email remains private.
revoke all on public.benches, public.adoptions from anon, authenticated;
grant select on public.benches to anon, authenticated;
grant select (bench_id, donor, starts, ends, dedication) on public.adoptions to anon, authenticated;
create policy benches_public_read on public.benches for select to anon, authenticated using (true);
create policy adoptions_public_read on public.adoptions for select to anon, authenticated using (true);
create view public.public_benches with (security_invoker = true, security_barrier = true) as
select b.id, b.area, b.lat, b.lng, a.donor, a.starts, a.ends, a.dedication
from public.benches b left join lateral (
  select donor, starts, ends, dedication from public.adoptions
  where bench_id = b.id and ends > now() order by ends desc limit 1
) a on true;
grant select on public.public_benches to anon, authenticated;
create or replace function public.adopt_bench(p_bench_id integer, p_name text, p_email text, p_months integer, p_dedication text default '')
returns void language plpgsql security definer set search_path = '' as $$
begin
  if p_name is null or char_length(trim(p_name)) not between 1 and 100 then
    raise exception 'Please provide a display name of up to 100 characters.';
  end if;
  if p_email is null or char_length(p_email) > 254 or p_email !~ '^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$' then
    raise exception 'Please provide a valid email address.';
  end if;
  if p_months is null or p_months not in (6,12,24,60) then raise exception 'Invalid adoption duration.'; end if;
  if char_length(p_dedication) > 240 then raise exception 'Dedication must be 240 characters or fewer.'; end if;
  -- Serialize competing requests for the same bench within this transaction.
  perform id from public.benches where id = p_bench_id for update;
  if not found then raise exception 'This bench could not be found.'; end if;
  if exists(select 1 from public.adoptions where bench_id = p_bench_id and ends > now()) then
    raise exception 'This bench has just been adopted. Please choose another bench.';
  end if;
  insert into public.adoptions(bench_id, donor, email, starts, ends, dedication)
  values(p_bench_id, trim(p_name), trim(p_email), now(), now() + pg_catalog.make_interval(months => p_months), trim(p_dedication));
end;
$$;
revoke all on function public.adopt_bench(integer,text,text,integer,text) from public;
grant execute on function public.adopt_bench(integer,text,text,integer,text) to anon, authenticated;
