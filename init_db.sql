create table groups
(
	id serial not null
		constraint groups_pkey
			primary key,
	name varchar(255),
	description integer
);


create table families
(
	id serial not null
		constraint families_pkey
			primary key,
	name varchar(255),
	"group" integer not null
		constraint families_group_fkey
			references groups,
	creation timestamp default now() not null
);



create unique index families_id_uindex
	on families (id);

create unique index groups_id_uindex
	on groups (id);

create table names_cases
(
	name varchar(255) not null
        constraint names_cases_pkey
			primary key,
	genitive varchar(255) not null
);

alter table names_cases
    owner to jolod;

create unique index names_cases_name_uindex
    on names_cases (name);

create table role
(
	id serial not null
		constraint role_pkey
			primary key,
	name varchar(80),
	description varchar(255)
);



create unique index role_id_uindex
	on role (id);

create unique index role_name_uindex
	on role (name);

create table "user"
(
	id serial not null
		constraint user_id_pk
			primary key,
	email varchar(255) not null,
	password varchar(255) not null,
	confirmed_at timestamp,
	active boolean,
	username varchar(255) not null,
	last_login_at timestamp,
	current_login_at timestamp,
	last_login_ip varchar(255),
	current_login_ip varchar(255),
	login_count integer,
	last_activity_at timestamp,
	last_activity_ip varchar(255),
	language varchar(5) default 'en'::character varying not null,
	first_seen timestamp default now() not null,
	birthday timestamp
);



create table roles_users
(
	id integer not null
		constraint roles_users_id_fkey
			references "user",
	role_id integer not null
		constraint roles_users_role_id_fkey
			references role
);

alter table roles_users owner to jolod;

create table shuffles
(
	giver integer not null
		constraint shuffles_giver_fkey
			references "user",
	getter integer not null
		constraint shuffles_getter_fkey
			references "user",
	"group" integer not null
		constraint shuffles_groups_id_fk
			references groups,
	year integer not null,
	id serial not null
		constraint shuffles_pk
			primary key
);



create index shuffles_group_index
	on shuffles ("group");

create index shuffles_year_index
	on shuffles (year);

create unique index shuffles_giver_getter_group_year_uindex
	on shuffles (giver, getter, "group", year);

create unique index shuffles_id_uindex
	on shuffles (id);

create unique index shuffles_giver_year_uindex
	on shuffles (giver, year);

create unique index user_email_uindex
	on "user" (email);

create unique index user_id_uindex
	on "user" (id);

create index user_username_index
	on "user" (username);

create table users_families_admins
(
	user_id integer not null
		constraint users_families_admins_pkey
			primary key
		constraint users_families_admins_user_id_fkey
			references "user",
	family_id integer not null
		constraint users_families_admins_family_id_fkey
			references families,
	admin boolean not null,
	confirmed boolean default false not null
);

comment on table users_families_admins is 'Contains all user-family relationships and if the user is the admin of that family';

alter table users_families_admins owner to jolod;

create table users_groups_admins
(
	user_id integer not null
		constraint users_groups_admins_user_id_pk
			primary key
		constraint users_groups_admins_user_id_fkey
			references "user",
	group_id integer not null
		constraint users_groups_admins_group_id_fkey
			references groups,
	admin boolean not null,
	confirmed boolean default false not null
);

alter table users_groups_admins owner to jolod;

create table wishlists
(
	user_id integer not null
		constraint wishlists_user_id_fkey
			references "user",
	item varchar(1024) not null,
	status integer not null,
	purchased_by integer
		constraint wishlists_purchased_by_fkey
			references "user",
	id bigserial not null
		constraint wishlists_note_id_pk
			primary key,
	received timestamp
);



create unique index wishlists_note_id_uindex
	on wishlists (id);

create table families_groups
(
	family_id integer not null
		constraint families_groups_admins_pk
			primary key
		constraint families_groups_admins_families_id_fk
			references families,
	group_id integer not null
		constraint families_groups_admins_groups_id_fk
			references groups,
	confirmed boolean default false not null
);

alter table families_groups owner to jolod;

create index families_groups_admins_family_id_index
	on families_groups (family_id);

create index families_groups_admins_group_id_index
	on families_groups (group_id);

create table user_connection
(
	id serial not null
		constraint user_connection_pk
			primary key,
	user_id integer not null
		constraint user_connection_user_id_fk
			references "user",
	provider_user_id varchar(255),
	created_at timestamp default now(),
	token varchar(255),
	provider varchar(255)
);

alter table user_connection owner to jolod;

create unique index user_connection_id_uindex
	on user_connection (id);

create table reminders
(
	"group" integer not null
		constraint reminders_pk
			primary key
		constraint reminders_groups_id_fk
			references groups,
	last_check timestamp default now() not null,
	type varchar(4)
);



create index reminders_group_index
	on reminders ("group");

create table subscription_types
(
	id serial not null
		constraint subscription_types_pk
			primary key,
	name varchar(255)
);

alter table subscription_types owner to jolod;

create table subscriptions
(
	user_id integer not null
		constraint subscriptions_pk
			primary key
		constraint subscriptions_user_id_fk
			references "user",
	type integer not null
		constraint subscriptions_subscription_types_id_fk
			references subscription_types,
	until timestamp not null
);


create unique index subscriptions_user_id_type_uindex
	on subscriptions (user_id, type);

create unique index subscription_types_id_uindex
	on subscription_types (id);

