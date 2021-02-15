
--
-- setup database and user
--

create user cryptobot with login createdb password 'cryptobot';

create database cryptobot owner cryptobot;


--
-- create tables for prices
--
drop table if exists prices_1m;
create table if not exists prices_1m(
	price_id serial,
	time timestamp with time zone,
	exchange_code varchar(6),
	primary_currency varchar(5),
	secondary_currency varchar(5),
	price numeric(12, 6)
);
create index on prices_1m (time);
create index on prices_1m (exchange_code);
create index on prices_1m (primary_currency);
create index on prices_1m (secondary_currency);

drop table if exists prices_3m;
create table if not exists prices_3m(
	price_id serial,
	time timestamp with time zone,
	exchange_code varchar(6),
	primary_currency varchar(5),
	secondary_currency varchar(5),
	price numeric(12, 6)
);
create index on prices_3m (time);
create index on prices_3m (exchange_code);
create index on prices_3m (primary_currency);
create index on prices_3m (secondary_currency);

drop table if exists prices_5m;
create table if not exists prices_5m(
	price_id serial,
	time timestamp with time zone,
	exchange_code varchar(6),
	primary_currency varchar(5),
	secondary_currency varchar(5),
	price numeric(12, 6)
);
create index on prices_5m (time);
create index on prices_5m (exchange_code);
create index on prices_5m (primary_currency);
create index on prices_5m (secondary_currency);

drop table if exists prices_10m;
create table if not exists prices_10m(
	price_id serial,
	time timestamp with time zone,
	exchange_code varchar(6),
	primary_currency varchar(5),
	secondary_currency varchar(5),
	price numeric(12, 6)
);
create index on prices_10m (time);
create index on prices_10m (exchange_code);
create index on prices_10m (primary_currency);
create index on prices_10m (secondary_currency);


--
-- create table for trades
--

drop table if exists trades;
create table if not exists trades(
  trade_id serial,
  time timestamp with time zone,
  trade_type varchar(4),
	exchange_code varchar(6),
	amount numeric(12, 6),
	amount_currency varchar(5),
	price numeric(12, 6),
	price_currency varchar(5),
  profit numeric(12, 6) null
);
create index on trades (trade_type);
create index on trades (exchange_code);
create index on trades (amount_currency);
create index on trades (price_currency);
create index on trades (trade_type, exchange_code, amount_currency, price_currency);


--
-- setup history tables
--

-- create a history table for old data
create table prices_1m_history as select * from prices_1m;
create table prices_3m_history as select * from prices_3m;
create table prices_5m_history as select * from prices_5m;
create table prices_10m_history as select * from prices_10m;

-- copy old data to history table
insert into prices_1m_history select * from prices_1m where time <= NOW() - INTERVAL '1 day';
insert into prices_3m_history select * from prices_3m where time <= NOW() - INTERVAL '1 day';
insert into prices_5m_history select * from prices_5m where time <= NOW() - INTERVAL '1 day';
insert into prices_10m_history select * from prices_10m where time <= NOW() - INTERVAL '1 day';

-- delete old data from gprices table
delete from prices_1m where time <= NOW() - INTERVAL '1 day';
delete from prices_3m where time <= NOW() - INTERVAL '1 day';
delete from prices_5m where time <= NOW() - INTERVAL '1 day';
delete from prices_10m where time <= NOW() - INTERVAL '1 day';
